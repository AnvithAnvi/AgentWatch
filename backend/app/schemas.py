from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# ---------- Project Schemas ----------

class ProjectCreate(BaseModel):
    name: str
    retention_days: Optional[int] = 90


class ProjectResponse(BaseModel):
    id: int
    name: str
    api_key: str
    retention_days: int
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Span Schemas ----------

class SpanCreate(BaseModel):
    span_type: str
    name: str
    input_json: Optional[str] = None
    output_json: Optional[str] = None
    status: Optional[str] = "success"
    latency_ms: Optional[int] = None
    error_message: Optional[str] = None
    parent_span_id: Optional[int] = None
    trace_id: Optional[str] = None
    host: Optional[str] = None
    pid: Optional[int] = None
    meta_json: Optional[str] = None


class SpanResponse(BaseModel):
    id: int
    run_id: int
    span_type: str
    name: str
    input_json: Optional[str] = None
    output_json: Optional[str] = None
    status: str
    latency_ms: Optional[int] = None
    error_message: Optional[str] = None
    parent_span_id: Optional[int] = None
    trace_id: Optional[str] = None
    host: Optional[str] = None
    pid: Optional[int] = None
    meta_json: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Run Schemas ----------

class RunCreate(BaseModel):
    project_id: Optional[int] = None
    run_name: str
    input_text: Optional[str] = None
    model: Optional[str] = None
    trace_id: Optional[str] = None
    host: Optional[str] = None
    pid: Optional[int] = None
    meta_json: Optional[str] = None


class RunComplete(BaseModel):
    output_text: Optional[str] = None
    status: Optional[str] = "success"
    latency_ms: Optional[int] = None
    cost_usd: Optional[str] = None


class RunResponse(BaseModel):
    id: int
    project_id: int
    run_name: str
    input_text: Optional[str] = None
    output_text: Optional[str] = None
    status: str
    model: Optional[str] = None
    latency_ms: Optional[int] = None
    cost_usd: Optional[str] = None
    trace_id: Optional[str] = None
    host: Optional[str] = None
    pid: Optional[int] = None
    meta_json: Optional[str] = None
    latest_evaluation_label: Optional[str] = None
    latest_evaluation_score: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class EvaluationResponse(BaseModel):
    id: int
    run_id: int
    score: int
    label: str
    reason: Optional[str] = None
    has_error: str
    latency_warning: str
    tool_failure: str
    empty_output: str
    created_at: datetime

    class Config:
        from_attributes = True


class RunDetailResponse(RunResponse):
    spans: List[SpanResponse] = []
    evaluations: List[EvaluationResponse] = []