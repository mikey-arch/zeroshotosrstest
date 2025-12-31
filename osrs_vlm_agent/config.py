"""
config.py - Configuration for OSRS VLM Agent
"""

import os

# VLM Configuration
VLM_PROVIDER = "anthropic"  # Options: "anthropic", "openai", "local"
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Model Selection
CLAUDE_MODEL = "claude-3-5-sonnet-20241022"
OPENAI_MODEL = "gpt-4o"

# Paths
SCREENSHOT_DIR = "screenshots"
LOG_DIR = "logs"
WINDOW_CONFIG_FILE = "window_config.json"

# Game Window
GAME_NAME = "RuneLite"  # Window title to search for

# Action Execution
MOUSE_MOVEMENT_DURATION = (0.3, 0.8)  # Min/max seconds for mouse movement
CLICK_DELAY = (0.1, 0.3)  # Delay after clicking
HUMAN_REACTION_TIME = (0.5, 1.5)  # Delay to simulate human thinking

# Screenshot Settings
SAVE_DEBUG_SCREENSHOTS = True
ANNOTATE_SCREENSHOTS = True  # Draw boxes on detected objects

# Logging
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
COLORIZE_LOGS = True

# Agent Settings
MAX_RETRIES = 3  # Max retries for failed actions
SKILL_LIBRARY_PATH = "skill_library.json"
