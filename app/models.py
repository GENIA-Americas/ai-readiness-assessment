from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Assessment(Base):
    __tablename__ = "assessments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    org_name: Mapped[str] = mapped_column(String, index=True)
    sector: Mapped[str] = mapped_column(String)
    org_size: Mapped[str] = mapped_column(String)  # e.g. "1-10", "11-50", "51-200", "200+"

    # raw questionnaire answers, kept as JSON so the rubric can evolve without a migration
    responses: Mapped[dict] = mapped_column(JSON)

    # scoring output
    category_scores: Mapped[dict] = mapped_column(JSON)
    overall_score: Mapped[float] = mapped_column(Float)
    readiness_tier: Mapped[str] = mapped_column(String)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
