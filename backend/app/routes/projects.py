from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import secrets

from app.database import get_db
from app import models, schemas

router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)


@router.post("/", response_model=schemas.ProjectResponse)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    existing_project = db.query(models.Project).filter(
        models.Project.name == project.name
    ).first()

    if existing_project:
        raise HTTPException(status_code=400, detail="Project already exists")

    api_key = "aw_" + secrets.token_urlsafe(24)

    new_project = models.Project(
        name=project.name,
        api_key=api_key,
        retention_days=project.retention_days
    )

    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    return new_project


@router.get("/", response_model=list[schemas.ProjectResponse])
def get_projects(db: Session = Depends(get_db)):
    return db.query(models.Project).order_by(models.Project.created_at.desc()).all()


@router.get("/{project_id}", response_model=schemas.ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(
        models.Project.id == project_id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return project