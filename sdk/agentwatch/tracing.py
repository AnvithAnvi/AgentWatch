import json
import time
from typing import Optional, Dict, Any


class TraceRun:
    def __init__(
        self,
        client,
        run_name: str,
        input_text: Optional[str] = None,
        model: Optional[str] = None
    ):
        self.client = client
        self.run_name = run_name
        self.input_text = input_text
        self.model = model

        self.run_id = None
        self.start_time = None
        self.output_text = None
        self.status = "success"

    def __enter__(self):
        self.start_time = time.time()

        run = self.client.create_run(
            run_name=self.run_name,
            input_text=self.input_text,
            model=self.model
        )

        self.run_id = run["id"]
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        latency_ms = int((time.time() - self.start_time) * 1000)

        if exc_type is not None:
            self.status = "error"
            self.output_text = str(exc_value)

            self.log_span(
                span_type="error",
                name="unhandled_exception",
                input_data=None,
                output_data=None,
                status="error",
                error_message=str(exc_value)
            )

        self.client.complete_run(
            run_id=self.run_id,
            output_text=self.output_text,
            status=self.status,
            latency_ms=latency_ms,
            cost_usd=None
        )

        # Returning False allows Python to still raise the exception.
        return False

    def log_span(
        self,
        span_type: str,
        name: str,
        input_data: Optional[Dict[str, Any]] = None,
        output_data: Optional[Dict[str, Any]] = None,
        status: str = "success",
        latency_ms: Optional[int] = None,
        error_message: Optional[str] = None
    ):
        input_json = json.dumps(input_data) if input_data is not None else None
        output_json = json.dumps(output_data) if output_data is not None else None

        return self.client.create_span(
            run_id=self.run_id,
            span_type=span_type,
            name=name,
            input_json=input_json,
            output_json=output_json,
            status=status,
            latency_ms=latency_ms,
            error_message=error_message
        )

    def set_output(self, output_text: str):
        self.output_text = output_text