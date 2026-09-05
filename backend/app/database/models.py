from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    Integer,
    String,
    Text,
)

from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database.database import Base


class DocumentAnalysis(Base):

    __tablename__ = "document_analyses"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    classification_confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    risk_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    is_anomaly: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False
    )

    anomaly_score: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    locations: Mapped[str] = mapped_column(
        Text,
        default=""
    )

    quantities: Mapped[str] = mapped_column(
        Text,
        default=""
    )

    word_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    text_preview: Mapped[str] = mapped_column(
        Text,
        default=""
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )