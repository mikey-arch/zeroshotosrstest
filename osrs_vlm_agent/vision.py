"""
vision.py - VLM integration for visual understanding
"""

import base64
import io
from typing import Optional, Dict, List
from PIL import Image

import config
from logger import logger


class VisionModel:
    """Wrapper for VLM (Claude Vision, GPT-4V, or local model)"""

    def __init__(self):
        self.provider = config.VLM_PROVIDER
        self._setup_client()

    def _setup_client(self):
        """Initialize the appropriate VLM client"""
        if self.provider == "anthropic":
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
                logger.info(f"Initialized Anthropic Claude ({config.CLAUDE_MODEL})")
            except ImportError:
                logger.error("anthropic package not installed. Run: pip install anthropic")
                self.client = None
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic client: {e}")
                self.client = None

        elif self.provider == "openai":
            try:
                import openai
                self.client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
                logger.info(f"Initialized OpenAI ({config.OPENAI_MODEL})")
            except ImportError:
                logger.error("openai package not installed. Run: pip install openai")
                self.client = None
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.client = None

        elif self.provider == "local":
            logger.warning("Local VLM not yet implemented")
            self.client = None

        else:
            logger.error(f"Unknown VLM provider: {self.provider}")
            self.client = None

    def _encode_image(self, image: Image.Image) -> str:
        """Encode PIL Image to base64"""
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

    def analyze_screenshot(self, image: Image.Image, prompt: str) -> Optional[str]:
        """
        Analyze a screenshot with VLM

        Args:
            image: PIL Image to analyze
            prompt: Question/instruction for the VLM

        Returns:
            VLM response text or None if failed
        """
        if not self.client:
            logger.error("VLM client not initialized")
            return None

        try:
            if self.provider == "anthropic":
                return self._analyze_anthropic(image, prompt)
            elif self.provider == "openai":
                return self._analyze_openai(image, prompt)
            else:
                logger.error(f"Provider {self.provider} not supported")
                return None

        except Exception as e:
            logger.error(f"VLM analysis failed: {e}")
            return None

    def _analyze_anthropic(self, image: Image.Image, prompt: str) -> Optional[str]:
        """Analyze with Claude Vision"""
        image_data = self._encode_image(image)

        message = self.client.messages.create(
            model=config.CLAUDE_MODEL,
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ],
                }
            ],
        )

        response = message.content[0].text
        logger.log_vision(response[:100] + "..." if len(response) > 100 else response)
        return response

    def _analyze_openai(self, image: Image.Image, prompt: str) -> Optional[str]:
        """Analyze with GPT-4V"""
        image_data = self._encode_image(image)

        response = self.client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_data}"
                            }
                        }
                    ],
                }
            ],
            max_tokens=1024,
        )

        result = response.choices[0].message.content
        logger.log_vision(result[:100] + "..." if len(result) > 100 else result)
        return result

    def identify_items(self, image: Image.Image) -> Dict:
        """
        Identify items in inventory from screenshot

        Returns:
            Dict with item names and positions
        """
        prompt = """Analyze this OSRS inventory screenshot.
        Identify all items and their positions in the inventory grid.
        Return as JSON with format: {"items": [{"name": "item_name", "slot": slot_number}]}
        Inventory slots are numbered 0-27, left to right, top to bottom."""

        response = self.analyze_screenshot(image, prompt)

        if response:
            try:
                import json
                return json.loads(response)
            except:
                logger.warning("Failed to parse VLM response as JSON")
                return {"items": []}

        return {"items": []}

    def find_tinderbox(self, image: Image.Image) -> Optional[int]:
        """Find tinderbox in inventory, return slot number"""
        prompt = """Look at this OSRS inventory. Find the tinderbox.
        Return ONLY the slot number (0-27) where the tinderbox is located.
        If no tinderbox is found, return -1.
        Respond with just the number, nothing else."""

        response = self.analyze_screenshot(image, prompt)

        if response:
            try:
                slot = int(response.strip())
                return slot if slot >= 0 else None
            except:
                logger.warning("Failed to parse tinderbox slot")
                return None

        return None

    def find_logs(self, image: Image.Image) -> Optional[int]:
        """Find logs in inventory, return slot number of first stack"""
        prompt = """Look at this OSRS inventory. Find logs (any type: normal, oak, willow, etc).
        Return ONLY the slot number (0-27) of the FIRST logs you see.
        If no logs are found, return -1.
        Respond with just the number, nothing else."""

        response = self.analyze_screenshot(image, prompt)

        if response:
            try:
                slot = int(response.strip())
                return slot if slot >= 0 else None
            except:
                logger.warning("Failed to parse logs slot")
                return None

        return None

    def verify_fire_made(self, image: Image.Image) -> bool:
        """Check if a fire was successfully made"""
        prompt = """Look at this OSRS game screenshot.
        Is there a fire visible on the ground?
        Respond with ONLY 'yes' or 'no'."""

        response = self.analyze_screenshot(image, prompt)

        if response:
            return 'yes' in response.lower()

        return False


# Global vision model instance
vision_model = VisionModel()
