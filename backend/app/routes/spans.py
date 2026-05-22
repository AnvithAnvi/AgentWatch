from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas

router = APIRouter(
    prefix="/runs",
    tags=["Spans"]
)


@router.post("/{run_id}/spans", response_model=schemas.SpanResponse)
def create_span(
    run_id: int,
    span: schemas.SpanCreate,
    db: Session = Depends(get_db)
):
    run = db.query(models.Run).filter(
        models.Run.id == run_id
    ).first()

    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    new_span = models.Span(
        run_id=run_id,
        span_type=span.span_type,
        name=span.name,
        input_json=span.input_json,
        output_json=span.output_json,
        status=span.status,
        latency_ms=span.latency_ms,
        error_message=span.error_message
    )

    db.add(new_span)
    db.commit()
    db.refresh(new_span)

    return new_span