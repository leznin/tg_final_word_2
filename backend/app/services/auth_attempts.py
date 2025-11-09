"""
Auth attempts service for tracking and blocking login attempts by fingerprint
"""

from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from app.models.auth_attempts import AuthAttempt


class AuthAttemptsService:
    """Service for managing authentication attempts and fingerprint blocking"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def record_attempt(
        self,
        fingerprint: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = False,
        blocked: bool = False,
        block_reason: Optional[str] = None
    ) -> AuthAttempt:
        """Record or update authentication attempt for fingerprint+user_agent combination"""

        # Try to find existing attempt for this fingerprint+user_agent combination
        from sqlalchemy import and_
        existing_attempt = await self.db.execute(
            select(AuthAttempt).where(
                and_(
                    AuthAttempt.fingerprint == fingerprint,
                    AuthAttempt.user_agent == user_agent
                )
            )
        )
        attempt = existing_attempt.scalar_one_or_none()

        if attempt:
            # Update existing attempt
            attempt.attempt_count = (attempt.attempt_count or 0) + 1
            attempt.last_attempt_at = func.now()

            if success:
                attempt.success_count = (attempt.success_count or 0) + 1
            else:
                attempt.failed_count = (attempt.failed_count or 0) + 1

            if blocked:
                attempt.blocked = True
                attempt.block_reason = block_reason

            # Update IP if different
            if ip_address and attempt.ip_address != ip_address:
                attempt.ip_address = ip_address

        else:
            # Create new attempt
            attempt = AuthAttempt(
                fingerprint=fingerprint,
                ip_address=ip_address,
                user_agent=user_agent,
                attempt_count=1,
                failed_count=1 if not success else 0,
                success_count=1 if success else 0,
                blocked=blocked,
                block_reason=block_reason
            )
            self.db.add(attempt)

        await self.db.commit()
        await self.db.refresh(attempt)

        return attempt

    async def is_fingerprint_blocked(self, fingerprint: str, window_minutes: int = 15) -> tuple[bool, Optional[str]]:
        """
        Check if fingerprint is blocked based on recent attempts
        Returns (is_blocked, block_reason)
        """
        # Check for recent failed attempts (last window_minutes)
        window_start = datetime.utcnow() - timedelta(minutes=window_minutes)

        query = select(AuthAttempt).where(
            and_(
                AuthAttempt.fingerprint == fingerprint,
                AuthAttempt.last_attempt_at >= window_start
            )
        )

        result = await self.db.execute(query)
        attempts = result.scalars().all()

        # Calculate total failed attempts in the window
        failed_count = sum(attempt.failed_count for attempt in attempts)

        # Block if more than 5 failed attempts in the window
        if failed_count >= 5:
            block_reason = f"Too many failed attempts ({failed_count}) in {window_minutes} minutes"
            return True, block_reason

        # Check if already marked as blocked
        blocked_query = select(AuthAttempt).where(
            and_(
                AuthAttempt.fingerprint == fingerprint,
                AuthAttempt.blocked == True
            )
        ).order_by(desc(AuthAttempt.last_attempt_at)).limit(1)

        blocked_result = await self.db.execute(blocked_query)
        latest_blocked = blocked_result.scalar_one_or_none()

        if latest_blocked and latest_blocked.block_reason:
            return True, latest_blocked.block_reason

        return False, None

    async def get_fingerprint_stats(self, fingerprint: str, hours: int = 24) -> dict:
        """Get statistics for a fingerprint"""
        window_start = datetime.utcnow() - timedelta(hours=hours)

        query = select(
            func.sum(AuthAttempt.attempt_count).label('total_attempts'),
            func.sum(AuthAttempt.success_count).label('successful_attempts'),
            func.sum(AuthAttempt.failed_count).label('failed_attempts'),
            func.count(func.cast(AuthAttempt.blocked, type_=func.Integer())).label('blocked_records')
        ).where(
            and_(
                AuthAttempt.fingerprint == fingerprint,
                AuthAttempt.last_attempt_at >= window_start
            )
        )

        result = await self.db.execute(query)
        row = result.first()

        total = row.total_attempts or 0
        successful = row.successful_attempts or 0
        failed = row.failed_attempts or 0
        blocked_records = row.blocked_records or 0

        return {
            'total_attempts': total,
            'successful_attempts': successful,
            'failed_attempts': failed,
            'blocked_records': blocked_records,
            'success_rate': (successful / total * 100) if total > 0 else 0
        }

    async def get_recent_attempts(self, fingerprint: str, limit: int = 10) -> List[AuthAttempt]:
        """Get recent attempts for a fingerprint"""
        query = select(AuthAttempt).where(
            AuthAttempt.fingerprint == fingerprint
        ).order_by(desc(AuthAttempt.last_attempt_at)).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def cleanup_old_attempts(self, days: int = 30) -> int:
        """Clean up old authentication attempts"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        query = select(AuthAttempt).where(AuthAttempt.last_attempt_at < cutoff_date)
        result = await self.db.execute(query)
        old_attempts = result.scalars().all()

        deleted_count = len(old_attempts)
        for attempt in old_attempts:
            await self.db.delete(attempt)

        await self.db.commit()
        return deleted_count

    async def reset_blocked_attempts(self, minutes: int = 20) -> int:
        """
        Reset authentication attempts for users blocked longer than specified minutes
        This allows users to try again after cooldown period
        
        Args:
            minutes: Number of minutes after which to reset attempts (default: 20)
            
        Returns:
            Number of records reset
        """
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        
        # Find all blocked attempts older than cutoff time
        query = select(AuthAttempt).where(
            and_(
                AuthAttempt.blocked == True,
                AuthAttempt.last_attempt_at < cutoff_time
            )
        )
        
        result = await self.db.execute(query)
        blocked_attempts = result.scalars().all()
        
        reset_count = 0
        for attempt in blocked_attempts:
            # Reset the attempt counters and blocked status
            attempt.blocked = False
            attempt.failed_count = 0
            attempt.attempt_count = 0
            attempt.success_count = 0
            attempt.block_reason = None
            attempt.blocked_until = None
            reset_count += 1
        
        await self.db.commit()
        
        if reset_count > 0:
            print(f"[AUTH] Reset {reset_count} blocked authentication attempts after {minutes} minutes cooldown")
        
        return reset_count
