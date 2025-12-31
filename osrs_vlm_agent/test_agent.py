#!/usr/bin/env python3
"""
test_agent.py - Simple test agent to validate screenshot capture and VLM
No actions, just observation and analysis
"""

import sys
import time

from logger import logger
from window_manager import window_manager
from screen_capture import screen_capture
from vision import vision_model
import config


class TestAgent:
    """Simple test agent for validation"""

    def __init__(self):
        self.running = False

    def test_window_detection(self) -> bool:
        """Test 1: Window detection"""
        logger.info("=" * 60)
        logger.info("TEST 1: Window Detection")
        logger.info("=" * 60)

        if not window_manager.is_ready():
            logger.error("❌ Window detection failed")
            logger.error("Make sure RuneLite is running and visible")
            return False

        region = window_manager.get_region()
        logger.log_success(f"✅ Found RuneLite window")
        logger.info(f"  Position: ({region['left']}, {region['top']})")
        logger.info(f"  Size: {region['width']}x{region['height']}")

        return True

    def test_screenshot(self) -> bool:
        """Test 2: Screenshot capture"""
        logger.info("\n" + "=" * 60)
        logger.info("TEST 2: Screenshot Capture")
        logger.info("=" * 60)

        screenshot = screen_capture.capture(save=True)

        if not screenshot:
            logger.error("❌ Screenshot capture failed")
            return False

        logger.log_success(f"✅ Screenshot captured")
        logger.info(f"  Size: {screenshot.size[0]}x{screenshot.size[1]}")
        logger.info(f"  Saved to: screenshots/")

        return True

    def test_vlm_basic(self) -> bool:
        """Test 3: Basic VLM understanding"""
        logger.info("\n" + "=" * 60)
        logger.info("TEST 3: VLM Basic Understanding")
        logger.info("=" * 60)

        if not vision_model.client:
            logger.warning("⚠️  VLM not configured (no API key)")
            logger.info("Set ANTHROPIC_API_KEY or OPENAI_API_KEY to test VLM")
            return False

        screenshot = screen_capture.capture(save=False)
        if not screenshot:
            logger.error("❌ Could not capture screenshot for VLM test")
            return False

        prompt = """Look at this Old School RuneScape screenshot.
        Describe what you see in 1-2 sentences.
        What is the player doing? What's visible on screen?"""

        logger.info("Asking VLM: 'What do you see in this OSRS screenshot?'")
        logger.info("(This may take a few seconds...)")

        response = vision_model.analyze_screenshot(screenshot, prompt)

        if response:
            logger.log_success("✅ VLM response received")
            logger.info(f"\n  VLM says: {response}\n")
            return True
        else:
            logger.error("❌ VLM analysis failed")
            return False

    def test_inventory_analysis(self) -> bool:
        """Test 4: Inventory item detection"""
        logger.info("\n" + "=" * 60)
        logger.info("TEST 4: Inventory Analysis")
        logger.info("=" * 60)

        if not vision_model.client:
            logger.warning("⚠️  VLM not configured - skipping inventory test")
            return False

        screenshot = screen_capture.capture(save=False)
        if not screenshot:
            logger.error("❌ Could not capture screenshot")
            return False

        prompt = """Look at this OSRS screenshot and focus on the inventory (right side).
        List all items you can see in the inventory.
        If the inventory is empty, say "empty".
        Keep it brief - just item names."""

        logger.info("Asking VLM to analyze inventory...")

        response = vision_model.analyze_screenshot(screenshot, prompt)

        if response:
            logger.log_success("✅ Inventory analysis complete")
            logger.info(f"\n  Items found: {response}\n")
            return True
        else:
            logger.error("❌ Inventory analysis failed")
            return False

    def test_interactive_questions(self):
        """Test 5: Interactive Q&A about screenshot"""
        logger.info("\n" + "=" * 60)
        logger.info("TEST 5: Interactive Questions")
        logger.info("=" * 60)
        logger.info("You can now ask questions about the current screenshot.")
        logger.info("Type 'refresh' to take a new screenshot")
        logger.info("Type 'quit' to exit\n")

        if not vision_model.client:
            logger.warning("⚠️  VLM not configured - cannot run interactive mode")
            return

        screenshot = screen_capture.capture(save=True)

        while True:
            try:
                question = input("\n👉 Your question: ").strip()

                if not question:
                    continue

                if question.lower() in ['quit', 'exit', 'q']:
                    logger.info("Exiting interactive mode")
                    break

                if question.lower() == 'refresh':
                    logger.info("Taking new screenshot...")
                    screenshot = screen_capture.capture(save=True)
                    logger.log_success("Screenshot refreshed")
                    continue

                # Ask VLM
                logger.info("Asking VLM...")
                response = vision_model.analyze_screenshot(screenshot, question)

                if response:
                    logger.log_vision(response)
                else:
                    logger.error("VLM did not respond")

            except KeyboardInterrupt:
                logger.info("\nExiting interactive mode")
                break
            except Exception as e:
                logger.error(f"Error: {e}")

    def run_all_tests(self):
        """Run all tests in sequence"""
        logger.info("\n" + "=" * 60)
        logger.info("OSRS VLM Agent - Test Suite")
        logger.info("=" * 60 + "\n")

        tests = [
            ("Window Detection", self.test_window_detection),
            ("Screenshot Capture", self.test_screenshot),
            ("VLM Basic Understanding", self.test_vlm_basic),
            ("Inventory Analysis", self.test_inventory_analysis),
        ]

        results = {}

        for test_name, test_func in tests:
            try:
                result = test_func()
                results[test_name] = result
                time.sleep(0.5)
            except Exception as e:
                logger.error(f"❌ {test_name} crashed: {e}")
                results[test_name] = False

        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("TEST SUMMARY")
        logger.info("=" * 60)

        passed = sum(1 for r in results.values() if r)
        total = len(results)

        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"  {status} - {test_name}")

        logger.info(f"\nResults: {passed}/{total} tests passed")

        if passed == total:
            logger.log_success("\n🎉 All tests passed! Ready to run firemaking agent.")
        else:
            logger.warning("\n⚠️  Some tests failed. Fix issues before running agent.")

    def run(self, mode: str = "all"):
        """
        Run tests

        Args:
            mode: 'all', 'interactive', or specific test number
        """
        if mode == "all":
            self.run_all_tests()
        elif mode == "interactive":
            self.test_window_detection()
            self.test_screenshot()
            self.test_interactive_questions()
        else:
            logger.error(f"Unknown mode: {mode}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Test OSRS VLM Agent Components")
    parser.add_argument('-i', '--interactive', action='store_true',
                       help='Run interactive Q&A mode')
    parser.add_argument('-r', '--refresh-window', action='store_true',
                       help='Re-detect RuneLite window position')

    args = parser.parse_args()

    # Refresh window if requested
    if args.refresh_window:
        logger.info("Re-detecting window...")
        window_manager.refresh()

    # Create test agent
    agent = TestAgent()

    # Run tests
    if args.interactive:
        agent.run(mode="interactive")
    else:
        agent.run(mode="all")

    return 0


if __name__ == '__main__':
    sys.exit(main())
