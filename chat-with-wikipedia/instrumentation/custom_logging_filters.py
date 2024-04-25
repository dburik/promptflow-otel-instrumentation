import logging


class AddAdditionalInfoLoggingFilter(logging.Filter):
    """Adds additional properties provided in the constructor to log records."""

    def __init__(self, additional_info: dict):
        super().__init__()
        self.additional_info = additional_info or {}

    def filter(self, record):
        # Add additional info to log record
        for key, value in self.additional_info.items():
            setattr(record, key, value)
        return True
