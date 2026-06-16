import logging
from datetime import datetime


class MediAgentException(Exception):
    """Base exception for MediAgent"""
    pass


class AuthenticationError(MediAgentException):
    """Raised when authentication fails"""
    pass


class ChatNotFoundError(MediAgentException):
    """Raised when chat is not found"""
    pass


class UserNotFoundError(MediAgentException):
    """Raised when user is not found"""
    pass


class RAGError(MediAgentException):
    """Raised when RAG operations fail"""
    pass


class LLMError(MediAgentException):
    """Raised when LLM operations fail"""
    pass


class ValidationError(MediAgentException):
    """Raised when validation fails"""
    pass


def setup_logger(name: str) -> logging.Logger:
    """Configure a logger with structured formatting"""
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    return logger


class Logger:
    """Wrapper for structured logging"""

    def __init__(self, name: str):
        self.logger = setup_logger(name)

    def info(self, message: str, **kwargs):
        context = " | ".join(f"{k}={v}" for k, v in kwargs.items())
        self.logger.info(f"{message} {context}")

    def error(self, message: str, **kwargs):
        context = " | ".join(f"{k}={v}" for k, v in kwargs.items())
        self.logger.error(f"{message} {context}")

    def debug(self, message: str, **kwargs):
        context = " | ".join(f"{k}={v}" for k, v in kwargs.items())
        self.logger.debug(f"{message} {context}")
