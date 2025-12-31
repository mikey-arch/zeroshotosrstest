## Project Structure

```
osrs_vlm_agent/
├── config.py              # Configuration (API keys, settings)
├── window_manager.py      # RuneLite window detection
├── screen_capture.py      # Screenshot capture
├── logger.py              # Real-time logging system
├── action_executor.py     # Mouse/keyboard control with randomization
├── vision.py              # VLM integration (Claude/GPT-4V)
├── skills.py              # Skill library (find_item, make_fire, etc)
├── agent.py    # Main agent script
├── requirements.txt       # Python dependencies
├── window_config.json     # Auto-generated window position
├── screenshots/           # Debug screenshots
└── logs/                  # Action logs
```

