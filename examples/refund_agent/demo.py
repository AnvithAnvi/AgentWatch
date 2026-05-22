import time

from agentwatch import AgentWatch

PROJECT_ID = 1
BASE_URL = "http://127.0.0.1:8000"

aw = AgentWatch(
    api_key="demo-key",
    project_id=PROJECT_ID,
    base_url=BASE_URL
)


def successful_refund_run():
    with aw.trace(
        run_name="refund-agent-successful-run",
        input_text="Can I get a refund for my order?",
        model="fake-llm-v1"
    ) as run:
        run.log_span(
            span_type="llm_call",
            name="classify_intent",
            input_data={"message": "Can I get a refund for my order?"},
            output_data={"intent": "refund_request"},
            latency_ms=120
        )

        run.log_span(
            span_type="tool_call",
            name="lookup_order",
            input_data={"order_id": "ORD-123"},
            output_data={"status": "delivered", "days_since_delivery": 12},
            latency_ms=80
        )

        run.log_span(
            span_type="tool_call",
            name="check_refund_policy",
            input_data={"days_since_delivery": 12, "policy": "refund allowed within 30 days"},
            output_data={"eligible": True, "reason": "Inside 30-day refund window"},
            latency_ms=60
        )

        final_answer = (
            "The customer may be eligible for a refund because the order was delivered "
            "12 days ago, which is inside the 30-day refund window."
        )

        run.log_span(
            span_type="llm_call",
            name="generate_response",
            input_data={"intent": "refund_request", "eligible": True},
            output_data={"response": final_answer},
            latency_ms=150
        )

        run.set_output(final_answer)

    print("Created successful run")


def tool_failure_refund_run():
    with aw.trace(
        run_name="refund-agent-tool-failure-run",
        input_text="Can I get a refund for my order?",
        model="fake-llm-v1"
    ) as run:
        run.log_span(
            span_type="llm_call",
            name="classify_intent",
            input_data={"message": "Can I get a refund for my order?"},
            output_data={"intent": "refund_request"},
            latency_ms=120
        )

        run.log_span(
            span_type="tool_call",
            name="lookup_order",
            input_data={"order_id": "ORD-123"},
            status="error",
            output_data=None,
            error_message="Order service timeout",
            latency_ms=450
        )

        fallback_answer = (
            "I could not verify the order because the order lookup service failed. "
            "Please try again later."
        )

        run.log_span(
            span_type="llm_call",
            name="generate_fallback_response",
            input_data={"intent": "refund_request", "order_verified": False},
            output_data={"response": fallback_answer},
            latency_ms=180
        )

        run.set_output(fallback_answer)

    print("Created tool failure run")


def slow_refund_run():
    with aw.trace(
        run_name="refund-agent-slow-run",
        input_text="Can I get a refund for my order?",
        model="fake-llm-v1"
    ) as run:
        run.log_span(
            span_type="llm_call",
            name="classify_intent",
            input_data={"message": "Can I get a refund for my order?"},
            output_data={"intent": "refund_request"},
            latency_ms=120
        )

        # Simulate a slow external call so the overall run latency reflects real delay
        time.sleep(3.5)

        run.log_span(
            span_type="tool_call",
            name="lookup_order",
            input_data={"order_id": "ORD-123"},
            output_data={"status": "delivered", "days_since_delivery": 12},
            latency_ms=3500
        )

        run.log_span(
            span_type="tool_call",
            name="check_refund_policy",
            input_data={"days_since_delivery": 12, "policy": "refund allowed within 30 days"},
            output_data={"eligible": True, "reason": "Inside 30-day refund window"},
            latency_ms=90
        )

        final_answer = (
            "The customer may be eligible for a refund, but this response was slow."
        )

        run.log_span(
            span_type="llm_call",
            name="generate_response",
            input_data={"intent": "refund_request", "eligible": True},
            output_data={"response": final_answer},
            latency_ms=150
        )

        run.set_output(final_answer)

    print("Created slow run")


def empty_output_refund_run():
    with aw.trace(
        run_name="refund-agent-empty-output-run",
        input_text="Can I get a refund for my order?",
        model="fake-llm-v1"
    ) as run:
        run.log_span(
            span_type="llm_call",
            name="classify_intent",
            input_data={"message": "Can I get a refund for my order?"},
            output_data={"intent": "refund_request"},
            latency_ms=120
        )

        run.log_span(
            span_type="tool_call",
            name="lookup_order",
            input_data={"order_id": "ORD-123"},
            output_data={"status": "delivered", "days_since_delivery": 12},
            latency_ms=80
        )

        run.log_span(
            span_type="tool_call",
            name="check_refund_policy",
            input_data={"days_since_delivery": 12, "policy": "refund allowed within 30 days"},
            output_data={"eligible": True, "reason": "Inside 30-day refund window"},
            latency_ms=60
        )

        run.log_span(
            span_type="llm_call",
            name="generate_response",
            input_data={"intent": "refund_request", "eligible": True},
            output_data={"response": ""},
            latency_ms=150
        )

        run.set_output("")

    print("Created empty output run")


if __name__ == "__main__":
    successful_refund_run()
    tool_failure_refund_run()
    slow_refund_run()
    empty_output_refund_run()
