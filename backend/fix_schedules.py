#!/usr/bin/env python3
"""
Исправление существующих расписаний - пересчет next_run_at
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import async_session
from app.services.user_verification_schedule import VerificationScheduleService


async def fix_schedules():
    """Пересчитать next_run_at для всех расписаний"""
    async with async_session() as db:
        schedule_service = VerificationScheduleService(db)
        schedules = await schedule_service.get_all_schedules()
        
        print("=" * 70)
        print("🔧 ИСПРАВЛЕНИЕ РАСПИСАНИЙ")
        print("=" * 70)
        
        if not schedules:
            print("❌ Расписаний нет!")
            return
        
        print(f"Найдено расписаний: {len(schedules)}\n")
        
        for schedule in schedules:
            print(f"📌 Schedule #{schedule.id}")
            print(f"   Текущее next_run_at: {schedule.next_run_at}")
            
            # Пересчитываем next_run_at используя новую логику
            new_next_run = schedule_service._calculate_next_run(
                schedule.schedule_time,
                schedule.interval_hours
            )
            
            print(f"   Новое next_run_at:   {new_next_run}")
            
            # Обновляем в базе
            schedule.next_run_at = new_next_run
            
            print(f"   ✅ Обновлено\n")
        
        await db.commit()
        
        print("=" * 70)
        print("✅ Все расписания исправлены!")
        print("=" * 70)
        print("\n💡 Теперь перезапустите backend сервер:")
        print("   1. Остановите uvicorn (Ctrl+C в терминале)")
        print("   2. Запустите заново: uvicorn app.main:app --reload")
        print("=" * 70)


if __name__ == "__main__":
    asyncio.run(fix_schedules())
