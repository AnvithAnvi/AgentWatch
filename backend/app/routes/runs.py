from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app import models, schemas
from app.services.evaluator import evaluate_run
from app.deps import get_current_project
import os
import requests

router = APIRouter(
    prefix="/runs",
    tags=["Runs"]
)


@router.post("/", response_model=schemas.RunResponse)
def create_run(run: schemas.RunCreate, db: Session = Depends(get_db), project: models.Project = Depends(get_current_project)):
    # enforce API key ownership: ignore client-sent project_id and use authenticated project
    new_run = models.Run(
        project_id=project.id,
        run_name=run.run_name,
        input_text=run.input_text,
        model=run.model,
        trace_id=run.trace_id,
        host=run.host,
        pid=run.pid,
        meta_json=run.meta_json,
        status="running"
    )

    db.add(new_run)
    db.commit()
    db.refresh(new_run)

    return new_run


@router.get("/", response_model=list[schemas.RunResponse])
def get_runs(db: Session = Depends(get_db)):
    runs = db.query(models.Run).options(
        joinedload(models.Run.evaluations)
    ).order_by(models.Run.created_at.desc()).all()

    for run in runs:
        latest_eval = run.evaluations[-1] if run.evaluations else None
        run.latest_evaluation_label = latest_eval.label if latest_eval else None
        run.latest_evaluation_score = latest_eval.score if latest_eval else None

    return runs


@router.get("/{run_id}", response_model=schemas.RunDetailResponse)
def get_run(run_id: int, db: Session = Depends(get_db)):
    run = db.query(models.Run).options(
        joinedload(models.Run.spans),
        joinedload(models.Run.evaluations)
    ).filter(
        models.Run.id == run_id
    ).first()

    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    return run


@router.patch("/{run_id}/complete", response_model=schemas.RunResponse)
def complete_run(
    run_id: int,
    run_update: schemas.RunComplete,
    db: Session = Depends(get_db)
):
    run = db.query(models.Run).filter(
        models.Run.id == run_id
    ).first()

    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    run.output_text = run_update.output_text
    run.status = run_update.status
    run.latency_ms = run_update.latency_ms
    run.cost_usd = run_update.cost_usd

    db.commit()
    db.refresh(run)

    db.query(models.Evaluation).filter(
        models.Evaluation.run_id == run_id
    ).delete(synchronize_session=False)
    db.commit()

    run_with_spans = db.query(models.Run).options(
        joinedload(models.Run.spans)
    ).filter(
        models.Run.id == run_id
    ).first()

    evaluation_result = evaluate_run(run_with_spans)

    new_evaluation = models.Evaluation(
        run_id=run_id,
        score=evaluation_result["score"],
        label=evaluation_result["label"],
        reason=evaluation_result["reason"],
        has_error=evaluation_result["has_error"],
        latency_warning=evaluation_result["latency_warning"],
        tool_failure=evaluation_result["tool_failure"],
        empty_output=evaluation_result["empty_output"],
    )

    db.add(new_evaluation)
    db.commit()
    db.refresh(run)

    # Alerting: if configured and run failed, POST to webhook(s)
    try:
        alert_urls = os.getenv("AGENTWATCH_ALERT_WEBHOOKS")
        if alert_urls and new_evaluation.label == "fail":
            payload = {
                "project_id": run.project_id,
                "run_id": run.id,
                "label": new_evaluation.label,
                "score": new_evaluation.score,
                "reason": new_evaluation.reason,
            }
            for url in alert_urls.split(","):
                try:
                    requests.post(url.strip(), json=payload, timeout=3)
                except Exception:
                    pass
    except Exception:
        pass

    return run