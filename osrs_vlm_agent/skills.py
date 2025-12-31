"""
skills.py - Skill library for OSRS actions
"""

import time
from typing import Optional, Tuple
from PIL import Image

from logger import logger
from screen_capture import screen_capture
from action_executor import action_executor
from vision import vision_model


class SkillLibrary:
    """Library of reusable skills for OSRS agent"""

    def __init__(self):
        # Inventory grid constants (will be calibrated from visual detection)
        self.inventory_start_x = None
        self.inventory_start_y = None
        self.slot_width = 42  # Approximate, will be refined
        self.slot_height = 36  # Approximate, will be refined
        self.slots_per_row = 4

    def calibrate_inventory(self):
        """Use VLM to calibrate inventory position (TODO: implement)"""
        logger.info("Inventory calibration not yet implemented, using defaults")
        # For now, these will need to be set manually or detected visually
        # In resizable mode, inventory position varies
        pass

    def get_slot_center(self, slot: int) -> Tuple[int, int]:
        """
        Get center coordinates of inventory slot

        Args:
            slot: Slot number (0-27)

        Returns:
            (x, y) coordinates relative to game window
        """
        if self.inventory_start_x is None or self.inventory_start_y is None:
            # TODO: Detect inventory position visually
            # For now, raise error - this needs to be calibrated
            raise ValueError("Inventory not calibrated. Run calibrate_inventory() first")

        row = slot // self.slots_per_row
        col = slot % self.slots_per_row

        x = self.inventory_start_x + (col * self.slot_width) + (self.slot_width // 2)
        y = self.inventory_start_y + (row * self.slot_height) + (self.slot_height // 2)

        return x, y

    def click_inventory_slot(self, slot: int, item_name: Optional[str] = None) -> bool:
        """
        Click an inventory slot

        Args:
            slot: Slot number (0-27)
            item_name: Name of item for logging

        Returns:
            True if clicked successfully
        """
        try:
            x, y = self.get_slot_center(slot)
            action_executor.click(x, y, relative=True, item_name=item_name)
            return True
        except Exception as e:
            logger.error(f"Failed to click slot {slot}: {e}")
            return False

    def find_item_visual(self, item_name: str) -> Optional[int]:
        """
        Find item in inventory using VLM

        Args:
            item_name: Name of item to find

        Returns:
            Slot number or None if not found
        """
        logger.log_action("FIND_ITEM", item_name)

        # Capture inventory region (TODO: make this dynamic)
        screenshot = screen_capture.capture(save=False)

        if not screenshot:
            return None

        # Use VLM to find item
        if item_name.lower() == "tinderbox":
            slot = vision_model.find_tinderbox(screenshot)
        elif "log" in item_name.lower():
            slot = vision_model.find_logs(screenshot)
        else:
            # Generic item search
            prompt = f"""Look at this OSRS inventory. Find the {item_name}.
            Return ONLY the slot number (0-27) where it is located.
            If not found, return -1. Respond with just the number."""

            response = vision_model.analyze_screenshot(screenshot, prompt)
            try:
                slot = int(response.strip()) if response else None
                slot = slot if slot and slot >= 0 else None
            except:
                slot = None

        if slot is not None:
            logger.log_success(f"Found {item_name} in slot {slot}")
        else:
            logger.log_error(f"{item_name} not found in inventory")

        return slot

    def use_item_on_item(self, item1: str, item2: str) -> bool:
        """
        Use one item on another (e.g., tinderbox on logs)

        Args:
            item1: First item to click
            item2: Second item to use it on

        Returns:
            True if successful
        """
        logger.log_skill("use_item_on_item", f"{item1} -> {item2}")

        # Find both items
        slot1 = self.find_item_visual(item1)
        slot2 = self.find_item_visual(item2)

        if slot1 is None or slot2 is None:
            logger.log_error(f"Could not find items: {item1}, {item2}", retry=False)
            return False

        # Click first item
        self.click_inventory_slot(slot1, item1)
        action_executor.wait(0.3)

        # Click second item
        self.click_inventory_slot(slot2, item2)
        action_executor.wait(0.5)

        return True

    def make_fire(self) -> bool:
        """
        Make one fire (tinderbox on logs)

        Returns:
            True if fire was made successfully
        """
        logger.log_skill("make_fire", "executing")

        # Use tinderbox on logs
        if not self.use_item_on_item("tinderbox", "logs"):
            return False

        # Wait for fire to appear
        action_executor.wait(2.0)

        # Verify fire was made
        screenshot = screen_capture.capture(save=True)
        if screenshot:
            fire_made = vision_model.verify_fire_made(screenshot)
            if fire_made:
                logger.log_success("Fire created")
                return True
            else:
                logger.log_error("Fire not detected")
                return False

        return False

    def move_away_from_fire(self, distance: int = 2) -> bool:
        """
        Move character away from current position (to avoid standing on fire)

        Args:
            distance: Tiles to move (approximate)

        Returns:
            True if moved successfully
        """
        logger.log_skill("move_away_from_fire", "executing")

        # TODO: Implement pathfinding or simple tile clicking
        # For now, just click a few tiles away
        # This needs visual detection of game tiles

        logger.warning("move_away_from_fire not fully implemented yet")
        return True

    def count_logs_in_inventory(self) -> int:
        """
        Count number of logs remaining in inventory

        Returns:
            Number of log stacks
        """
        screenshot = screen_capture.capture(save=False)
        if not screenshot:
            return 0

        prompt = """Look at this OSRS inventory.
        Count how many inventory slots contain logs (any type).
        Return ONLY a number. If no logs, return 0."""

        response = vision_model.analyze_screenshot(screenshot, prompt)

        try:
            count = int(response.strip()) if response else 0
            logger.debug(f"Logs remaining: {count}")
            return count
        except:
            logger.warning("Failed to count logs")
            return 0


# Global skill library instance
skill_library = SkillLibrary()
