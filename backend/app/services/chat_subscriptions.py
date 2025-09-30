"""
Chat subscriptions service with business logic
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from typing import List, Optional
from datetime import datetime, timedelta

from app.models.chat_subscriptions import ChatSubscription
from app.models.chats import Chat
from app.schemas.chat_subscriptions import ChatSubscriptionCreate, ChatSubscriptionUpdate, ChatSubscriptionResponse, ChatSubscriptionWithChatInfo


class ChatSubscriptionsService:
    """Service class for chat subscriptions operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_active_subscription_for_chat(self, chat_id: int) -> Optional[ChatSubscription]:
        """Get active subscription for a specific chat"""
        current_time = datetime.now()
        result = await self.db.execute(
            select(ChatSubscription)
            .where(and_(
                ChatSubscription.chat_id == chat_id,
                ChatSubscription.is_active == True,
                ChatSubscription.start_date <= current_time,
                ChatSubscription.end_date > current_time
            ))
            .order_by(ChatSubscription.end_date.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def has_active_subscription(self, chat_id: int) -> bool:
        """Check if chat has active subscription"""
        subscription = await self.get_active_subscription_for_chat(chat_id)
        return subscription is not None

    async def create_subscription(self, subscription_data: ChatSubscriptionCreate) -> ChatSubscription:
        """Create a new chat subscription"""
        db_subscription = ChatSubscription(**subscription_data.model_dump())
        self.db.add(db_subscription)
        await self.db.commit()
        await self.db.refresh(db_subscription)
        return db_subscription

    async def create_subscription_from_payment(
        self,
        chat_id: int,
        subscription_type: str,
        price_stars: int,
        telegram_payment_charge_id: str
    ) -> ChatSubscription:
        """Create subscription from successful payment"""
        current_time = datetime.now()

        # Calculate end date based on subscription type
        if subscription_type == 'month':
            end_date = current_time + timedelta(days=30)
        elif subscription_type == 'year':
            end_date = current_time + timedelta(days=365)
        else:
            raise ValueError(f"Invalid subscription type: {subscription_type}")

        subscription_data = ChatSubscriptionCreate(
            chat_id=chat_id,
            subscription_type=subscription_type,
            price_stars=price_stars,
            start_date=current_time,
            end_date=end_date,
            telegram_payment_charge_id=telegram_payment_charge_id
        )

        return await self.create_subscription(subscription_data)

    async def get_subscription_by_id(self, subscription_id: int) -> Optional[ChatSubscription]:
        """Get subscription by ID"""
        result = await self.db.execute(select(ChatSubscription).where(ChatSubscription.id == subscription_id))
        return result.scalar_one_or_none()

    async def get_subscriptions_for_chat(self, chat_id: int, include_expired: bool = False) -> List[ChatSubscription]:
        """Get all subscriptions for a chat"""
        query = select(ChatSubscription).where(ChatSubscription.chat_id == chat_id)

        if not include_expired:
            current_time = datetime.now()
            query = query.where(and_(
                ChatSubscription.start_date <= current_time,
                ChatSubscription.end_date > current_time
            ))

        query = query.order_by(ChatSubscription.created_at.desc())
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_all_subscriptions_with_chat_info(
        self,
        include_expired: bool = False,
        skip: int = 0,
        limit: int = 100
    ) -> List[ChatSubscriptionWithChatInfo]:
        """Get all subscriptions with chat information"""
        current_time = datetime.now()

        query = select(
            ChatSubscription,
            Chat.title.label('chat_title'),
            Chat.telegram_chat_id.label('chat_telegram_id'),
            Chat.username.label('chat_username')
        ).join(Chat, ChatSubscription.chat_id == Chat.id)

        if not include_expired:
            query = query.where(and_(
                ChatSubscription.is_active == True,
                ChatSubscription.start_date <= current_time,
                ChatSubscription.end_date > current_time
            ))

        query = query.order_by(ChatSubscription.created_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        rows = result.all()

        subscriptions = []
        for row in rows:
            subscription_data = ChatSubscriptionResponse.model_validate(row[0])
            subscription_dict = subscription_data.model_dump()
            subscription_dict.update({
                'chat_title': row.chat_title,
                'chat_telegram_id': row.chat_telegram_id,
                'chat_username': row.chat_username
            })
            subscriptions.append(ChatSubscriptionWithChatInfo(**subscription_dict))

        return subscriptions

    async def update_subscription(self, subscription_id: int, subscription_data: ChatSubscriptionUpdate) -> Optional[ChatSubscription]:
        """Update subscription"""
        db_subscription = await self.get_subscription_by_id(subscription_id)
        if not db_subscription:
            return None

        for field, value in subscription_data.model_dump(exclude_unset=True).items():
            setattr(db_subscription, field, value)

        await self.db.commit()
        await self.db.refresh(db_subscription)
        return db_subscription

    async def deactivate_subscription(self, subscription_id: int) -> bool:
        """Deactivate subscription"""
        db_subscription = await self.get_subscription_by_id(subscription_id)
        if not db_subscription:
            return False

        db_subscription.is_active = False
        await self.db.commit()
        return True

    async def get_expiring_subscriptions(self, days_ahead: int = 7) -> List[ChatSubscriptionWithChatInfo]:
        """Get subscriptions expiring within specified days"""
        current_time = datetime.now()
        expiry_time = current_time + timedelta(days=days_ahead)

        query = select(
            ChatSubscription,
            Chat.title.label('chat_title'),
            Chat.telegram_chat_id.label('chat_telegram_id'),
            Chat.username.label('chat_username')
        ).join(Chat, ChatSubscription.chat_id == Chat.id).where(and_(
            ChatSubscription.is_active == True,
            ChatSubscription.end_date > current_time,
            ChatSubscription.end_date <= expiry_time
        )).order_by(ChatSubscription.end_date)

        result = await self.db.execute(query)
        rows = result.all()

        subscriptions = []
        for row in rows:
            subscription_data = ChatSubscriptionResponse.model_validate(row[0])
            subscription_dict = subscription_data.model_dump()
            subscription_dict.update({
                'chat_title': row.chat_title,
                'chat_telegram_id': row.chat_telegram_id,
                'chat_username': row.chat_username
            })
            subscriptions.append(ChatSubscriptionWithChatInfo(**subscription_dict))

        return subscriptions

