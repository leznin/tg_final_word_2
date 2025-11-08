"""
User search logs model for tracking mini-app search usage
"""

from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class UserSearchLog(Base):
    """Model for tracking user search operations in mini-app"""
    
    __tablename__ = "user_search_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    telegram_user_id = Column(Integer, nullable=False, index=True)
    search_query = Column(String(255), nullable=False)
    results_count = Column(Integer, default=0)
    searched_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationship to User table
    user = relationship("User", backref="search_logs")

    def __repr__(self):
        return f"<UserSearchLog(id={self.id}, user_id={self.user_id}, query='{self.search_query}', searched_at={self.searched_at})>"
