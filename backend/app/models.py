from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    api_key = Column(String, unique=True, index=True, nullable=False)
    retention_days = Column(Integer, default=90)
    created_at = Column(DateTime, default=datetime.utcnow)

    runs = relationship("Run", back_populates="project")

class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("runs.id"), nullable=False)

    score = Column(Integer, nullable=False)
    label = Column(String, nullable=False)
    meta_json = Column("metadata", Text, nullable=True)

    has_error = Column(String, default="false")
    latency_warning = Column(String, default="false")
    tool_failure = Column(String, default="false")
    empty_output = Column(String, default="false")

    created_at = Column(DateTime, default=datetime.utcnow)

    run = relationship("Run", back_populates="evaluations")

class Run(Base):
    __tablename__ = "runs"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    run_name = Column(String, nullable=False)
    input_text = Column(Text, nullable=True)
    output_text = Column(Text, nullable=True)
    status = Column(String, default="running")
    model = Column(String, nullable=True)
    latency_ms = Column(Integer, nullable=True)
    cost_usd = Column(String, nullable=True)
    trace_id = Column(String, nullable=True)
    host = Column(String, nullable=True)
    pid = Column(Integer, nullable=True)
    meta_json = Column("metadata", Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="runs")
    spans = relationship("Span", back_populates="run")
    evaluations = relationship("Evaluation", back_populates="run")


class Span(Base):
    __tablename__ = "spans"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("runs.id"), nullable=False)

    span_type = Column(String, nullable=False)
    name = Column(String, nullable=False)

    input_json = Column(Text, nullable=True)
    output_json = Column(Text, nullable=True)

    status = Column(String, default="success")
    latency_ms = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    parent_span_id = Column(Integer, nullable=True)
    trace_id = Column(String, nullable=True)
    host = Column(String, nullable=True)
    pid = Column(Integer, nullable=True)
    meta_json = Column("metadata", Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    run = relationship("Run", back_populates="spans")