"""
Search boost service for managing additional search purchases
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from app.models.search_boost_purchases import SearchBoostPurchase, SearchBoostPrice
from app.schemas.mini_app import (
    SearchBoostAvailabilityResponse,
    SearchBoostPurchaseResponse,
    SearchBoostPriceResponse,
    SearchBoostPriceUpdate
)


class SearchBoostService:
    """Service for managing search boost purchases and availability"""
    
    MAX_PURCHASES_PER_DAY = 2
    DEFAULT_BOOST_AMOUNT = 10
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def check_purchase_availability(self, user_id: int) -> SearchBoostAvailabilityResponse:
        """
        Check if user can purchase more search boosts today.
        Users can purchase up to 2 boosts per day (24 hours).
        """
        twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
        
        # Count purchases in last 24 hours
        count_query = select(func.count()).select_from(SearchBoostPurchase).where(
            and_(
                SearchBoostPurchase.user_id == user_id,
                SearchBoostPurchase.purchased_at >= twenty_four_hours_ago
            )
        )
        result = await self.db.execute(count_query)
        purchases_today = result.scalar() or 0
        
        can_purchase = purchases_today < self.MAX_PURCHASES_PER_DAY
        remaining_purchases = max(0, self.MAX_PURCHASES_PER_DAY - purchases_today)
        
        reason = None
        if not can_purchase:
            reason = f"Maximum {self.MAX_PURCHASES_PER_DAY} purchases per day reached. Try again later."
        
        return SearchBoostAvailabilityResponse(
            can_purchase=can_purchase,
            purchases_today=purchases_today,
            max_purchases_per_day=self.MAX_PURCHASES_PER_DAY,
            remaining_purchases=remaining_purchases,
            reason=reason
        )
    
    async def get_available_boost_searches(self, user_id: int) -> int:
        """
        Get total number of unused boost searches available for user.
        This counts all active purchases with remaining searches.
        """
        query = select(SearchBoostPurchase).where(
            and_(
                SearchBoostPurchase.user_id == user_id,
                SearchBoostPurchase.is_active == True
            )
        ).order_by(SearchBoostPurchase.purchased_at.asc())
        
        result = await self.db.execute(query)
        purchases = result.scalars().all()
        
        total_available = 0
        for purchase in purchases:
            remaining = purchase.boost_amount - purchase.used_searches
            if remaining > 0:
                total_available += remaining
            else:
                # Mark as inactive if fully used
                purchase.is_active = False
        
        await self.db.commit()
        return total_available
    
    async def use_boost_search(self, user_id: int) -> bool:
        """
        Use one search from available boosts (oldest first).
        Returns True if a boost search was used, False if no boosts available.
        """
        query = select(SearchBoostPurchase).where(
            and_(
                SearchBoostPurchase.user_id == user_id,
                SearchBoostPurchase.is_active == True
            )
        ).order_by(SearchBoostPurchase.purchased_at.asc())
        
        result = await self.db.execute(query)
        purchases = result.scalars().all()
        
        for purchase in purchases:
            remaining = purchase.boost_amount - purchase.used_searches
            if remaining > 0:
                purchase.used_searches += 1
                if purchase.used_searches >= purchase.boost_amount:
                    purchase.is_active = False
                await self.db.commit()
                return True
        
        return False
    
    async def create_purchase(
        self,
        user_id: int,
        telegram_user_id: int,
        price_stars: int,
        telegram_payment_charge_id: Optional[str] = None
    ) -> SearchBoostPurchase:
        """Create a new search boost purchase"""
        purchase = SearchBoostPurchase(
            user_id=user_id,
            telegram_user_id=telegram_user_id,
            boost_amount=self.DEFAULT_BOOST_AMOUNT,
            price_stars=price_stars,
            telegram_payment_charge_id=telegram_payment_charge_id,
            used_searches=0,
            is_active=True
        )
        
        self.db.add(purchase)
        await self.db.commit()
        await self.db.refresh(purchase)
        
        return purchase
    
    async def get_active_price(self) -> Optional[SearchBoostPrice]:
        """Get the active search boost price configuration"""
        query = select(SearchBoostPrice).where(
            SearchBoostPrice.is_active == True
        ).order_by(desc(SearchBoostPrice.updated_at)).limit(1)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def update_price(self, price_update: SearchBoostPriceUpdate) -> SearchBoostPrice:
        """Update or create search boost price"""
        # Get existing price
        existing_price = await self.get_active_price()
        
        if existing_price:
            existing_price.price_stars = price_update.price_stars
            existing_price.updated_at = datetime.utcnow()
            price = existing_price
        else:
            # Create new price
            price = SearchBoostPrice(
                boost_amount=self.DEFAULT_BOOST_AMOUNT,
                price_stars=price_update.price_stars,
                is_active=True
            )
            self.db.add(price)
        
        await self.db.commit()
        await self.db.refresh(price)
        
        return price
    
    async def get_price_response(self) -> Optional[SearchBoostPriceResponse]:
        """Get search boost price as response schema"""
        price = await self.get_active_price()
        
        if not price:
            return None
        
        return SearchBoostPriceResponse(
            id=price.id,
            boost_amount=price.boost_amount,
            price_stars=price.price_stars,
            currency=price.currency,
            is_active=price.is_active,
            created_at=price.created_at,
            updated_at=price.updated_at
        )
