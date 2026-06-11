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

## Screenshots

### Runs Dashboard

![Runs Dashboard](screenshots/runs-list.png)

### Run Detail

![Run Detail](screenshots/run-detail.png)

## Tech Stack

- Backend: FastAPI
- Database: SQLite, SQLAlchemy
- Frontend: React, Vite
- SDK: Python
- HTTP client: `requests`


## Quick Start

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

### Step 4: Run Demo Agent (new terminal)

From the repository root:

```bash
python examples/refund_agent/demo.py
```

This creates four demo agent runs:

- ✅ **successful run** — completes successfully
- ⚠️ **slow run** — takes >3 seconds (triggers latency warning)
- ❌ **tool failure run** — tool call fails
- ⚠️ **empty output run** — agent produces no output

Each run is immediately visible in the dashboard with evaluation results and workflow visualization.

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

## Key Features

### Workflow Visualization

The run detail page displays a **workflow diagram** showing:
- Each span as an ordered workflow step
- Error markers for failed steps
- Persistent error highlighting for downstream steps after a failure
- Error start/persistent error path indicators

### Automatic Evaluation

AgentWatch runs a rule-based evaluator on each completed run. Starting from a score of 100, penalties are applied:

- Span error: -30 points
- Tool failure: -25 points
- Latency warning (>2 sec): -15 points
- Empty output: -40 points

Final labels:
- **pass** (score ≥ 80)
- **warning** (score 50-79)
- **fail** (score < 50)

### Metrics Tracked

- `has_error` — any span failed
- `tool_failure` — tool/function call failed
- `latency_warning` — run exceeded 2-second threshold
- `empty_output` — agent produced no output

## Instrumenting Your Agent

### Basic Setup

```python
from agentwatch import AgentWatch

# Initialize with your project API key
aw = AgentWatch(
    api_key="your-api-key",
    project_id=1,
    base_url="http://127.0.0.1:8001"  # Point to backend
)
```

### Trace a Run

```python
with aw.trace(
    run_name="my-agent-run",
    input_text="User input here",
    model="gpt-4"
) as run:
    # Log spans for each step
    run.log_span(
        span_type="llm_call",
        name="step_name",
        input_data={...},
        output_data={...},
        latency_ms=200
    )
    
    # Set final output
    run.set_output("Agent output")
```

### Span Types

- `llm_call` — LLM inference
- `tool_call` — External function/API call
- `error` — Error handling

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
