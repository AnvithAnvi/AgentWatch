# AgentWatch — AI Agent Observability & Evaluation Dashboard

A lightweight, end-to-end observability platform for AI agents. Monitor agent execution, capture runtime metadata, log execution steps, and automatically evaluate performance — all with a simple Python SDK and clean web dashboard.

**Perfect for:** developers building agentic systems who need visibility into execution, debugging tools, and quality metrics.

## Why AgentWatch?

Building reliable AI agents requires observability. AgentWatch provides:

- **Complete Visibility** — See every step of agent execution, inputs, outputs, latency
- **Automatic Quality Scoring** — Rule-based evaluation assigns pass/warning/fail status
- **Error Tracking** — Track error propagation through execution steps
- **Minimal Setup** — Wrap your agent in one context manager, add 1-2 lines per step
- **No Configuration** — Works locally; zero deployment complexity

## Key Features

✅ **Python SDK** — Lightweight instrumentation with context managers  
✅ **Real-time Dashboard** — Web UI for runs list, detailed workflows, error analysis  
✅ **Automatic Metadata Capture** — Host, PID, trace IDs collected automatically  
✅ **Error Propagation Tracking** — See which steps cascade failures downstream  
✅ **Rule-Based Evaluation** — Pass/warning/fail scoring based on errors, latency, output  
✅ **REST API** — Direct access to runs, spans, evaluations, projects  
✅ **Local First** — SQLite backend; no external dependencies required  

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend   | FastAPI (Python 3.11+) |
| Database  | SQLite + SQLAlchemy ORM |
| Frontend  | React 19 + Vite 8 |
| Backend   | FastAPI (Python 3.11+) |
| Database  | SQLite + SQLAlchemy ORM |
| Frontend  | React 19 + Vite 8 |
| SDK       | Python `requests` library |


---

## 🚀 Getting Started (5 Minutes)

### Installation

**Prerequisites:** Python 3.11+ and Node.js 18+

#### 1. Clone & Install SDK

```bash
git clone https://github.com/AnvithAnvi/AgentWatch.git
cd AgentWatch

# Install Python SDK locally
cd sdk
pip install -e .
cd ..
```

#### 2. Start Backend (Terminal A)

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies and start server
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8001
```

Check health: Open `http://127.0.0.1:8001/docs` in your browser for API documentation.

#### 3. Start Frontend (Terminal B)

```bash
cd frontend
npm install
npm run dev
```

**Expected output:**
```
VITE v8.x.x  ready in xxx ms

➜  Local: http://127.0.0.1:5173/
```

Open `http://127.0.0.1:5173` in your browser.

#### 4. Verify Everything Works

In a new terminal, run:

```python
python3 << 'EOF'
from agentwatch import AgentWatch

# Test basic connectivity
aw = AgentWatch(
    api_key="test-key",
    project_id=1,
    base_url="http://127.0.0.1:8001"
)

with aw.trace(
    run_name="hello-world",
    input_text="Testing AgentWatch",
    model="test"
) as run:
    run.log_span(
        span_type="llm_call",
        name="test_step",
        input_data={"test": True},
        output_data={"result": "success"},
        latency_ms=100
    )
    run.set_output("Test completed successfully!")

print("✅ AgentWatch is working!")
EOF
```

Then check the dashboard at `http://127.0.0.1:5173` — you should see your test run!

---

## 📊 Using the Dashboard

### Runs List Page

The main dashboard shows all agent runs with key metrics:

**Columns:**
- **Run Name** — Identifier for the run
- **Model** — LLM model used (e.g., "gpt-4", "claude-3")
- **Status** — Current status (running/completed)
- **Evaluation** — Pass ✅ / Warning ⚠️ / Fail ❌
- **Latency** — Total execution time
- **Input** — First 50 chars of input text
- **Created** — When the run was created

**Actions:**
- Click any row to view detailed workflow
- Runs appear in reverse chronological order (newest first)
- Refresh shows latest runs immediately

### Run Detail Page

Shows complete execution trace with workflow visualization.

**Sections:**

#### 1. **Metadata Bar** (top)
- Run name, status, creation time
- Model and evaluation badge
- Total latency and span count

#### 2. **Input/Output Section**
- Full input text (what was sent to agent)
- Full output text (final result)
- Useful for comparing expected vs. actual behavior

#### 3. **Workflow Visualization** (center)
Visual diagram of execution flow:

```
① intent_classification ✅ [250ms]
   ↓
② lookup_customer_order ✅ [150ms]
   ↓
③ process_refund ❌ [5000ms]  ← ERROR
   Error: Payment gateway timeout
   ↓
④ fallback_notification ⚠️ [800ms]  ← PERSISTENT ERROR
   (highlighted in yellow — impacted by upstream failure)
```

**Color meanings:**
- 🟢 **Green** — Span completed successfully
- 🔴 **Red** — Span failed with error
- 🟡 **Yellow** — Span after an error (persistent failure path)

#### 4. **Evaluation Breakdown**
Shows scoring details:
```
Base Score: 100
- Error penalty (span 3): -30
- Latency penalty: -15
Final Score: 55 → ⚠️ WARNING
```

#### 5. **Spans Table**
Expandable list of all execution steps:
- Span name and type (llm_call, tool_call, etc.)
- Status (success/error)
- Latency in milliseconds
- Input/output JSON (click to expand)
- Error message (if failed)

---

## 🛠️ SDK User Guide

### Basic Setup

Import and initialize AgentWatch:

```python
from agentwatch import AgentWatch

# Initialize with your API key and backend URL
aw = AgentWatch(
    api_key="your-api-key",           # Can be any string for local testing
    project_id=1,                      # Project ID from dashboard
    base_url="http://127.0.0.1:8001"  # Backend URL
)
```

### Creating Your First Run

Wrap agent execution in a trace context manager:

```python
with aw.trace(
    run_name="customer-support",       # Identifier for this run
    input_text="I need help with...",  # User input
    model="gpt-4"                       # Model name
) as run:
    # Your agent logic here
    
    # Log each step (see below)
    run.log_span(...)
    
    # Set final output
    run.set_output("Response to user")
```

**When you use `.trace()`:**
- Backend creates a run record immediately
- Metadata (host, PID, trace ID) is captured automatically
- A unique `run_id` is assigned
- Timer starts for latency measurement

### Logging Execution Steps

Log each step as a **span**:

```python
run.log_span(
    span_type="llm_call",              # Type: llm_call, tool_call, or error
    name="extract_intent",              # Step identifier
    input_data={"text": "..."},         # What was sent to this step
    output_data={"intent": "refund"},   # What this step returned
    latency_ms=234,                     # How long it took
    status="success"                    # Optional: success/error (default: success)
)
```

**Span Types:**

| Type | Use Case | Example |
|------|----------|---------|
| `llm_call` | LLM inference | ChatGPT, Claude, Ollama calls |
| `tool_call` | External API/function | Database lookup, API request, file I/O |
| `error` | Error handling logic | Retry logic, fallback handlers |

### Handling Errors

When a step fails, mark it as an error:

```python
try:
    result = api.fetch_order(order_id)
except ApiError as e:
    run.log_span(
        span_type="tool_call",
        name="fetch_order",
        input_data={"order_id": order_id},
        output_data={},
        status="error",                    # Mark as error
        error_message=str(e),              # Error details
        latency_ms=elapsed_time
    )
    # Continue with fallback logic...
```

**Dashboard Effect:**
- Span marked red on workflow
- All subsequent spans highlighted yellow (persistent error)
- Run score reduced by 30 points
- Run evaluation may become "fail" if score < 50

### Complete Example: Simple Agent

```python
from agentwatch import AgentWatch
import time

aw = AgentWatch(
    api_key="demo-key",
    project_id=1,
    base_url="http://127.0.0.1:8001"
)

def refund_agent(customer_id: str, reason: str):
    """Determine if customer qualifies for refund."""
    
    with aw.trace(
        run_name=f"refund-check-{customer_id}",
        input_text=reason,
        model="gpt-4"
    ) as run:
        
        # Step 1: Classify refund request
        start = time.time()
        intent = classify_intent(reason)
        run.log_span(
            span_type="llm_call",
            name="classify_request",
            input_data={"reason": reason},
            output_data={"intent": intent},
            latency_ms=int((time.time() - start) * 1000)
        )
        
        # Step 2: Look up customer order
        start = time.time()
        try:
            order = lookup_order(customer_id)
            run.log_span(
                span_type="tool_call",
                name="fetch_customer_order",
                input_data={"customer_id": customer_id},
                output_data={"order_id": order["id"], "status": order["status"]},
                latency_ms=int((time.time() - start) * 1000)
            )
        except Exception as e:
            run.log_span(
                span_type="tool_call",
                name="fetch_customer_order",
                input_data={"customer_id": customer_id},
                output_data={},
                status="error",
                error_message=str(e),
                latency_ms=int((time.time() - start) * 1000)
            )
            run.set_output("Unable to fetch order. Please contact support.")
            return
        
        # Step 3: Make refund decision
        start = time.time()
        decision = make_decision(order, intent)
        run.log_span(
            span_type="llm_call",
            name="make_decision",
            input_data={"order": order, "intent": intent},
            output_data={"decision": decision},
            latency_ms=int((time.time() - start) * 1000)
        )
        
        # Set final output
        run.set_output(f"Refund Decision: {decision}")
        return decision

# Usage
refund_agent("CUST-123", "Item arrived damaged")
```

---

## 📋 Common Use Cases

### 1. LLM Chain Tracing

Track multi-step LLM workflows:

```python
with aw.trace(run_name="research-synthesis", input_text=query, model="gpt-4") as run:
    # Step 1: Retrieve relevant docs
    docs = retrieve_documents(query)
    
    # Step 2: Summarize each document
    for i, doc in enumerate(docs):
        summary = llm.summarize(doc)
        run.log_span(
            span_type="llm_call",
            name=f"summarize_doc_{i}",
            input_data={"text": doc[:200]},
            output_data={"summary": summary[:200]},
            latency_ms=timing()
        )
    
    # Step 3: Synthesize final answer
    final_answer = llm.synthesize([...])
    run.set_output(final_answer)
```

### 2. Tool-Use Agent (ReAct Pattern)

Track agent reasoning loop:

```python
with aw.trace(run_name="react-agent", input_text=goal, model="gpt-4") as run:
    for step_num in range(max_steps):
        # Reasoning
        thought, action = agent.think(history)
        
        # Tool use
        result = use_tool(action)
        run.log_span(
            span_type="tool_call",
            name=f"tool_step_{step_num}",
            input_data={"action": action},
            output_data={"result": result},
            latency_ms=elapsed
        )
        
        if is_final(result):
            run.set_output(result)
            break
```

### 3. Agentic RAG

Track retrieval and generation:

```python
with aw.trace(run_name="rag-query", input_text=question, model="claude-3") as run:
    # Retrieval
    start = time.time()
    chunks = vector_db.search(question, top_k=5)
    retrieval_time = time.time() - start
    
    run.log_span(
        span_type="tool_call",
        name="vector_search",
        input_data={"query": question, "top_k": 5},
        output_data={"chunks_retrieved": len(chunks)},
        latency_ms=int(retrieval_time * 1000)
    )
    
    # Generation
    start = time.time()
    answer = llm.generate(question, chunks)
    generation_time = time.time() - start
    
    run.log_span(
        span_type="llm_call",
        name="generate_answer",
        input_data={"context": "..."},
        output_data={"answer": answer[:200]},
        latency_ms=int(generation_time * 1000)
    )
    
    run.set_output(answer)
```

---

## ❓ Troubleshooting & FAQ

### Q: Backend won't start — "Address already in use"
**A:** Another process is using port 8001.
```bash
# Find what's using port 8001
lsof -i :8001

# Kill the process
kill -9 <PID>

# Or use a different port
python -m uvicorn app.main:app --host 127.0.0.1 --port 8002
```

### Q: Frontend can't connect to backend
**A:** Check that backend is running and CORS is enabled.
```bash
# Verify backend health
curl http://127.0.0.1:8001/docs

# Check frontend environment
cat frontend/.env
```

### Q: Spans not appearing in dashboard
**A:** Verify the run is completed (context manager exited).
```python
with aw.trace(...) as run:
    run.log_span(...)
# Spans sent when exiting context manager
```

### Q: SDK gives "Connection refused"
**A:** Backend URL is incorrect or backend isn't running.
```python
# Verify correct URL and port
aw = AgentWatch(
    api_key="test-key",
    project_id=1,
    base_url="http://127.0.0.1:8001"  # Not 8000!
)
```

### Q: Evaluations seem wrong — my successful run shows "fail"
**A:** Check penalties applied:
- Error span: -30 points
- Latency > 2s: -15 points
- Empty output: -40 points
- Score < 50: marked "fail"

See run details to view breakdown.

### Q: Can I use AgentWatch in production?
**A:** Currently local-only (SQLite). Upcoming features: PostgreSQL, containerization, hosted option. For production, consider exporting runs to persistent storage.

---

## 💡 Best Practices

### 1. Granular Span Names
❌ Bad: `run.log_span(span_type="llm_call", name="step1")`  
✅ Good: `run.log_span(span_type="llm_call", name="classify_sentiment")`

Clear names make workflows easier to understand in the dashboard.

### 2. Include Relevant Context in I/O
```python
run.log_span(
    span_type="llm_call",
    name="summarize_document",
    input_data={
        "doc_id": doc.id,
        "text_preview": doc.text[:200],
        "language": doc.language
    },
    output_data={
        "summary": summary,
        "confidence": confidence_score
    },
    latency_ms=elapsed
)
```

This helps debugging without re-running the agent.

### 3. Always Set Final Output
```python
run.set_output("Your agent's final response")
```

Missing output penalizes evaluation score by 40 points.

### 4. Measure Latency Accurately
```python
import time
start = time.time()
result = expensive_operation()
latency_ms = int((time.time() - start) * 1000)

run.log_span(..., latency_ms=latency_ms)
```

### 5. Mark Errors Explicitly
```python
try:
    result = risky_operation()
except Exception as e:
    run.log_span(
        ...,
        status="error",
        error_message=str(e)
    )
```

This helps identify failure patterns.

---

## 🔌 API Reference

All operations via HTTP. Authentication: Bearer token in `Authorization` header.

### List Runs
```bash
GET http://127.0.0.1:8001/runs/

# Response
[
  {
    "id": 1,
    "project_id": 1,
    "run_name": "refund-check",
    "model": "gpt-4",
    "status": "completed",
    "evaluation": "pass",
    "latency_ms": 1234,
    "created_at": "2025-01-15T10:30:00Z"
  }
]
```

### Get Run Details
```bash
GET http://127.0.0.1:8001/runs/1

# Response
{
  "id": 1,
  "run_name": "refund-check",
  "input_text": "I need a refund",
  "output_text": "Refund approved",
  "evaluation": {
    "score": 85,
    "label": "pass",
    "has_error": false,
    "tool_failure": false,
    "latency_warning": false,
    "empty_output": false
  },
  "spans": [
    {
      "id": 1,
      "span_type": "llm_call",
      "name": "classify_intent",
      "status": "success",
      "latency_ms": 250,
      "input_data": {...},
      "output_data": {...}
    }
  ]
}
```

### Create Project
```bash
POST http://127.0.0.1:8001/projects/
Content-Type: application/json

{
  "name": "my-project",
  "retention_days": 90
}

# Response
{
  "id": 1,
  "name": "my-project",
  "api_key": "proj_xxx...",
  "retention_days": 90
}
```

---

## 🏗️ How It Works (Technical Deep Dive)

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

---

## 🏛️ Architecture

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
