from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_admin
from app.models import Competition
from app.schemas.competition import CompetitionCreate, CompetitionResponse

router = APIRouter(prefix="/competitions", tags=["competitions"])


@router.get("", response_model=list[CompetitionResponse])
def list_competitions(db: Session = Depends(get_db)):
    return db.scalars(select(Competition).order_by(Competition.deadline.asc())).all()


@router.post("", response_model=CompetitionResponse, status_code=status.HTTP_201_CREATED)
def create_competition(
    payload: CompetitionCreate,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    competition = Competition(
        title=payload.title,
        description=payload.description,
        deadline=payload.deadline,
        status=payload.status,
    )
    db.add(competition)
    db.commit()
    db.refresh(competition)
    return competition


@router.get("/{competition_id}", response_model=CompetitionResponse)
def get_competition(competition_id: int, db: Session = Depends(get_db)):
    competition = db.get(Competition, competition_id)
    if not competition:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Конкурс не найден")
    return competition