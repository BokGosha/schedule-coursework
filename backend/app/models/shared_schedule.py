from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Enum,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base
import enum


class PermissionLevel(str, enum.Enum):
    VIEW = "view"
    EDIT = "edit"


class SharedSchedule(Base):
    __tablename__ = "shared_schedules"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    shared_with_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    schedule_id = Column(
        Integer, ForeignKey("schedules.id", ondelete="CASCADE"), nullable=False
    )
    permission_level = Column(
        Enum(PermissionLevel), default=PermissionLevel.VIEW, nullable=False
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship(
        "User", foreign_keys=[user_id], back_populates="shared_schedules"
    )
    shared_with_user = relationship(
        "User",
        foreign_keys=[shared_with_id],
        back_populates="received_schedules",
    )
    schedule = relationship("Schedule", back_populates="shares")
