"""
Subscription prices service with business logic
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update
from typing import List, Optional

from app.models.subscription_prices import SubscriptionPrice
from app.schemas.subscription_prices import SubscriptionPriceCreate, SubscriptionPriceUpdate, SubscriptionPriceResponse


class SubscriptionPricesService:
    """Service class for subscription prices operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_price_by_type(self, subscription_type: str) -> Optional[SubscriptionPrice]:
        """Get active subscription price by type"""
        result = await self.db.execute(
            select(SubscriptionPrice)
            .where(and_(
                SubscriptionPrice.subscription_type == subscription_type,
                SubscriptionPrice.is_active == True
            ))
            .order_by(SubscriptionPrice.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_all_prices(self, include_inactive: bool = False) -> List[SubscriptionPrice]:
        """Get all subscription prices"""
        query = select(SubscriptionPrice)
        if not include_inactive:
            query = query.where(SubscriptionPrice.is_active == True)
        query = query.order_by(SubscriptionPrice.subscription_type, SubscriptionPrice.created_at.desc())

        result = await self.db.execute(query)
        return result.scalars().all()

    async def create_price(self, price_data: SubscriptionPriceCreate) -> SubscriptionPrice:
        """Create a new subscription price"""
        # First, deactivate all existing active prices of the same type
        await self.db.execute(
            update(SubscriptionPrice)
            .where(and_(
                SubscriptionPrice.subscription_type == price_data.subscription_type,
                SubscriptionPrice.is_active == True
            ))
            .values(is_active=False)
        )

        db_price = SubscriptionPrice(**price_data.model_dump())
        self.db.add(db_price)
        await self.db.commit()
        await self.db.refresh(db_price)
        return db_price

    async def update_price(self, price_id: int, price_data: SubscriptionPriceUpdate) -> Optional[SubscriptionPrice]:
        """Update subscription price"""
        db_price = await self.get_price_by_id(price_id)
        if not db_price:
            return None

        # Store original type before update
        original_type = db_price.subscription_type

        for field, value in price_data.model_dump(exclude_unset=True).items():
            setattr(db_price, field, value)

        # If subscription type changed, deactivate other active prices of the new type
        new_type = getattr(price_data, 'subscription_type', None)
        if new_type and new_type != original_type:
            await self.db.execute(
                update(SubscriptionPrice)
                .where(and_(
                    SubscriptionPrice.subscription_type == new_type,
                    SubscriptionPrice.is_active == True,
                    SubscriptionPrice.id != price_id  # Don't deactivate the one we're updating
                ))
                .values(is_active=False)
            )

        await self.db.commit()
        await self.db.refresh(db_price)
        return db_price

    async def get_price_by_id(self, price_id: int) -> Optional[SubscriptionPrice]:
        """Get subscription price by ID"""
        result = await self.db.execute(select(SubscriptionPrice).where(SubscriptionPrice.id == price_id))
        return result.scalar_one_or_none()

    async def deactivate_price(self, price_id: int) -> bool:
        """Deactivate subscription price"""
        db_price = await self.get_price_by_id(price_id)
        if not db_price:
            return False

        db_price.is_active = False
        await self.db.commit()
        return True

    async def cleanup_duplicate_prices(self) -> int:
        """Deactivate duplicate active prices, keeping only the most recent one for each type"""
        from sqlalchemy import func

        # Get all active prices grouped by type, ordered by creation date
        result = await self.db.execute(
            select(
                SubscriptionPrice.subscription_type,
                func.array_agg(SubscriptionPrice.id).label('ids')
            )
            .where(SubscriptionPrice.is_active == True)
            .group_by(SubscriptionPrice.subscription_type)
        )

        total_deactivated = 0

        for row in result:
            subscription_type = row.subscription_type
            ids = row.ids

            if len(ids) > 1:
                # Keep the most recent (last created), deactivate others
                # Get creation dates for these IDs
                date_result = await self.db.execute(
                    select(SubscriptionPrice.id, SubscriptionPrice.created_at)
                    .where(SubscriptionPrice.id.in_(ids))
                    .order_by(SubscriptionPrice.created_at.desc())
                )

                prices_with_dates = date_result.fetchall()
                # Keep the first one (most recent), deactivate the rest
                ids_to_deactivate = [price.id for price in prices_with_dates[1:]]

                if ids_to_deactivate:
                    await self.db.execute(
                        update(SubscriptionPrice)
                        .where(SubscriptionPrice.id.in_(ids_to_deactivate))
                        .values(is_active=False)
                    )
                    total_deactivated += len(ids_to_deactivate)

        if total_deactivated > 0:
            await self.db.commit()

        return total_deactivated

