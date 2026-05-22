import requests
from typing import Optional

from agentwatch.tracing import TraceRun


class AgentWatch:
    def __init__(
        self,
        api_key: str,
        project_id: int,
        base_url: str = "http://127.0.0.1:8000"
    ):
        self.api_key = api_key
        self.project_id = project_id
        self.base_url = base_url.rstrip("/")

    def trace(
        self,
        run_name: str,
        input_text: Optional[str] = None,
        model: Optional[str] = None
    ):
        return TraceRun(
            client=self,
            run_name=run_name,
            input_text=input_text,
            model=model
        )

    def create_run(
        self,
        run_name: str,
        input_text: Optional[str] = None,
        model: Optional[str] = None
    ):
        payload = {
            "project_id": self.project_id,
            "run_name": run_name,
            "input_text": input_text,
            "model": model
        }

        response = requests.post(
            f"{self.base_url}/runs/",
            json=payload,
            headers=self._headers()
        )

        response.raise_for_status()
        return response.json()

    def create_span(
        self,
        run_id: int,
        span_type: str,
        name: str,
        input_json: Optional[str] = None,
        output_json: Optional[str] = None,
        status: str = "success",
        latency_ms: Optional[int] = None,
        error_message: Optional[str] = None
    ):
        payload = {
            "span_type": span_type,
            "name": name,
            "input_json": input_json,
            "output_json": output_json,
            "status": status,
            "latency_ms": latency_ms,
            "error_message": error_message
        }

        response = requests.post(
            f"{self.base_url}/runs/{run_id}/spans",
            json=payload,
            headers=self._headers()
        )

        response.raise_for_status()
        return response.json()

    def complete_run(
        self,
        run_id: int,
        output_text: Optional[str] = None,
        status: str = "success",
        latency_ms: Optional[int] = None,
        cost_usd: Optional[str] = None
    ):
        payload = {
            "output_text": output_text,
            "status": status,
            "latency_ms": latency_ms,
            "cost_usd": cost_usd
        }

        response = requests.patch(
            f"{self.base_url}/runs/{run_id}/complete",
            json=payload,
            headers=self._headers()
        )

        response.raise_for_status()
        return response.json()

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }