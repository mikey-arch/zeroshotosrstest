"""
logger.py - Real-time logging system with color support
"""

import logging
import sys
from datetime import datetime
from typing import Optional

import config


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for terminal output"""

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m',
        'BOLD': '\033[1m',
    }

    def format(self, record):
        if config.COLORIZE_LOGS:
            color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
            record.levelname = f"{color}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)


class AgentLogger:
    """Logger for OSRS VLM Agent with real-time action logging"""

    def __init__(self, name: str = "OSRSAgent"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, config.LOG_LEVEL))

        # Console handler with colors
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)

        # Format: [TIME] LEVEL - Message
        formatter = ColoredFormatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(formatter)

        self.logger.addHandler(console_handler)

        # File handler for persistent logs
        log_file = f"{config.LOG_DIR}/agent_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        self.info(f"Logger initialized. Logs saved to: {log_file}")

    def debug(self, msg: str):
        self.logger.debug(msg)

    def info(self, msg: str):
        self.logger.info(msg)

    def warning(self, msg: str):
        self.logger.warning(msg)

    def error(self, msg: str):
        self.logger.error(msg)

    def critical(self, msg: str):
        self.logger.critical(msg)

    # Custom logging methods for agent actions
    def log_click(self, x: int, y: int, item: Optional[str] = None):
        """Log mouse click with coordinates"""
        item_str = f" on '{item}'" if item else ""
        self.info(f"🖱️  CLICK at ({x}, {y}){item_str}")

    def log_action(self, action: str, details: str = ""):
        """Log agent action"""
        details_str = f" - {details}" if details else ""
        self.info(f"🎮 ACTION: {action}{details_str}")

    def log_vision(self, observation: str):
        """Log VLM observation"""
        self.info(f"👁️  VISION: {observation}")

    def log_decision(self, decision: str):
        """Log agent decision"""
        self.info(f"🧠 DECISION: {decision}")

    def log_skill(self, skill_name: str, status: str = "executing"):
        """Log skill execution"""
        self.info(f"⚡ SKILL: {skill_name} ({status})")

    def log_error(self, error: str, retry: bool = False):
        """Log error with optional retry info"""
        retry_str = " - Will retry" if retry else ""
        self.error(f"❌ ERROR: {error}{retry_str}")

    def log_success(self, task: str):
        """Log successful task completion"""
        self.info(f"✅ SUCCESS: {task}")


# Global logger instance
logger = AgentLogger()
