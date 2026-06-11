import requests
import threading
from typing import Optional, Callable

from agentwatch.tracing import TraceRun
from agentwatch.sender import Sender


class AgentWatch:
    def __init__(
        self,
        api_key: str,
        project_id: int,
        base_url: str = "http://127.0.0.1:8000",
        async_send: bool = False,
        pii_redactor: Optional[Callable[[str], str]] = None
    ):
        self.api_key = api_key
        self.project_id = project_id
        self.base_url = base_url.rstrip("/")
        self._async = async_send
        self._pii_redactor = pii_redactor

        # optional background sender
        self._sender: Optional[Sender] = None
        if self._async:
            self._sender = Sender(base_url=self.base_url, headers=self._headers())

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
        model: Optional[str] = None,
        trace_id: Optional[str] = None,
        host: Optional[str] = None,
        pid: Optional[int] = None,
        meta_json: Optional[dict] = None
    ):
        payload = {
            "project_id": self.project_id,
            "run_name": run_name,
            "input_text": input_text,
            "model": model,
            "trace_id": trace_id,
            "host": host,
            "pid": pid,
            "meta_json": meta_json
        }

        # always create the run synchronously so caller receives an ID
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
        error_message: Optional[str] = None,
        parent_span_id: Optional[int] = None,
        trace_id: Optional[str] = None,
        host: Optional[str] = None,
        pid: Optional[int] = None,
        meta_json: Optional[dict] = None
    ):
        payload = {
            "span_type": span_type,
            "name": name,
            "input_json": input_json,
            "output_json": output_json,
            "status": status,
            "latency_ms": latency_ms,
            "error_message": error_message,
            "parent_span_id": parent_span_id,
            "trace_id": trace_id,
            "host": host,
            "pid": pid,
            "meta_json": meta_json
        }

        # apply PII redaction if provided and payload is text
        if self._pii_redactor is not None:
            if isinstance(payload.get("input_json"), str):
                try:
                    payload["input_json"] = self._pii_redactor(payload["input_json"])
                except Exception:
                    pass
            if isinstance(payload.get("output_json"), str):
                try:
                    payload["output_json"] = self._pii_redactor(payload["output_json"])
                except Exception:
                    pass

        if self._async and self._sender:
            return self._sender.post(f"/runs/{run_id}/spans", json=payload)

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

        if self._async and self._sender:
            return self._sender.patch(f"/runs/{run_id}/complete", json=payload)

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