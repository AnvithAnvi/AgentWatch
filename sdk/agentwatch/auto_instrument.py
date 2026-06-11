"""Simple auto-instrumentation helpers to patch common libraries.

This module provides opt-in patching for `requests` and `subprocess` to auto-log
spans when used inside a `TraceRun`.
"""
import requests
import subprocess
import functools
from typing import Callable, Optional


def patch_requests(trace_getter: Callable[[], Optional[object]]):
    """Patch `requests.Session.request` to log spans when a TraceRun is active.

    `trace_getter` should return the current `TraceRun` or None.
    Returns an undo function to restore the original method.
    """
    Session = requests.Session
    orig = Session.request

    def wrapped(self, method, url, *args, **kwargs):
        trace = trace_getter()
        start = None
        if trace:
            start = __import__("time").time()
        try:
            res = orig(self, method, url, *args, **kwargs)
            if trace and start is not None:
                trace.log_span(
                    span_type="http",
                    name=f"requests.{method}",
                    input_data={"url": url, "method": method, "args": args, "kwargs": kwargs},
                    output_data={"status_code": getattr(res, "status_code", None)},
                    status="success",
                    latency_ms=int((__import__("time").time() - start) * 1000)
                )
            return res
        except Exception as e:
            if trace and start is not None:
                trace.log_span(
                    span_type="http",
                    name=f"requests.{method}",
                    input_data={"url": url, "method": method, "args": args, "kwargs": kwargs},
                    output_data=None,
                    status="error",
                    latency_ms=int((__import__("time").time() - start) * 1000),
                    error_message=str(e)
                )
            raise

    Session.request = wrapped

    def undo():
        Session.request = orig

    return undo


def patch_subprocess_run(trace_getter: Callable[[], Optional[object]]):
    """Patch `subprocess.run` to log spans when a TraceRun is active.

    Returns an undo function to restore the original.
    """
    orig = subprocess.run

    def wrapped(*popenargs, **kwargs):
        trace = trace_getter()
        start = None
        if trace:
            start = __import__("time").time()
        try:
            res = orig(*popenargs, **kwargs)
            if trace and start is not None:
                trace.log_span(
                    span_type="tool_call",
                    name="subprocess.run",
                    input_data={"args": popenargs, "kwargs": kwargs},
                    output_data={"returncode": getattr(res, "returncode", None)},
                    status="success",
                    latency_ms=int((__import__("time").time() - start) * 1000)
                )
            return res
        except Exception as e:
            if trace and start is not None:
                trace.log_span(
                    span_type="tool_call",
                    name="subprocess.run",
                    input_data={"args": popenargs, "kwargs": kwargs},
                    output_data=None,
                    status="error",
                    latency_ms=int((__import__("time").time() - start) * 1000),
                    error_message=str(e)
                )
            raise

    subprocess.run = wrapped

    def undo():
        subprocess.run = orig

    return undo
