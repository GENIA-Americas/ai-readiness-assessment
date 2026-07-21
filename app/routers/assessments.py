from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_org
from app.db import get_db
from app.models import Assessment
from app.schemas import AssessmentCreate, AssessmentResult
from app.scoring import score_assessment

router = APIRouter(prefix="/assessments", tags=["assessments"])


@router.post("", response_model=AssessmentResult, status_code=201)
def create_assessment(
    payload: AssessmentCreate,
    db: Session = Depends(get_db),
    org_name: str = Depends(get_current_org),
):
    category_scores, overall_score, readiness_tier = score_assessment(payload.responses)

    record = Assessment(
        org_name=org_name,
        sector=payload.sector,
        org_size=payload.org_size,
        responses=payload.responses.model_dump(),
        category_scores=category_scores,
        overall_score=overall_score,
        readiness_tier=readiness_tier,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/{assessment_id}", response_model=AssessmentResult)
def get_assessment(
    assessment_id: int,
    db: Session = Depends(get_db),
    org_name: str = Depends(get_current_org),
):
    record = db.get(Assessment, assessment_id)
    if record is None or record.org_name != org_name:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return record


@router.get("", response_model=list[AssessmentResult])
def list_assessments(
    db: Session = Depends(get_db),
    org_name: str = Depends(get_current_org),
):
    # Scoped to the caller's org — this previously returned every org's
    # assessments to any caller with no auth at all, arguably the most
    # sensitive data in the whole toolkit (raw self-reported governance
    # and security gaps per org).
    return (
        db.query(Assessment)
        .filter(Assessment.org_name == org_name)
        .order_by(Assessment.created_at.desc())
        .all()
    )
