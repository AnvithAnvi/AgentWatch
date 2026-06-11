from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.database import get_db
from app import models
from app.deps import get_current_project
import os

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


@router.post("/purge_old_runs")
def purge_old_runs(days: int | None = None, db: Session = Depends(get_db), project: models.Project = Depends(get_current_project)):
    # only allow purging for the authenticated project
    if days is None:
        days = project.retention_days
    cutoff = datetime.utcnow() - timedelta(days=days)
    deleted = db.query(models.Run).filter(models.Run.project_id == project.id, models.Run.created_at < cutoff).delete(synchronize_session=False)
    db.commit()
    return {"deleted": deleted}
