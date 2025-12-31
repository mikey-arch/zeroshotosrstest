#!/usr/bin/env python3
"""
firemaking_agent.py - Main OSRS Firemaking Agent
Uses VLM for visual understanding and autonomous firemaking
"""

import time
import sys

from logger import logger
from window_manager import window_manager
from screen_capture import screen_capture
from action_executor import action_executor
from vision import vision_model
from skills import skill_library
import config


class FiremakingAgent:
    """OSRS Firemaking Agent using CRADLE-style approach"""

    def __init__(self):
        self.running = False
        self.fires_made = 0
        self.failures = 0

    def initialize(self) -> bool:
        """Initialize agent and check all systems"""
        logger.info("=" * 50)
        logger.info("OSRS VLM Firemaking Agent")
        logger.info("=" * 50)

        # Check window manager
        if not window_manager.is_ready():
            logger.error("Window manager not ready. Make sure RuneLite is running.")
            return False

        logger.log_success("Window manager initialized")

        # Test screenshot
        test_shot = screen_capture.capture(save=True)
        if not test_shot:
            logger.error("Failed to capture screenshot")
            return False

        logger.log_success("Screenshot capture working")

        # Check VLM
        if not vision_model.client:
            logger.warning("VLM not initialized. Visual understanding will not work.")
            logger.warning("Set ANTHROPIC_API_KEY or OPENAI_API_KEY environment variable.")

        logger.info("=" * 50)
        logger.info("Agent initialized successfully!")
        logger.info("=" * 50)

        return True

    def make_one_fire(self) -> bool:
        """
        Make a single fire using tinderbox on logs

        Returns:
            True if fire was made successfully
        """
        logger.log_action("MAKE_FIRE", "Starting firemaking sequence")

        try:
            # Make the fire
            success = skill_library.make_fire()

            if success:
                self.fires_made += 1
                logger.log_success(f"Fire #{self.fires_made} complete")

                # Move away from fire
                skill_library.move_away_from_fire()
                action_executor.wait(1.0)

                return True
            else:
                self.failures += 1
                logger.log_error(f"Fire attempt failed (failures: {self.failures})")
                return False

        except Exception as e:
            logger.error(f"Exception during firemaking: {e}")
            self.failures += 1
            return False

    def burn_inventory(self) -> int:
        """
        Burn entire inventory of logs

        Returns:
            Number of fires successfully made
        """
        logger.info("Starting full inventory firemaking...")

        initial_fires = self.fires_made

        while self.running:
            # Check if we still have logs
            logs_count = skill_library.count_logs_in_inventory()

            if logs_count == 0:
                logger.log_success("No more logs in inventory!")
                break

            logger.info(f"Logs remaining: {logs_count}")

            # Make one fire
            success = self.make_one_fire()

            if not success:
                # Retry logic
                if self.failures >= config.MAX_RETRIES:
                    logger.error(f"Too many failures ({self.failures}). Stopping.")
                    break

                logger.warning(f"Retrying... (attempt {self.failures}/{config.MAX_RETRIES})")
                action_executor.wait(2.0)
                continue

            # Reset failure counter on success
            self.failures = 0

            # Small delay between fires
            action_executor.wait(0.5)

        fires_this_run = self.fires_made - initial_fires
        logger.info(f"Firemaking complete. Made {fires_this_run} fires this run.")
        logger.info(f"Total fires: {self.fires_made}")

        return fires_this_run

    def run(self, num_fires: int = None):
        """
        Run the agent

        Args:
            num_fires: Number of fires to make (None = full inventory)
        """
        if not self.initialize():
            logger.error("Initialization failed. Exiting.")
            return

        self.running = True

        try:
            if num_fires is None:
                # Burn full inventory
                self.burn_inventory()
            else:
                # Make specific number of fires
                for i in range(num_fires):
                    if not self.running:
                        break

                    logger.info(f"Making fire {i+1}/{num_fires}...")
                    self.make_one_fire()

        except KeyboardInterrupt:
            logger.warning("Interrupted by user")
        except Exception as e:
            logger.error(f"Fatal error: {e}")
        finally:
            self.running = False
            logger.info("Agent stopped")

    def stop(self):
        """Stop the agent"""
        logger.warning("Stopping agent...")
        self.running = False


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="OSRS VLM Firemaking Agent")
    parser.add_argument('-n', '--num-fires', type=int, default=None,
                       help='Number of fires to make (default: full inventory)')
    parser.add_argument('-t', '--test', action='store_true',
                       help='Test mode: make one fire and exit')
    parser.add_argument('-r', '--refresh-window', action='store_true',
                       help='Re-detect RuneLite window position')

    args = parser.parse_args()

    # Refresh window if requested
    if args.refresh_window:
        logger.info("Re-detecting window...")
        window_manager.refresh()

    # Create agent
    agent = FiremakingAgent()

    # Test mode
    if args.test:
        logger.info("TEST MODE: Making one fire")
        agent.run(num_fires=1)
    else:
        # Normal mode
        agent.run(num_fires=args.num_fires)

    return 0


if __name__ == '__main__':
    sys.exit(main())
