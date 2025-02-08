```markdown
# ReadAloud: Real-Time Text & Web Content Reader

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)

ReadAloud is a lightweight text-to-speech utility that instantly converts selected text or webpage content into natural sounding speech using advanced TTS engines. Perfect for hands-free reading of articles, documents, and web content.

## Key Features

- 🔥 Instant hotkey activation (default: Pause key)
- 🌐 Automatic URL content extraction (requires Openrouter API key)
- 🎙️ Dual TTS engine support (KokoroEngine & EdgeEngine)
- 🌍 Multi-language detection & voice matching
- ⚡ Voice prewarming for zero-latency startup
- 📝 Text post-processing (summarization/optimization)
- 🖥️ Cross-platform compatibility (Windows/macOS/Linux) - TESTED ONLY UNDER WINDOWS SO FAR!

## Installation

**Prerequisites**: Python 3.8+

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate.bat  # Windows

# Clone repository
git clone https://github.com/KoljaB/ReadAloud.git
cd ReadAloud

# Install dependencies
python install.py
```

## Usage

```bash
python main.py [arguments]
```

### Basic Controls
- `Hotkey` (default Pause): Trigger text reading/pause/resume
- `ESC`: Stop current playback

### Command Line Arguments

| Argument           | Description                                  | Example                     |
|--------------------|----------------------------------------------|-----------------------------|
| `--edge`           | Use EdgeEngine instead of Kokoro            | `python main.py --edge`     |
| `--hotkey=<key>`   | Set custom hotkey                           | `--hotkey=F8`               |
| `--post-process`   | Enable content summarization for URLs       | `--post-process`            |
| `--prewarm=<keys>` | Preload specific voices                     | `--prewarm=a,e,j`           |

## Prewarming Voices

Accelerate initial TTS generation by preloading frequently used voices:

```bash
--prewarm=a,e,j,zn
```

Available voice keys:
- `a`: English (US)
- `e`: Spanish
- `j`: Japanese
- `z/zn`: Mandarin Chinese
- `f`: French
- `h`: Hindi
- `i`: Italian
- `p`: Portuguese

## Important Notes

1. **URL Processing** requires:
   - Set `OPENROUTER_API_KEY` environment variable
   - Active internet connection

2. **Engine Requirements**:
   - EdgeEngine needs internet access
   - KokoroEngine works offline after initial setup

3. **GPU Acceleration**:
   - Automatic CUDA detection during installation
   - Fallback to CPU if no compatible GPU found

## License

MIT License