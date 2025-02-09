# ReadAloud

*Instantly converts selected text or URL content into speech*

## About the Project

ReadAloud speaks the text you have selected. If you highlight a URL, it retrieves the webpage content and can summarize it before reading. 

> **Note:** the project has only been tested on Windows so far; Linux support is in progress.

## Key Features

- 🚀 **Free to use**: TTS and LLM features are completely free
- 🔥 **Instant Response**: Press hotkey => hear speech
- 🌍 **Multilangual**: 70+ languages available
- 🌐 **Smart URL Processing**: Website content extraction with optional summarization
- 🎙️ **Dual TTS Engine System**: 
  - Kokoro Engine: Fast, offline synthesis
  - Edge TTS: Cloud-based, high-quality alternative
- ⚡ **Performance Optimization**: Optional voice prewarming for frequently used languages

## System Requirements

- **Operating System**: Windows 10 or later
- **Software**: Python 3.9 or higher

## Installation

1. **Clone the Repository**:
```bash
git clone https://github.com/KoljaB/ReadAloud.git
cd ReadAloud
```

2. **Set Up Virtual Environment**:
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate.bat
# Linux/macOS:
# source venv/bin/activate

# Update pip
python -m pip install --upgrade pip
```

3. **Install Dependencies**:
```bash
python install.py
```
The installation script will:
- Install required Python packages
- Detect and set up CUDA if available

4. **Configure API Keys** (Required for URL processing):

Set environment variables:
```plaintext
set OPENROUTER_API_KEY=<your_key_here>
set OPENAI_API_KEY=<your_key_here>
```


## Usage

### Quick Start
```bash
python main.py [arguments]
```

### Basic Controls

- **Default Hotkey** (Pause key): 
  - First press: Start reading selected text
  - Second press: Pause/Resume
- **ESC**: Stop current playback

### Command Line Arguments

| Argument              | Description                                    | Default |
|----------------------|------------------------------------------------|---------|
| `--openrouter`       | Use OpenRouter (gemini-2.0-pro) for summaries | False   |
| `--openai`           | Use OpenAI (gpt-4o-mini) for summaries        | False   |
| `--hotkey=<key>`     | Set custom hotkey                             | "Pause" |
| `--summary`          | Enable URL content summarization               | False   |
| `--optimize`         | Enable TTS content optimization                | False   |
| `--edge`             | Force Edge TTS engine usage                    | False   |
| `--prewarm=<keys>`   | Preload specific language voices              | None    |


### Voice Prewarming

Reduce initial Kokoro TTS latency by preloading frequently used voices:
```bash
python main.py --prewarm=a,e,j,zn
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

## Additional Information

If not called with --edge parameter ReadAloud will try to prefer Kokoro synthesis first because it's faster and more reliable. If the language is not supported by Kokoro or the --edge parameter was used, ReadAloud will synthesize using Edge TTS.

1. **Summary and Optimize** parameters require:
   - Either `OPENROUTER_API_KEY` or `OPENAI_API_KEY` environment variable set to a valid api key
   - Active internet connection

2. **Engine Requirements**:
   - EdgeEngine needs active internet connection
   - KokoroEngine works offline after initial setup

## Contributions

🖥️ Cross-platform compatibility (macOS/Linux) wanted:
- extracting marked/selected text
- testing hotkey functionality

## License

MIT License