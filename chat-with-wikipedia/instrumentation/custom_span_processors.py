import typing

from opentelemetry import context as context_api
from opentelemetry.sdk.trace import Span, SpanProcessor


class AddAdditionalAttributesSpanProcessor(SpanProcessor):
    """Adds additional attributes provided in the constructor to the processed span."""

    def __init__(self, span_attributes: dict) -> None:
        self.span_attributes = span_attributes or {}

    def on_start(
        self, span: Span, parent_context: typing.Optional[context_api.Context] = None
    ) -> None:
        for attribute, value in self.span_attributes.items():
            span.set_attribute(attribute, value)
