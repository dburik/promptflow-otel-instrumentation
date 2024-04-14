import os
import typing

from azure.monitor.opentelemetry.exporter import (
    AzureMonitorTraceExporter,
)
from dotenv import load_dotenv
from opentelemetry import context as context_api


from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import ReadableSpan, Span, SpanContext, SpanProcessor, TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from promptflow import tool
from opentelemetry import trace

load_dotenv()


class CustomSpanProcessor(SpanProcessor):
    def __init__(self, inner_processor: SpanProcessor) -> None:
        self.inner_processor = inner_processor

    def on_start(self, span: Span, parent_context: typing.Optional[context_api.Context] = None) -> None:
        self.inner_processor.on_start(span, parent_context)

    def on_end(self, span: ReadableSpan) -> None:
        # ignore the node that sets up the instrumentation
        if span.name == "instrument_otel":
            return

        new_span = self.create_new_span_with_additional_attributes(span)

        self.inner_processor.on_end(new_span)

    def shutdown(self) -> None:
        self.inner_processor.shutdown()

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        return self.inner_processor.force_flush(timeout_millis)

    def create_new_span_with_additional_attributes(self, span: ReadableSpan) -> ReadableSpan:
        old_span_context = span.get_span_context()

        new_span = ReadableSpan(
            resource=span.resource,
            name=span.name,
            context=SpanContext(
                trace_id=old_span_context.trace_id,
                span_id=old_span_context.span_id,
                trace_flags=old_span_context.trace_flags,
                trace_state=old_span_context.trace_state,
                is_remote=old_span_context.is_remote,
            ),
            parent=span.parent,
            kind=span.kind,
            start_time=span.start_time,
            end_time=span.end_time,
            attributes={**span.attributes, "customer_name": customer_name},
            events=span.events,
            links=span.links,
            status=span.status,
        )

        return new_span


def get_resource():
    return Resource.create(
        {
            "service.name": os.getenv("APPLICATION_NAME"),
            "service.instance.id": os.getenv("APPLICATION_INSTANCE"),
        }
    )


def setup_telemetry():
    resource = get_resource()

    # Tracing
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(
        CustomSpanProcessor(
            BatchSpanProcessor(AzureMonitorTraceExporter(connection_string=appinsights_connection_string))
        )
    )
    provider.add_span_processor(CustomSpanProcessor(BatchSpanProcessor(ConsoleSpanExporter())))
    trace.set_tracer_provider(provider)

    tracer = trace.get_tracer(__name__)

    return tracer


# Global variables

customer_name = os.getenv("CUSTOMER_NAME")
appinsights_connection_string = os.getenv("APPINSIGHTS_CONNECTION_STRING")

tracer = setup_telemetry()


@tool
def instrument_otel():
    return True
