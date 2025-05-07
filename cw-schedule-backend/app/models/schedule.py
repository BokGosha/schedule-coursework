from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Boolean,
    Text,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    is_all_day = Column(Boolean, default=False)
    location = Column(String, nullable=True)
    color = Column(String, nullable=True)
    is_recurring = Column(Boolean, default=False)
    recurrence_rule = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="schedules", lazy="selectin")

    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    category = relationship(
        "Category", back_populates="schedules", lazy="selectin"
    )

    shares = relationship(
        "SharedSchedule", back_populates="schedule", lazy="selectin"
    )
