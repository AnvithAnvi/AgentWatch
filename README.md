
# AgentWatch

AgentWatch is a small observability and demo framework for instrumenting, storing, and evaluating agent traces (runs and spans). It includes a FastAPI backend, a React frontend, and a Python SDK for instrumenting demo agents.

**Key features**
- **Trace storage:** Persist runs and spans using SQLAlchemy (SQLite by default).
- **Rule-based evaluations:** Evaluate completed runs and attach pass/warning/fail labels and scores.
- **Frontend dashboard:** Browse projects, runs, and detailed span timelines.
- **SDK & demos:** Lightweight Python SDK and example agents to generate realistic success/failure/slow runs.

**Quick links**
- Backend: `backend/`
- Frontend: `frontend/`
- SDK: `sdk/agentwatch`
- Examples: `examples/refund_agent`

**Prerequisites**
- Python 3.10+ and `pip` (backend & SDK)
- Node.js 18+ and `npm` (frontend)

**Setup — Backend**
1. Create and activate a virtualenv:

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Start the FastAPI server (development):

```bash
uvicorn app.main:app --reload
```

3. (Optional) Reset the database:

```bash
rm backend/agentwatch.db
# restart the server after removing the DB
```

**Setup — Frontend**
1. Install and run the dev server:

```bash
cd frontend
npm install
npm run dev
```

2. Build for production:

```bash
npm run build
```

**Run the demo agents**
1. With the backend running, generate demo runs:

```bash
python examples/refund_agent/demo.py
```

2. Inspect runs via the API:

```bash
curl http://127.0.0.1:8000/runs/ | jq
```

Open the frontend and view run details to see evaluations and span timelines.

**Developer notes**
- Evaluations are stored in the `Evaluation` model and the latest evaluation is attached to run responses.
- Span rendering UI lives under `frontend/components/SpanCard.jsx`.
- If the backend process is killed by the OS (exit code 137), restart `uvicorn` and ensure your system has enough memory.

**Adding new demos**
- Place new demo scripts in `examples/` and use the SDK (`sdk/agentwatch/tracing.py`) to create `TraceRun` contexts that record spans and metrics.

**Contributing**
- Open issues and PRs are welcome. Keep changes focused and run the frontend build and backend lint before submitting.

---

See the code and usage examples in the repository root and the specific folders above. For details, open the project files (for example, [README.md](README.md)).

## Table of contents

- Overview
- Quick Start
- API Reference (examples)
- Data schemas (summary)
- Frontend
- SDK & Examples
- Troubleshooting
- Contributing

## Quick Start (recap)

1. Start the backend:

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

2. Start the frontend (dev):

```bash
cd frontend
npm install
npm run dev
```

3. Generate demo runs:

```bash
python examples/refund_agent/demo.py
```

4. Inspect runs via API:

```bash
curl http://127.0.0.1:8000/runs/ | jq
```

## Screenshots

Runs list (shows latest evaluation and latency):

![Runs list](screenshots/runs-list.png)

Run detail (span timeline, failure highlighting, and pretty JSON):

![Run detail](screenshots/run-detail.png)


## API Reference (examples)

These are quick examples to interact with the running backend. Replace `127.0.0.1:8000` with your host/port.

- List projects

```bash
curl http://127.0.0.1:8000/projects/
```

- Create a project

```bash
curl -X POST http://127.0.0.1:8000/projects/ -H "Content-Type: application/json" -d '{"name":"refund-agent"}'
```

- List runs (includes latest evaluation summary)

```bash
curl http://127.0.0.1:8000/runs/ | jq
```

- Get run detail (includes spans and evaluations)

```bash
curl http://127.0.0.1:8000/runs/<RUN_ID>/ | jq
```

## Data schemas (summary)

The backend exposes run, span, and evaluation objects. Below are the most important fields to know when consuming the API.

- `Run` (partial)
	- `id`: string
	- `project_id`: string
	- `status`: `running` | `completed` | `failed`
	- `latency_ms`: integer (ms)
	- `spans`: array of `Span` objects
	- `latest_evaluation_label`: `pass` | `warning` | `fail` (attached to list responses)
	- `latest_evaluation_score`: integer (0-100)

- `Span` (partial)
	- `id`: string
	- `name`: human-readable name
	- `span_type`: e.g. `llm_call` | `tool_call`
	- `status`: `success` | `error` | `running`
	- `latency_ms`: integer
	- `input_json` / `output_json`: strings (JSON)
	- `error_message`: optional string

- `Evaluation` (partial)
	- `id`: string
	- `run_id`: string
	- `score`: integer 0-100
	- `label`: `pass` | `warning` | `fail`
	- `flags`: array of strings describing triggered checks (e.g. `latency_warning`, `empty_output`)

## Frontend

- UI entry: open `frontend/` and run the dev server. The run list shows `latest_evaluation_label` and `latest_evaluation_score` alongside runs.
- Run details live on the `RunDetailPage` and render spans with `frontend/components/SpanCard.jsx`.
- Styling is in `frontend/src/App.css`.

## SDK & Examples

- The lightweight SDK is located at `sdk/agentwatch` and provides `TraceRun` context manager to record spans and run metadata.
- Example demo agent(s) live in `examples/refund_agent/demo.py`. They create runs that showcase different evaluator outcomes: successful, slow (latency warning), tool failure, and empty output.

## Troubleshooting

- Backend killed with exit code 137: this typically indicates the OS killed the process (OOM or resource constraints). Try:

```bash
# run without the auto-reloader or restart the process
uvicorn app.main:app

# or ensure the system has available memory and restart
```

- Frontend build issues: run `npm run build` in `frontend/` to reproduce production build errors; check the console output for missing imports or CSS typos.

- DB reset: delete `backend/agentwatch.db` to start clean, then restart the backend.

## Contributing

- Keep changes small and focused. Run the frontend build and perform a quick syntax check on backend scripts before creating a PR:

```bash
cd frontend && npm run build
python -m py_compile backend/app/services/evaluator.py
```

If you want, I can add more detailed API docs, example responses, or Postman/Insomnia collections — tell me which you'd prefer and I'll add them.


## Current Features

- FastAPI backend
- SQLite database
- Python SDK
- React dashboard
- Trace timeline
- Rule-based evaluations
- Demo refund agent with success/failure scenarios

## Run Backend

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

## Run Frontend

```bash
cd frontend
npm run dev
```

## Run Demo Agent

```bash
python examples/refund_agent/demo.py
```
