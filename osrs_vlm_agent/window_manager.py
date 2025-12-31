"""
window_manager.py - RuneLite window detection and management
"""

import json
from typing import Optional, Dict
from Xlib import X, display
from Xlib.error import XError

import config
from logger import logger


class WindowManager:
    """Manages RuneLite window detection and tracking"""

    def __init__(self):
        self.window_config: Optional[Dict] = None
        self.display = display.Display()
        self.load_or_detect()

    def _get_window_geometry(self, window):
        """Get window geometry (position and size)"""
        try:
            geo = window.get_geometry()

            # Translate to root window coordinates
            coords = window.translate_coords(self.display.screen().root, 0, 0)

            # Handle negative coordinates (window decorations)
            # If coords are negative, use their absolute value as offset
            # to skip decorations, and keep original dimensions
            offset_x = abs(min(0, coords.x))  # Left border width
            offset_y = abs(min(0, coords.y))  # Top titlebar height

            # Start from offset position to skip decorations
            x = offset_x
            y = offset_y

            # Keep original dimensions (captures game content area)
            width = geo.width
            height = geo.height

            return {
                'x': x,
                'y': y,
                'width': width,
                'height': height
            }
        except Exception as e:
            return None

    def _get_window_name(self, window):
        """Get window title/name"""
        try:
            return window.get_wm_name()
        except:
            return None

    def _search_windows(self, window, name_filter, results=None):
        """Recursively search for windows matching name filter"""
        if results is None:
            results = []

        try:
            window_name = self._get_window_name(window)

            if window_name and name_filter.lower() in window_name.lower():
                geo = self._get_window_geometry(window)
                if geo and geo['width'] > 0 and geo['height'] > 0:
                    # Store this as a potential match
                    results.append({
                        'window': window,
                        'title': window_name,
                        **geo
                    })

            # Search children
            children = window.query_tree().children
            for child in children:
                self._search_windows(child, name_filter, results)

        except XError:
            pass

        return results

    def find_runelite_window(self) -> Optional[Dict]:
        """Find RuneLite window using Xlib (Linux)"""
        try:
            root = self.display.screen().root

            # Search for all RuneLite windows
            results = self._search_windows(root, config.GAME_NAME)

            if not results:
                logger.warning(f"{config.GAME_NAME} window not found!")
                logger.warning("Make sure RuneLite is running and visible.")
                return None

            # Debug: show all found windows
            logger.debug(f"Found {len(results)} RuneLite window(s):")
            for i, r in enumerate(results):
                logger.debug(f"  {i+1}. '{r['title']}' at ({r['x']}, {r['y']}) size {r['width']}x{r['height']}")

            # Just pick the largest window (tiling WM coordinates are already correct)
            result = max(results, key=lambda r: r['width'] * r['height'])

            window_info = {
                'x': result['x'],
                'y': result['y'],
                'width': result['width'],
                'height': result['height'],
                'title': result['title']
            }

            logger.info(f"Found window: '{result['title']}' at ({result['x']}, {result['y']}) size {result['width']}x{result['height']}")
            if len(results) > 1:
                logger.debug(f"Found {len(results)} RuneLite windows, selected the largest")

            return window_info

        except Exception as e:
            logger.error(f"Error finding window: {e}")
            return None

    def load_or_detect(self) -> bool:
        """Load saved window config or detect new one"""
        # Try to load existing config
        try:
            with open(config.WINDOW_CONFIG_FILE, 'r') as f:
                self.window_config = json.load(f)
                logger.info(f"Loaded window config from {config.WINDOW_CONFIG_FILE}")
                return True
        except FileNotFoundError:
            logger.debug("No saved window config found, detecting...")
        except Exception as e:
            logger.warning(f"Error loading config: {e}, detecting new window...")

        # Detect window
        self.window_config = self.find_runelite_window()

        if self.window_config:
            self.save_config()
            return True

        return False

    def save_config(self):
        """Save window configuration to file"""
        if self.window_config:
            with open(config.WINDOW_CONFIG_FILE, 'w') as f:
                json.dump(self.window_config, f, indent=2)
            logger.debug(f"Saved window config to {config.WINDOW_CONFIG_FILE}")

    def refresh(self) -> bool:
        """Re-detect window (useful if window moved/resized)"""
        logger.info("Refreshing window detection...")
        self.window_config = self.find_runelite_window()

        if self.window_config:
            self.save_config()
            return True

        return False

    def get_region(self) -> Optional[Dict]:
        """Get window region for screenshot capture"""
        if not self.window_config:
            logger.error("No window config available")
            return None

        return {
            'left': self.window_config['x'],
            'top': self.window_config['y'],
            'width': self.window_config['width'],
            'height': self.window_config['height']
        }

    def get_absolute_coords(self, relative_x: int, relative_y: int) -> tuple[int, int]:
        """Convert relative window coordinates to absolute screen coordinates"""
        if not self.window_config:
            raise ValueError("No window config available")

        abs_x = self.window_config['x'] + relative_x
        abs_y = self.window_config['y'] + relative_y

        return abs_x, abs_y

    def is_ready(self) -> bool:
        """Check if window manager is ready"""
        return self.window_config is not None


# Global window manager instance
window_manager = WindowManager()
