"""
screen_capture.py - Screenshot capture for RuneLite window
"""

import mss
import mss.tools
from PIL import Image, ImageDraw
from datetime import datetime
from typing import Optional, List, Tuple

import config
from logger import logger
from window_manager import window_manager


class ScreenCapture:
    """Handles screenshot capture and annotation"""

    def __init__(self):
        self.screenshot_count = 0

    def capture(self, save: bool = True, annotate: bool = False,
                boxes: Optional[List[Tuple[int, int, int, int, str]]] = None) -> Optional[Image.Image]:
        """
        Capture screenshot of RuneLite window

        Args:
            save: Save screenshot to file
            annotate: Draw annotations on screenshot
            boxes: List of (x1, y1, x2, y2, label) tuples for bounding boxes

        Returns:
            PIL Image or None if failed
        """
        if not window_manager.is_ready():
            logger.error("Window manager not ready")
            return None

        region = window_manager.get_region()

        try:
            # Simple mss capture - coordinates are now validated
            with mss.mss() as sct:
                screenshot = sct.grab(region)
                image = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")

            # Annotate if requested
            if annotate and boxes:
                image = self._annotate_image(image, boxes)

            # Save if requested
            if save:
                self._save_screenshot(image)

            return image

        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")
            return None

    def _annotate_image(self, image: Image.Image,
                       boxes: List[Tuple[int, int, int, int, str]]) -> Image.Image:
        """Draw bounding boxes and labels on image"""
        draw = ImageDraw.Draw(image)

        for box in boxes:
            x1, y1, x2, y2, label = box

            # Draw rectangle
            draw.rectangle([x1, y1, x2, y2], outline="red", width=2)

            # Draw label
            draw.text((x1, y1 - 10), label, fill="red")

        return image

    def _save_screenshot(self, image: Image.Image) -> str:
        """Save screenshot to file"""
        self.screenshot_count += 1
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{config.SCREENSHOT_DIR}/screenshot_{timestamp}_{self.screenshot_count:03d}.png"

        image.save(filename)
        logger.debug(f"Screenshot saved: {filename}")

        return filename

    def capture_region(self, x: int, y: int, width: int, height: int,
                      save: bool = False) -> Optional[Image.Image]:
        """
        Capture a specific region within the game window

        Args:
            x, y: Top-left corner relative to game window
            width, height: Region size
            save: Save to file

        Returns:
            PIL Image or None
        """
        full_image = self.capture(save=False)

        if full_image:
            region = full_image.crop((x, y, x + width, y + height))

            if save:
                self._save_screenshot(region)

            return region

        return None


# Global screen capture instance
screen_capture = ScreenCapture()
