"""User persistence models."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Integer,
    String,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class User(Base):
    """User account identity, profile, and progression state."""

    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid4,
    )
    auth_subject: Mapped[UUID] = mapped_column(
        Uuid,
        unique=True,
        index=True,
        nullable=False,
    )
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)
    display_name: Mapped[str] = mapped_column(
        String(100),
        default="Suspect_A7K92B",
        nullable=False,
    )
    avatar_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        default=None,
    )
    is_guest: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    total_xp: Mapped[int] = mapped_column(
        BigInteger,
        default=0,
        nullable=False,
    )
    credit_balance: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    # current_rank_id: Mapped[UUID | None] = mapped_column(
    #     Uuid,
    #     ForeignKey("ranks.id"),
    #     nullable=True,
    # )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


__all__ = ["User"]
