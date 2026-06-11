import os
from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app import models


def get_current_project(authorization: str = Header(None), db: Session = Depends(get_db)) -> models.Project:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    if not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization scheme")

    token = authorization.split(" ", 1)[1]

    project = db.query(models.Project).filter(models.Project.api_key == token).first()
    if not project:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return project
