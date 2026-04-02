from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_admin
from app.models import AIReview
from app.schemas.application import ApplicationResponse, AdminStatusUpdate
from app.routers.applications import get_application_or_404

router = APIRouter(prefix="/admin", tags=["admin"])


@router.patch("/applications/{application_id}/status", response_model=ApplicationResponse)
def update_application_status(
    application_id: int,
    payload: AdminStatusUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    application = get_application_or_404(db, application_id)
    application.status = payload.status
    application.updated_at = datetime.utcnow()
    db.commit()
    return get_application_or_404(db, application_id)


@router.post("/applications/{application_id}/ai-review/mock", response_model=ApplicationResponse)
def regenerate_mock_ai_review(
    application_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    application = get_application_or_404(db, application_id)

    if application.ai_review:
        application.ai_review.score = 84.2
        application.ai_review.summary = "Заявка повторно проанализирована. Обнаружен приемлемый уровень соответствия."
        application.ai_review.recommendations = (
            "Добавить более точное описание методологии, календарный план и обоснование сметы."
        )
    else:
        review = AIReview(
            application_id=application.id,
            score=84.2,
            summary="Заявка повторно проанализирована. Обнаружен приемлемый уровень соответствия.",
            recommendations="Добавить более точное описание методологии, календарный план и обоснование сметы.",
        )
        db.add(review)

    application.updated_at = datetime.utcnow()
    db.commit()
    return get_application_or_404(db, application_id)