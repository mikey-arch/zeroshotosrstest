# OSRS VLM Firemaking Agent

An autonomous Old School RuneScape (OSRS) firemaking bot using Vision-Language Models (VLM) for visual understanding. Built following the CRADLE framework approach - no pre-recorded demonstrations needed, the agent learns from its own experience.

## Features

- **Vision-based understanding**: Uses Claude Vision or GPT-4V to understand game state from screenshots
- **Dynamic window detection**: Works with any RuneLite window size (no fixed mode required)
- **Human-like movements**: Randomized mouse movements and click positions to avoid detection
- **Real-time logging**: Live terminal output showing all actions and decisions
- **Modular skill library**: Reusable skills that can be composed for complex tasks
- **Works with tiling managers**: Automatically detects RuneLite window position

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
├── firemaking_agent.py    # Main agent script
├── requirements.txt       # Python dependencies
├── window_config.json     # Auto-generated window position
├── screenshots/           # Debug screenshots
└── logs/                  # Action logs
```

## Setup

### 1. Install System Dependencies

```bash
# Arch Linux
sudo pacman -S wmctrl

# Ubuntu/Debian
sudo apt install wmctrl

# Fedora
sudo dnf install wmctrl
```

### 2. Install Python Dependencies

```bash
cd osrs_vlm_agent
pip install -r requirements.txt
```

### 3. Set Up API Key

Choose one VLM provider:

**Option A: Claude Vision (Recommended)**
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

**Option B: OpenAI GPT-4V**
```bash
export OPENAI_API_KEY="your-api-key-here"
```

Edit `config.py` to select your provider:
```python
VLM_PROVIDER = "anthropic"  # or "openai"
```

### 4. Run RuneLite

- Launch RuneLite and log in to OSRS
- No specific window mode required - any size works
- Have inventory with tinderbox and logs ready

## Usage

### Test Mode (Make 1 Fire)

```bash
python firemaking_agent.py --test
```

This will:
1. Detect RuneLite window
2. Take a test screenshot
3. Attempt to make one fire
4. Exit

### Burn Full Inventory

```bash
python firemaking_agent.py
```

This will burn all logs in your inventory.

### Make Specific Number of Fires

```bash
python firemaking_agent.py --num-fires 5
```

### Refresh Window Detection

If you move/resize RuneLite:

```bash
python firemaking_agent.py --refresh-window
```

## Configuration

Edit `config.py` to customize:

- **VLM Provider**: `anthropic`, `openai`, or `local` (future)
- **Mouse Speed**: `MOUSE_MOVEMENT_DURATION = (0.3, 0.8)`
- **Human Delays**: `HUMAN_REACTION_TIME = (0.5, 1.5)`
- **Logging Level**: `LOG_LEVEL = "INFO"`
- **Debug Screenshots**: `SAVE_DEBUG_SCREENSHOTS = True`

## How It Works

### CRADLE-Style Approach

1. **Visual Understanding**: Agent captures screenshots and uses VLM to understand game state
2. **Skill Execution**: Executes skills like `find_item()`, `use_item_on_item()`, `make_fire()`
3. **Self-Reflection**: When actions fail, uses VLM to understand why and adapt
4. **Zero-Shot Learning**: No human demonstrations needed - learns from trial and error

### Firemaking Sequence

1. Capture screenshot of inventory
2. Use VLM to find tinderbox slot
3. Use VLM to find logs slot
4. Click tinderbox → Click logs
5. Wait for fire animation
6. Verify fire was made (VLM checks game screen)
7. Move away from fire
8. Repeat until inventory empty

## Real-Time Logging

The agent logs all actions in real-time with colors:

```
15:23:45 | INFO | Found window: 'RuneLite - Player' at (1920, 0) size 1280x720
15:23:46 | INFO | 👁️  VISION: I can see a tinderbox in slot 0 and logs in slot 1
15:23:47 | INFO | 🖱️  CLICK at (1995, 245) on 'tinderbox'
15:23:48 | INFO | 🖱️  CLICK at (2038, 245) on 'logs'
15:23:50 | INFO | ✅ SUCCESS: Fire created
```

## Current Limitations

- **Inventory calibration**: Currently needs manual calibration for inventory slot positions
- **Movement**: Basic movement away from fires (pathfinding not implemented)
- **Error recovery**: Basic retry logic only
- **Single task**: Only firemaking implemented (woodcutting, agility, combat planned)

## Roadmap

### Phase 1: Basic Firemaking ✓
- [x] Window detection
- [x] Screenshot capture
- [x] VLM integration
- [x] Basic firemaking loop

### Phase 2: Visual Calibration (In Progress)
- [ ] Automatic inventory detection
- [ ] Game tile detection for movement
- [ ] Minimap integration

### Phase 3: CRADLE Loop
- [ ] Self-reflection on failures
- [ ] Dynamic skill generation
- [ ] Episodic memory

### Phase 4: Expansion
- [ ] Woodcutting (tree detection, banking)
- [ ] Agility courses
- [ ] Combat (prayer switching, movement)

## Safety & Ethics

⚠️ **Important Notes**:

- This is an **educational/research project** exploring VLM applications in gaming
- Use at your own risk - bot detection is possible
- Designed to look human-like with randomized movements/delays
- Not for commercial use or unfair advantages

## Troubleshooting

### "wmctrl not found"
Install wmctrl: `sudo pacman -S wmctrl`

### "Window manager not ready"
Make sure RuneLite is running and visible

### "VLM not initialized"
Set `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` environment variable

### Window detection fails with tiling manager
Try refreshing: `python firemaking_agent.py --refresh-window`

### Agent clicks wrong positions
Run inventory calibration (coming soon) or manually adjust in `skills.py`

## Contributing

This is a personal learning project, but suggestions welcome!

## License

Educational use only. OSRS and RuneLite are property of their respective owners.
