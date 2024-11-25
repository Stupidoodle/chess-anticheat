import structlog
import logging.config
from typing import Dict


def setup_logging(service_name: str, log_level: str = "INFO"):
    """Configure structured logging for the service."""

    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ]

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processor": structlog.processors.JSONRenderer(),
                }
            },
            "handlers": {
                "default": {"class": "logging.StreamHandler", "formatter": "json"}
            },
            "loggers": {
                "": {
                    "handlers": ["default"],
                    "level": log_level,
                    "propagate": True,
                }
            },
        }
    )

    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    return structlog.get_logger(service_name)


# Example usage in services
logger = setup_logging("move-analysis")


@logger.inject_lambda_context
def analyze_move(event, context):
    logger.info("starting_move_analysis", move=event["move"])
    try:
        result = perform_analysis(event)
        logger.info(
            "analysis_complete",
            duration=result["duration"],
            suspicious_score=result["score"],
        )
        return result
    except Exception as e:
        logger.exception("analysis_failed", error=str(e))
        raise
