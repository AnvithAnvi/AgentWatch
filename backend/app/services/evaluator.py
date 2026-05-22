from app import models


def evaluate_run(run: models.Run):
    score = 100
    reasons = []

    has_error = any(span.status == "error" for span in run.spans)
    tool_failure = any(
        span.span_type == "tool_call" and span.status == "error"
        for span in run.spans
    )
    latency_warning = run.latency_ms is not None and run.latency_ms > 3000
    empty_output = not run.output_text or len(run.output_text.strip()) == 0

    if has_error:
        score -= 30
        reasons.append("One or more spans failed.")

    if tool_failure:
        score -= 25
        reasons.append("A tool call failed.")

    if latency_warning:
        score -= 15
        reasons.append("Run latency exceeded 3000 ms.")

    if empty_output:
        score -= 40
        reasons.append("Run returned an empty output.")

    score = max(score, 0)

    # Improved label logic: any serious flags should produce at least a warning.
    if has_error or tool_failure or empty_output:
        label = "fail" if score < 50 else "warning"
    elif latency_warning:
        label = "warning"
    else:
        label = "pass"

    if not reasons:
        reasons.append("Run completed successfully with no obvious issues.")

    return {
        "score": score,
        "label": label,
        "reason": " ".join(reasons),
        "has_error": str(has_error).lower(),
        "latency_warning": str(latency_warning).lower(),
        "tool_failure": str(tool_failure).lower(),
        "empty_output": str(empty_output).lower(),
    }
