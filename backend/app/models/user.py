from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    schedules = relationship(
        "Schedule", back_populates="user", lazy="selectin"
    )

    friends = relationship(
        "Friend",
        foreign_keys="Friend.user_id",
        back_populates="user",
        lazy="selectin",
    )
    friend_of = relationship(
        "Friend",
        foreign_keys="Friend.friend_id",
        back_populates="friend",
        lazy="selectin",
    )

    shared_schedules = relationship(
        "SharedSchedule",
        foreign_keys="SharedSchedule.user_id",
        back_populates="user",
        lazy="selectin",
    )
    received_schedules = relationship(
        "SharedSchedule",
        foreign_keys="SharedSchedule.shared_with_id",
        back_populates="shared_with_user",
        lazy="selectin",
    )
