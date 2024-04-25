import logging
import os

from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes

from .custom_logging_filters import AddAdditionalInfoLoggingFilter
from .custom_span_processors import AddAdditionalAttributesSpanProcessor

AZURE_MONITOR_LOGGER_NAME = "azure_monitor_logger"

_appinsights_connection_string = os.getenv("APPINSIGHTS_CONNECTION_STRING")

# Dictionary to hold additional info to be added to log records and spans
_additional_attributes = {
    "my_custom_property": os.getenv("INSTRUMENTATION_MY_CUSTOM_PROPERTY"),
}


def configure_tracing_and_logging():
    """Configures OpenTelemetry tracing and logging with Azure Monitor."""
    configure_azure_monitor(
        connection_string=_appinsights_connection_string,
        resource=_get_resource(),
        logger_name=AZURE_MONITOR_LOGGER_NAME,
        span_processors=[
            AddAdditionalAttributesSpanProcessor(_additional_attributes),
            # BatchSpanProcessor(ConsoleSpanExporter()),
        ],
    )

    # configure Azure Monitor logger
    azm_logger = logging.getLogger(AZURE_MONITOR_LOGGER_NAME)
    azm_logger.setLevel(logging.INFO)
    azm_logger.addFilter(AddAdditionalInfoLoggingFilter(_additional_attributes))

    formatter = logging.Formatter("[%(asctime)s] - %(name)-15s - [%(levelname)s] - %(message)s")

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    azm_logger.addHandler(stream_handler)

    logging.getLogger(__name__).info("Tracing and logging configured successfully.")


def get_azure_monitor_logger():
    """Returns a named logger for Azure Monitor logs.
    This logger will send all logs (above the level specified during
    configuration) to Azure Monitor    and WILL NOT propagate to the root
    logger."""
    return logging.getLogger(AZURE_MONITOR_LOGGER_NAME)


def _get_resource():
    return Resource.create(
        {
            ResourceAttributes.SERVICE_NAME: os.getenv("INSTRUMENTATION_SERVICE_NAME", "chat-with-wikipedia"),
            ResourceAttributes.SERVICE_INSTANCE_ID: os.getenv("INSTRUMENTATION_SERVICE_INSTANCE_ID", "dev"),
        }
    )


configure_tracing_and_logging()
