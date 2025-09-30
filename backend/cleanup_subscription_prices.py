"""
Script to check and cleanup duplicate subscription prices
"""
import asyncio
from app.core.database import init_db, async_session
from app.services.subscription_prices import SubscriptionPricesService
from sqlalchemy import select
from app.models.subscription_prices import SubscriptionPrice


async def check_subscription_prices():
    """Check current subscription prices in database"""
    await init_db()
    async with async_session() as db:
        # Get all prices
        result = await db.execute(
            select(SubscriptionPrice).order_by(
                SubscriptionPrice.subscription_type,
                SubscriptionPrice.created_at.desc()
            )
        )
        prices = result.scalars().all()

        print("Все записи subscription_prices:")
        for price in prices:
            print(f"ID: {price.id}, Type: {price.subscription_type}, Price: {price.price_stars}, "
                  f"Active: {price.is_active}, Created: {price.created_at}")

        print("\nАктивные записи:")
        active_prices = [p for p in prices if p.is_active]
        for price in active_prices:
            print(f"ID: {price.id}, Type: {price.subscription_type}, Price: {price.price_stars}")

        print(f"\nВсего записей: {len(prices)}, Активных: {len(active_prices)}")

        # Check for duplicates
        month_prices = [p for p in active_prices if p.subscription_type == 'month']
        year_prices = [p for p in active_prices if p.subscription_type == 'year']

        print(f"\nАктивных месячных подписок: {len(month_prices)}")
        print(f"Активных годовых подписок: {len(year_prices)}")

        if len(month_prices) > 1 or len(year_prices) > 1:
            print("\n⚠️  ОБНАРУЖЕНЫ ДУБЛИКАТЫ! Запускаю очистку...")

            service = SubscriptionPricesService(db)
            deactivated_count = await service.cleanup_duplicate_prices()
            print(f"✅ Деактивировано дубликатов: {deactivated_count}")

            # Show result after cleanup
            print("\nПосле очистки:")
            result = await db.execute(
                select(SubscriptionPrice)
                .where(SubscriptionPrice.is_active == True)
                .order_by(SubscriptionPrice.subscription_type, SubscriptionPrice.created_at.desc())
            )
            clean_prices = result.scalars().all()
            for price in clean_prices:
                print(f"ID: {price.id}, Type: {price.subscription_type}, Price: {price.price_stars}")
        else:
            print("\n✅ Дубликатов не найдено.")


if __name__ == "__main__":
    asyncio.run(check_subscription_prices())
