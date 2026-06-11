# AgentWatch

## Overview

AgentWatch is a lightweight observability dashboard for AI agents that helps developers trace runs, inspect tool calls, detect failures, measure latency, and evaluate execution quality.

## Why AgentWatch?

AgentWatch provides a compact end-to-end experience for building, testing, and reviewing agent workflows. It combines a FastAPI backend, Python SDK, React dashboard, and demo scenarios so teams can quickly demonstrate AI traceability and runtime quality checks.

## Features

- Python SDK for instrumenting agent workflows
- FastAPI backend for collecting runs and spans
- SQLite database with SQLAlchemy models
- React + Vite dashboard
- Run list with status, latency, and latest evaluation
- Run detail page with input, output, spans, and evaluation
- Span-level failure highlighting
- Rule-based pass / warning / fail evaluations
- Demo refund agent with success, slow, tool-failure, and empty-output scenarios

## Tech Stack

- Backend: FastAPI
- Database: SQLite, SQLAlchemy
- Frontend: React, Vite
- SDK: Python
- HTTP client: `requests`


## How It Works

AgentWatch provides end-to-end observability for AI agent execution with three main components working together:

### 1. **Agent Instrumentation (SDK)**

Your agent code uses the Python SDK to wrap execution within a **trace context**:

```python
from agentwatch import AgentWatch

aw = AgentWatch(
    api_key="your-api-key",
    project_id=1,
    base_url="http://127.0.0.1:8001"
)

with aw.trace(
    run_name="refund-decision",
    input_text="Customer request",
    model="gpt-4"
) as run:
    # Your agent logic here
    run.set_output("Final response")
```

When the context manager enters:
- A **run** is created on the backend (start time, model, input captured)
- Metadata is collected (host, process ID, trace ID for correlation)
- Backend assigns a unique `run_id`

### 2. **Span Logging During Execution**

Inside the trace, log each step as a **span**:

```python
run.log_span(
    span_type="llm_call",
    name="intent_classification",
    input_data={"text": "Can I get a refund?"},
    output_data={"intent": "refund_request"},
    latency_ms=250
)

run.log_span(
    span_type="tool_call",
    name="lookup_customer_order",
    input_data={"customer_id": "C123"},
    output_data={"order": {...}},
    latency_ms=150
)

# If something fails, mark it as an error
run.log_span(
    span_type="tool_call",
    name="process_refund",
    status="error",
    error_message="Payment gateway timeout",
    latency_ms=5000
)
```

Spans are sent **asynchronously** in batches to the backend:
- Each span includes timing, inputs/outputs, status, and error details
- Linked to the parent run by `run_id`
- Timestamped for ordering in the dashboard

### 3. **Run Completion & Evaluation**

When the context manager exits:

```python
run.set_output("Final answer for the user")
```

The backend:
- **Records completion** (end time, final output, overall status)
- **Calculates latency** (elapsed time from start to finish)
- **Runs evaluation logic** (see below)

### 4. **Automatic Evaluation**

AgentWatch evaluates completed runs against a scoring rubric:

**Starting score: 100 points**

Penalties applied automatically:
- Any span with `status="error"`: **-30 points**
- Span marked as tool failure: **-25 points**
- Run latency > 2 seconds: **-15 points**
- Empty or missing final output: **-40 points**

**Final labels assigned:**
- **pass** — score ≥ 80 (green) ✅
- **warning** — score 50-79 (yellow) ⚠️
- **fail** — score < 50 (red) ❌

### 5. **Dashboard Visualization**

The web dashboard displays:

**Runs List:**
- All runs in reverse chronological order
- Status badge (success/running)
- Latest evaluation (pass/warning/fail)
- Model, latency, cost metadata
- Quick links to detailed view

**Run Detail Page:**
- Input and output text
- **Workflow visualization** showing:
  - Each span as a numbered step in order
  - Success/error markers on each step
  - Error propagation highlighting (downstream steps after a failure highlighted in yellow)
  - Latency for each span
  - Error messages displayed inline
- Full evaluation breakdown
- All spans with input/output JSON

### 6. **Data Flow Summary**

```
Your Agent Code (Python)
    ↓
    │ .trace() context manager starts
    ↓
SDK creates Run on Backend ← HTTP POST /runs/
    ↓
    │ Agent executes, logs spans
    ├─ run.log_span(...) → queued locally
    ├─ run.log_span(...) → queued locally
    └─ async batch sends to backend ← HTTP POST /spans/ (batch)
    ↓
SDK calls run.set_output()
    ↓
Context exits → run completion signal ← HTTP PATCH /runs/{id}/complete
    ↓
Backend evaluates run (rule-based scoring)
    ↓
Dashboard fetches runs/details ← HTTP GET /runs/, /runs/{id}
    ↓
User views workflow, errors, and metrics in React UI
```

### 7. **Error Tracking Example**

If a span fails:

```python
run.log_span(
    span_type="tool_call",
    name="verify_order",
    status="error",
    error_message="Database connection lost",
    latency_ms=1200
)
```

The dashboard will:
1. Mark this span red (error indicator)
2. Highlight all **subsequent spans in yellow** (persistent error path)
3. Show the error message inline
4. Reduce run score by 30 points
5. Mark overall run as "fail" (if score < 50)
6. Display workflow showing where failure originated and impact


### Prerequisites

- Python 3.11+
- Node.js 18+
- pip and npm

### Step 1: Install SDK

From the repository root, install the AgentWatch SDK locally:

```bash
cd sdk
pip install -e .
cd ..
```

### Step 2: Start Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

✅ Backend running at: `http://127.0.0.1:8001`

Swagger docs: `http://127.0.0.1:8001/docs`

### Step 3: Start Frontend (new terminal)

```bash
cd frontend
npm install
npm run dev
```

✅ Frontend running at: `http://127.0.0.1:5173`

### Step 4: Instrument Your Agent

Now use the SDK in your agent code (see examples below).

## SDK Example

```python
from agentwatch import AgentWatch

aw = AgentWatch(
    api_key="demo-key",
    project_id=1,
    base_url="http://127.0.0.1:8000"
)

with aw.trace(
    run_name="refund-agent-test",
    input_text="Can I get a refund?",
    model="fake-llm-v1"
) as run:
    run.log_span(
        span_type="llm_call",
        name="classify_intent",
        input_data={"message": "Can I get a refund?"},
        output_data={"intent": "refund_request"},
        latency_ms=120
    )

    run.log_span(
        span_type="tool_call",
        name="lookup_order",
        input_data={"order_id": "ORD-123"},
        output_data={"status": "delivered"},
        latency_ms=80
    )

    run.set_output("The customer may be eligible for a refund.")
```

## API Endpoints

### List Runs
```bash
curl http://127.0.0.1:8001/runs/
```

### Get Run Details
```bash
curl http://127.0.0.1:8001/runs/1
```

### Create Project
```bash
curl -X POST http://127.0.0.1:8001/projects/ \
  -H "Content-Type: application/json" \
  -d '{"name":"my-project","retention_days":90}'
```

## Architecture

### Backend (FastAPI)
- RESTful API for creating runs, spans, and projects
- SQLite database with SQLAlchemy ORM
- Rule-based run evaluation service
- API key authentication per project

### Frontend (React + Vite)
- Runs dashboard with filtering and sorting
- Run detail page with workflow visualization
- Real-time error highlighting
- Automatic refresh support

### SDK (Python)
- `AgentWatch` client for API communication
- `TraceRun` context manager for run lifecycle
- Automatic host/PID/trace metadata capture
- Async background batch sender for spans

## Roadmap

- Docker Compose setup for easy deployment
- PostgreSQL support for scalability
- LangChain / LangGraph integration
- LLM-as-judge evaluations (Claude, GPT-4)
- Prompt versioning and tracking
- Export traces to JSON/CSV
- Webhook alerts for failed runs
- Hosted deployment option

## License

License details are available in the LICENSE file.

<!--
Recommended GitHub About:
Description: Lightweight monitoring and evaluation dashboard for AI agents.
Topics: ai-agents, llm, observability, fastapi, react, python-sdk, agent-monitoring, developer-tools
-->
