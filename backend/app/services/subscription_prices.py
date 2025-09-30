"""
Subscription prices service with business logic
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
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

        for field, value in price_data.model_dump(exclude_unset=True).items():
            setattr(db_price, field, value)

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

