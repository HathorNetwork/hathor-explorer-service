import structlog

from common.configuration import LOG_RENDERER


def get_logger():
    if not structlog.is_configured():
        processors = [
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.format_exc_info,
            LOG_RENDERER.renderer_class(),
        ]
        structlog.configure(processors=processors)
    return structlog.get_logger()
