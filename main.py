#!/usr/bin/env python
"""
Realtime TTS Website/Text Reader

This script monitors the clipboard for text selections or website URLs.
When you press a hotkey (default is Pause), it copies the current selection
and either extracts the main content from a URL or uses the text directly.
The text is then read aloud.

Controls during playback:
  - Default hotkey (Pause): Pause/resume the reading.
  - ESC: Stop the reading.

Usage:
  1. Select text or a website URL.
  2. Press the hotkey to copy the selection and start reading aloud.
  3. During playback, press the hotkey to pause/resume, and ESC to stop reading.

Pass '--hotkey=<key>' to set your own hotkey (e.g., '--hotkey=F8').
Pass '--edge' to use EdgeEngine. Otherwise, KokoroEngine is used by default.
Pass '--summarize' to apply summary post-processing on URLs.
Pass '--prewarm=<voices>' to prewarm specific voices (e.g., '--prewarm=a,e,f').
"""

import sys
import time
import signal
from fetch_text import get_main_content
from realtime_tts import speak_text, prewarm_voices
from clipboard import ClipboardTextRetriever
import keyboard

# Read the voice prewarming keys from argv.
voices_to_prewarm = None
for arg in sys.argv:
    if arg.startswith("--prewarm="):
        voices_to_prewarm = arg.split("=")[1].split(",")
        break
if voices_to_prewarm is None:
    voices_to_prewarm = ["a"]

prewarm_voices(*voices_to_prewarm)

# Determine which TTS engine to use based on the command-line argument.
if "--edge" in sys.argv:
    engine_type = 'edge'
    print("Using EdgeEngine as TTS engine.")
else:
    engine_type = 'kokoro'
    print("Using KokoroEngine as TTS engine.")

# Check if post-processing is enabled.
enable_post_process = "--summarize" in sys.argv
if enable_post_process:
    print("Post-processing enabled for URLs.")

# Check for a custom hotkey. Default is 'pause'.
default_hotkey = 'pause'
custom_hotkey = None
for arg in sys.argv:
    if arg.startswith("--hotkey="):
        custom_hotkey = arg.split("=")[1].strip()
        break
hotkey_to_use = custom_hotkey if custom_hotkey else default_hotkey

def read_website_or_text_aloud(text_or_url):
    """Checks if the clipboard has a URL or text, then reads it aloud."""
    if text_or_url.startswith("http://") or text_or_url.startswith("https://"):
        print(f"Reading website: {text_or_url}")
        main_text = get_main_content(text_or_url)
        if not main_text:
            print("Failed to extract main content from the website.")
            return
        text_to_read = main_text
        # Only enable post-processing if --post-process is passed
        post_process = enable_post_process
    else:
        print("Reading selected text from clipboard.")
        text_to_read = text_or_url
        post_process = False

    if not text_to_read:
        print("No text available to read.")
        return

    print(f"Playback started. Press {hotkey_to_use} to pause/resume, and ESC to stop reading.")
    speak_text(text_to_read, engine_type=engine_type, post_process=post_process, hotkey_to_use=hotkey_to_use)

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    print("\nCtrl+C detected. Exiting...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def main():
    print("Realtime TTS Website/Text Reader is running in the background.")
    print("Instructions:")
    print(f"  1. Select text or a website URL in any application.")
    print(f"  2. Press {hotkey_to_use} to copy the selection and start reading aloud.")
    print("  3. During reading, press the hotkey to pause/resume, and ESC to stop reading.\n")

    retriever = ClipboardTextRetriever()
    while True:
        keyboard.wait(hotkey_to_use)
        text = retriever.get_selected_text()
        read_website_or_text_aloud(text)
        time.sleep(0.2)

if __name__ == "__main__":
    main()
