import json
import time
import os
import socket
import uuid
import functools
import traceback
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
        self._meta = None

    def __enter__(self):
        self.start_time = time.time()
        # capture basic host/process metadata for this run before creating it
        self._meta = self._collect_runtime_metadata()

        run = self.client.create_run(
            run_name=self.run_name,
            input_text=self.input_text,
            model=self.model,
            trace_id=self._meta.get("trace_id"),
            host=self._meta.get("host"),
            pid=self._meta.get("pid"),
            meta_json=json.dumps(self._meta)
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
        def safe_serialize(obj):
            try:
                return json.dumps(obj)
            except Exception:
                try:
                    return json.dumps({"repr": repr(obj)})
                except Exception:
                    return json.dumps({"error": "unserializable"})

        input_json = safe_serialize(input_data) if input_data is not None else None
        output_json = safe_serialize(output_data) if output_data is not None else None

        return self.client.create_span(
            run_id=self.run_id,
            span_type=span_type,
            name=name,
            input_json=input_json,
            output_json=output_json,
            status=status,
            latency_ms=latency_ms,
            error_message=error_message,
            trace_id=self._meta.get("trace_id"),
            host=self._meta.get("host"),
            pid=self._meta.get("pid"),
             meta_json=self._meta

    def _collect_runtime_metadata(self) -> Dict[str, Any]:
        meta = {
            "trace_id": uuid.uuid4().hex,
            "host": None,
            "pid": None,
            "timestamp": int(time.time() * 1000)
        }
        try:
            meta["host"] = socket.gethostname()
        except Exception:
            meta["host"] = None

        try:
            meta["pid"] = os.getpid()
        except Exception:
            meta["pid"] = None

        # try to include lightweight resource usage if available
        try:
            import psutil

            p = psutil.Process()
            with p.oneshot():
                meta["cpu_percent"] = p.cpu_percent(interval=None)
                mem = p.memory_info()
                meta["rss_bytes"] = getattr(mem, "rss", None)
                meta["vms_bytes"] = getattr(mem, "vms", None)
        except Exception:
            # psutil is optional; ignore if not installed
            pass

        return meta

    def instrument(self, name: Optional[str] = None, span_type: str = "tool_call"):
        """Return a decorator that auto-logs the wrapped function as a span.

        Usage:
            @run.instrument("lookup_order", span_type="tool_call")
            def lookup_order(...):
                ...
        """
        def decorator(fn):
            span_name = name or fn.__name__

            @functools.wraps(fn)
            def wrapper(*args, **kwargs):
                start = time.time()
                input_data = {"args": args, "kwargs": kwargs}
                try:
                    result = fn(*args, **kwargs)
                    latency_ms = int((time.time() - start) * 1000)
                    try:
                        output_data = {"result": result}
                    except Exception:
                        output_data = {"result_repr": repr(result)}

                    self.log_span(
                        span_type=span_type,
                        name=span_name,
                        input_data=input_data,
                        output_data=output_data,
                        status="success",
                        latency_ms=latency_ms
                    )
                    return result
                except Exception as e:
                    latency_ms = int((time.time() - start) * 1000)
                    err = {
                        "type": type(e).__name__,
                        "message": str(e),
                        "traceback": traceback.format_exc()
                    }
                    self.log_span(
                        span_type=span_type,
                        name=span_name,
                        input_data=input_data,
                        output_data=None,
                        status="error",
                        latency_ms=latency_ms,
                        error_message=str(e)
                    )
                    raise

            return wrapper

        return decorator