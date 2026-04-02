from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse
from app.services.expert_ai import analyze_application, AIReviewResult
from app.models import AIReview
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.config import settings
from app.database import get_db
from app.deps import get_current_user
from app.models import (
    Application,
    ApplicationFile,
    Competition,
    User,
    UserRole,
    AIReview,
    ApplicationStatus,
)
from app.schemas.application import (
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationResponse,
    ApplicationListItem,
    ApplicationFileResponse,
    AIReviewResponse,
)
from app.services.files import validate_upload_file, build_storage_name, ensure_upload_dir

router = APIRouter(prefix="/applications", tags=["applications"])


def get_application_or_404(db: Session, application_id: int) -> Application:
    query = (
        select(Application)
        .where(Application.id == application_id)
        .options(
            joinedload(Application.owner),
            joinedload(Application.competition),
            joinedload(Application.files),
            joinedload(Application.ai_review),
        )
    )
    application = db.scalar(query)
    if not application:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Заявка не найдена")
    return application


def check_application_access(application: Application, current_user: User) -> None:
    if current_user.role == UserRole.admin:
        return
    if application.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет доступа к этой заявке")


@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application(
    payload: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    competition = db.get(Competition, payload.competition_id)
    if not competition:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Конкурс не найден")

    application = Application(
        title=payload.title,
        description=payload.description,
        project_goal=payload.project_goal,
        requested_amount=payload.requested_amount,
        owner_id=current_user.id,
        competition_id=payload.competition_id,
        status=ApplicationStatus.submitted,
        submitted_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(application)
    db.commit()
    db.refresh(application)

    try:
        ai_result = await analyze_application(
            text=application.description + " " + (application.project_goal or ""),
            title=application.title
        )

        ai_review = AIReview(
            application_id=application.id,
            score=ai_result.score,
            summary=ai_result.summary,
            recommendations=ai_result.recommendations
        )
        db.add(ai_review)
        db.commit()
    except Exception as e:
        print(f"AI analysis failed: {e}")

    return get_application_or_404(db, application.id)


@router.get("", response_model=list[ApplicationListItem])
def list_applications(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = (
        select(Application)
        .options(joinedload(Application.competition))
        .order_by(Application.created_at.desc())
    )

    if current_user.role != UserRole.admin:
        query = query.where(Application.owner_id == current_user.id)

    return db.scalars(query).unique().all()


@router.get("/{application_id}", response_model=ApplicationResponse)
def get_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    application = get_application_or_404(db, application_id)
    check_application_access(application, current_user)
    return application


@router.put("/{application_id}", response_model=ApplicationResponse)
def update_application(
    application_id: int,
    payload: ApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    application = get_application_or_404(db, application_id)
    check_application_access(application, current_user)

    if current_user.role != UserRole.admin and application.status in {
        ApplicationStatus.approved,
        ApplicationStatus.rejected,
        ApplicationStatus.in_review,
    }:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя редактировать заявку после передачи на рассмотрение",
        )

    for field, value in payload.model_dump(exclude_unset=True).items():
        if field == "status" and current_user.role != UserRole.admin:
            continue
        setattr(application, field, value)

    application.updated_at = datetime.utcnow()
    db.commit()
    return get_application_or_404(db, application_id)


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    application = get_application_or_404(db, application_id)

    if current_user.role != UserRole.admin and application.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет доступа к удалению заявки")

    db.delete(application)
    db.commit()
    return None


@router.post("/{application_id}/files", response_model=ApplicationFileResponse, status_code=status.HTTP_201_CREATED)
async def upload_application_file(
    application_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    application = get_application_or_404(db, application_id)
    check_application_access(application, current_user)

    content = await file.read()
    file_size = len(content)
    validate_upload_file(file, file_size)

    ensure_upload_dir()
    stored_name = build_storage_name(file.filename or "file.bin")
    file_path = f"{settings.upload_dir}/{stored_name}"

    with open(file_path, "wb") as f:
        f.write(content)

    db_file = ApplicationFile(
        application_id=application.id,
        original_name=file.filename or stored_name,
        stored_name=stored_name,
        mime_type=file.content_type or "application/octet-stream",
        size_bytes=file_size,
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file


@router.get("/{application_id}/files/{file_id}/download")
def download_application_file(
    application_id: int,
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    application = get_application_or_404(db, application_id)
    check_application_access(application, current_user)

    db_file = db.get(ApplicationFile, file_id)
    if not db_file or db_file.application_id != application.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Файл не найден",
        )

    file_path = Path(settings.upload_dir) / db_file.stored_name
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Файл отсутствует на диске",
        )

    return FileResponse(
        path=file_path,
        media_type=db_file.mime_type,
        filename=db_file.original_name,
    )


@router.post("/{application_id}/ai-review")
async def trigger_ai_review(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Запускает ExpertAI анализ заявки"""
    application = get_application_or_404(db, application_id)
    check_application_access(application, current_user)
    
    # Анализируем текст заявки
    result = await analyze_application(
        text=application.description + " " + (application.project_goal or ""),
        title=application.title
    )
    
    # Сохраняем результат в БД
    ai_review = AIReview(
        application_id=application_id,
        score=result.score,
        summary=result.summary,
        recommendations=result.recommendations
    )
    db.add(ai_review)
    db.commit()
    db.refresh(ai_review)
    
    return ai_review

@router.get("/{application_id}/ai-review")
async def get_ai_review(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получает результат AI-анализа"""
    application = get_application_or_404(db, application_id)
    check_application_access(application, current_user)
    
    ai_review = db.query(AIReview).filter(
        AIReview.application_id == application_id
    ).first()
    
    if not ai_review:
        raise HTTPException(status_code=404, detail="AI-анализ не проведён")
    
    return ai_review
