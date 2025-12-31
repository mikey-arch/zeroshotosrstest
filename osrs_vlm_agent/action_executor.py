"""
action_executor.py - Mouse and keyboard control with human-like randomization
"""

import time
import random
import pyautogui
from typing import Tuple, Optional

import config
from logger import logger
from window_manager import window_manager


# Disable pyautogui fail-safe (we handle errors ourselves)
pyautogui.FAILSAFE = False


class ActionExecutor:
    """Executes mouse and keyboard actions with human-like randomization"""

    def __init__(self):
        self.last_click_time = 0

    def _randomize_point(self, x: int, y: int, radius: int = 3) -> Tuple[int, int]:
        """Add random offset to coordinates to look more human"""
        offset_x = random.randint(-radius, radius)
        offset_y = random.randint(-radius, radius)
        return x + offset_x, y + offset_y

    def _random_duration(self, duration_range: Tuple[float, float]) -> float:
        """Get random duration within range"""
        return random.uniform(duration_range[0], duration_range[1])

    def _human_delay(self, delay_range: Tuple[float, float] = None):
        """Add human-like delay"""
        if delay_range is None:
            delay_range = config.HUMAN_REACTION_TIME

        delay = self._random_duration(delay_range)
        time.sleep(delay)

    def move_mouse(self, x: int, y: int, relative: bool = True, randomize: bool = True):
        """
        Move mouse to position

        Args:
            x, y: Coordinates (relative to game window if relative=True)
            relative: If True, coordinates are relative to game window
            randomize: Add random offset to look human
        """
        if relative:
            abs_x, abs_y = window_manager.get_absolute_coords(x, y)
        else:
            abs_x, abs_y = x, y

        if randomize:
            abs_x, abs_y = self._randomize_point(abs_x, abs_y)

        duration = self._random_duration(config.MOUSE_MOVEMENT_DURATION)

        try:
            pyautogui.moveTo(abs_x, abs_y, duration=duration)
            logger.debug(f"Mouse moved to ({abs_x}, {abs_y})")
        except Exception as e:
            logger.error(f"Failed to move mouse: {e}")

    def click(self, x: int, y: int, relative: bool = True, randomize: bool = True,
              item_name: Optional[str] = None, button: str = 'left'):
        """
        Click at position

        Args:
            x, y: Coordinates (relative to game window if relative=True)
            relative: If True, coordinates are relative to game window
            randomize: Add random offset
            item_name: Name of item being clicked (for logging)
            button: Mouse button ('left', 'right', 'middle')
        """
        if relative:
            abs_x, abs_y = window_manager.get_absolute_coords(x, y)
        else:
            abs_x, abs_y = x, y

        if randomize:
            abs_x, abs_y = self._randomize_point(abs_x, abs_y)

        try:
            # Move to position
            duration = self._random_duration(config.MOUSE_MOVEMENT_DURATION)
            pyautogui.moveTo(abs_x, abs_y, duration=duration)

            # Small delay before click
            time.sleep(self._random_duration((0.05, 0.15)))

            # Click
            pyautogui.click(button=button)

            # Log the click
            logger.log_click(abs_x, abs_y, item_name)

            # Delay after click
            self._human_delay(config.CLICK_DELAY)
            self.last_click_time = time.time()

        except Exception as e:
            logger.error(f"Failed to click: {e}")

    def right_click(self, x: int, y: int, relative: bool = True, randomize: bool = True,
                   item_name: Optional[str] = None):
        """Right click at position"""
        self.click(x, y, relative, randomize, item_name, button='right')

    def drag(self, start_x: int, start_y: int, end_x: int, end_y: int,
             relative: bool = True, randomize: bool = True):
        """
        Drag from start to end position

        Args:
            start_x, start_y: Starting coordinates
            end_x, end_y: Ending coordinates
            relative: If True, coordinates are relative to game window
            randomize: Add random offset
        """
        if relative:
            abs_start_x, abs_start_y = window_manager.get_absolute_coords(start_x, start_y)
            abs_end_x, abs_end_y = window_manager.get_absolute_coords(end_x, end_y)
        else:
            abs_start_x, abs_start_y = start_x, start_y
            abs_end_x, abs_end_y = end_x, end_y

        if randomize:
            abs_start_x, abs_start_y = self._randomize_point(abs_start_x, abs_start_y)
            abs_end_x, abs_end_y = self._randomize_point(abs_end_x, abs_end_y)

        try:
            duration = self._random_duration(config.MOUSE_MOVEMENT_DURATION)
            pyautogui.moveTo(abs_start_x, abs_start_y, duration=duration * 0.5)

            time.sleep(0.1)

            pyautogui.drag(abs_end_x - abs_start_x, abs_end_y - abs_start_y,
                          duration=duration, button='left')

            logger.log_action("DRAG", f"from ({abs_start_x}, {abs_start_y}) to ({abs_end_x}, {abs_end_y})")

            self._human_delay(config.CLICK_DELAY)

        except Exception as e:
            logger.error(f"Failed to drag: {e}")

    def type_text(self, text: str, interval: float = None):
        """
        Type text with human-like intervals

        Args:
            text: Text to type
            interval: Time between keystrokes (random if None)
        """
        if interval is None:
            interval = random.uniform(0.05, 0.15)

        try:
            pyautogui.typewrite(text, interval=interval)
            logger.log_action("TYPE", text)
            self._human_delay(config.CLICK_DELAY)
        except Exception as e:
            logger.error(f"Failed to type text: {e}")

    def press_key(self, key: str):
        """Press a single key"""
        try:
            pyautogui.press(key)
            logger.log_action("KEY_PRESS", key)
            self._human_delay(config.CLICK_DELAY)
        except Exception as e:
            logger.error(f"Failed to press key: {e}")

    def wait(self, duration: float = None):
        """Wait for a duration (or random human delay)"""
        if duration is None:
            self._human_delay()
        else:
            time.sleep(duration)


# Global action executor instance
action_executor = ActionExecutor()
