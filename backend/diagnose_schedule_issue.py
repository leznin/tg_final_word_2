#!/usr/bin/env python3
"""
Детальная диагностика проблемы с расписанием
"""

import asyncio
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import async_session
from app.services.user_verification_schedule import VerificationScheduleService


async def diagnose():
    """Детальная диагностика"""
    print("=" * 80)
    print("🔍 ДЕТАЛЬНАЯ ДИАГНОСТИКА ПРОБЛЕМЫ С РАСПИСАНИЕМ")
    print("=" * 80)
    
    # Проверка системного времени
    now_local = datetime.now()
    now_utc = datetime.utcnow()
    
    print(f"\n⏰ СИСТЕМНОЕ ВРЕМЯ:")
    print(f"   Локальное время: {now_local.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   UTC время:       {now_utc.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Разница:         {(now_local - now_utc).total_seconds() / 3600:.1f} часов")
    print(f"   Timezone aware:  Local={now_local.tzinfo}, UTC={now_utc.tzinfo}")
    print(f"\n   ℹ️  ВАЖНО: После исправления код использует ЛОКАЛЬНОЕ время!")
    
    # Проверка расписаний
    async with async_session() as db:
        schedule_service = VerificationScheduleService(db)
        
        print(f"\n📋 РАСПИСАНИЯ В БАЗЕ ДАННЫХ:")
        schedules = await schedule_service.get_all_schedules()
        
        if not schedules:
            print("   ❌ Расписаний нет!")
            return
        
        print(f"   Всего расписаний: {len(schedules)}")
        
        for schedule in schedules:
            print(f"\n   {'='*70}")
            print(f"   📌 Schedule ID: {schedule.id}")
            print(f"   ✓ Enabled: {schedule.enabled}")
            print(f"   ✓ Schedule time: {schedule.schedule_time}")
            print(f"   ✓ Interval: {schedule.interval_hours} hours")
            print(f"   ✓ Chat ID: {schedule.chat_id or 'All chats'}")
            
            if schedule.next_run_at:
                print(f"\n   ⏰ Next run at:")
                print(f"      Value: {schedule.next_run_at}")
                print(f"      Type: {type(schedule.next_run_at)}")
                print(f"      Timezone: {schedule.next_run_at.tzinfo}")
                
                # Сравнение времени С ЛОКАЛЬНЫМ ВРЕМЕНЕМ
                print(f"\n   🔍 СРАВНЕНИЕ ВРЕМЕНИ (ЛОКАЛЬНОЕ):")
                print(f"      next_run_at:  {schedule.next_run_at}")
                print(f"      now_local:    {now_local}")
                
                # Проверка условия с локальным временем
                should_run_local = schedule.next_run_at <= now_local
                print(f"\n   ❓ ДОЛЖНО ЛИ ЗАПУСТИТЬСЯ:")
                print(f"      next_run_at <= now_local: {should_run_local}")
                
                if schedule.next_run_at.tzinfo and now_local.tzinfo is None:
                    print(f"      ⚠️  ПРОБЛЕМА: next_run_at имеет timezone, а now_local - нет!")
                elif schedule.next_run_at.tzinfo is None and now_local.tzinfo:
                    print(f"      ⚠️  ПРОБЛЕМА: now_local имеет timezone, а next_run_at - нет!")
                
                diff = (now_local - schedule.next_run_at).total_seconds()
                if diff > 0:
                    print(f"      Время прошло: {diff:.0f} секунд ({diff/60:.1f} минут) - ДОЛЖНО ЗАПУСТИТЬСЯ!")
                else:
                    print(f"      До запуска:   {-diff:.0f} секунд ({-diff/60:.1f} минут)")
                
            if schedule.last_run_at:
                print(f"\n   ⏰ Last run at:")
                print(f"      Value: {schedule.last_run_at}")
                print(f"      Timezone: {schedule.last_run_at.tzinfo}")
            else:
                print(f"\n   ⏰ Last run at: ❌ НИКОГДА НЕ ЗАПУСКАЛОСЬ")
        
        # Проверка метода get_schedules_to_run
        print(f"\n\n{'='*80}")
        print(f"🔍 ПРОВЕРКА МЕТОДА get_schedules_to_run():")
        print(f"{'='*80}")
        
        schedules_to_run = await schedule_service.get_schedules_to_run()
        print(f"   Найдено расписаний для запуска: {len(schedules_to_run)}")
        
        if schedules_to_run:
            for schedule in schedules_to_run:
                print(f"   ✓ Schedule #{schedule.id} должно запуститься")
        else:
            print(f"   ❌ НЕТ РАСПИСАНИЙ ДЛЯ ЗАПУСКА!")
            print(f"\n   🤔 ВОЗМОЖНЫЕ ПРИЧИНЫ:")
            print(f"   1. Проблема с timezone (aware vs naive datetime)")
            print(f"   2. Проблема с сравнением datetime")
            print(f"   3. Расписания отключены (enabled=False)")
            print(f"   4. Ошибка в логике get_schedules_to_run()")
    
    print(f"\n{'='*80}")
    print(f"💡 РЕКОМЕНДАЦИИ:")
    print(f"{'='*80}")
    print(f"1. Проверьте логи backend сервера на наличие 'Started scheduled user verification task'")
    print(f"2. Если задача запущена, но расписания не выполняются - проблема в timezone")
    print(f"3. Перезапустите backend сервер если задача не запущена")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    asyncio.run(diagnose())
