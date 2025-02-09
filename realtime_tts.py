"""
RealtimeTTS Module

This module provides text-to-speech playback using two different engines:
  - KokoroEngine: The default engine for TTS.
  - EdgeEngine: An alternative engine used when explicitly requested (via the --edge flag)
                or when the detected language isn't supported by Kokoro.

Both engines and their audio streams are set up as soon as the module loads, 
minimizing delays when you start playback. The module also features:
  - Voice prewarming for faster response times.
  - Automatic language detection to choose the right voice.
  - Interactive playback controls:
      * F8 to pause/resume.
      * ESC to stop playback.
  - Optional text processing (like summarization) before speaking.

Key functions:
  - prewarm_voices: Preloads specified voices for KokoroEngine.
  - select_voice: Determines the appropriate voice based on engine type and language.
  - read_text_aloud: Detects language, sets up the voice, and reads the text aloud with controls.
  - speak_text: A convenience wrapper for read_text_aloud.

Use this module to convert text into speech efficiently with minimal startup latency.
"""

import time
import keyboard
from langdetect import detect, detect_langs, LangDetectException
from prepare_text import prepare_text_for_speech

# Import TTS engine classes and the audio stream wrapper.
from RealtimeTTS import TextToAudioStream, EdgeEngine, KokoroEngine

# Pre-create the engine instances (avoiding latency on every call).
EDGE_ENGINE = EdgeEngine(rate=0, pitch=0, volume=0)
# Use default voice "af_heart" (American English) and default language code "a" for Kokoro.
KOKORO_ENGINE = KokoroEngine(default_lang_code="a", default_voice="af_heart", debug=False)

# Pre-create one stream per engine.
EDGE_STREAM = TextToAudioStream(EDGE_ENGINE)
KOKORO_STREAM = TextToAudioStream(KOKORO_ENGINE)

from default_voices import edge_default_voice_mapping, kokoro_default_voice_mapping

def prewarm_voices(*voice_keys):
    """
    Prewarms the Kokoro TTS engine for the specified voices.
    
    Call this method with one or more simple voice keys. For example:
        prewarm_voices("a", "zn")
    will prewarm the English (key "a") and Chinese (key "zn") voices.
    
    Args:
        *voice_keys: One or more keys corresponding to the voices to prewarm.
                     Available keys include:
                       - "a": American English (af_heart)
                       - "b": Alternative English (bf_emma)
                       - "j": Japanese (jf_alpha)
                       - "z" or "zn": Mandarin Chinese (zf_xiaobei)
                       - "e": Spanish (ef_dora)
                       - "f": French (ff_siwis)
                       - "h": Hindi (hf_alpha)
                       - "i": Italian (if_sara)
                       - "p": Brazilian Portuguese (pf_dora)
    """
    # Mapping of simple keys to (voice_name, warmup_text)
    prewarm_map = {
        "a": ("af_heart", "Warm up"),
        #"b": ("bf_emma", "Warm up"),
        "j": ("jf_alpha", "準備中"),
        "z": ("zf_xiaobei", "预热"),
        "zn": ("zf_xiaobei", "预热"),  # alias for Chinese
        "e": ("ef_dora", "Preparando"),
        "f": ("ff_siwis", "Préchauffage"),
        "h": ("hf_alpha", "तैयारी"),
        "i": ("if_sara", "Riscaldamento"),
        "p": ("pf_dora", "Aquecendo")
    }
    
    for key in voice_keys:
        if key not in prewarm_map:
            print(f"Voice key '{key}' not found for prewarming.")
            continue
        voice, text = prewarm_map[key]
        print(f"Prewarming voice: {voice} (key: {key})")
        KOKORO_ENGINE.set_voice(voice)
        # Create a temporary stream instance to play the warmup text muted.
        TextToAudioStream(KOKORO_ENGINE).feed([text]).play(muted=True)


def select_voice(engine_type, detected_lang):
    """
    Select a default voice based on the engine type and detected language.
    """
    if engine_type == 'edge':
        return edge_default_voice_mapping.get(detected_lang, 'en-US-EmmaMultilingualNeural')
    elif engine_type == 'kokoro':
        return kokoro_default_voice_mapping.get(detected_lang, 'af_heart')
    else:
        return None

def shutdown():
    """
    Clean up the engine and stream instances before exiting the program.
    """
    EDGE_STREAM.stop()
    KOKORO_STREAM.stop()
    EDGE_ENGINE.shutdown()
    KOKORO_ENGINE.shutdown()

def read_text_aloud(text, engine_type='kokoro', post_process="", hotkey_to_use='pause', provider='openrouter'):
    """
    Detects the language of the text, selects a suitable voice, and plays the text aloud
    using the pre-instantiated TTS engine and its dedicated stream.
    
    Playback controls:
      - F8: Pause/resume.
      - ESC: Stop playback.
    """
    try:
        # Use detect_langs to get probabilities.
        detected_langs = detect_langs(text)
        print(f"Detected languages for text {text} with probabilities:")
        for lang in detected_langs:
            print(f"  {lang.lang}: {lang.prob:.2f}")
        detected_lang = detected_langs[0].lang
        print(f"Using detected language: {detected_lang} (Probability: {detected_langs[0].prob:.2f})")
    except LangDetectException:
        print("Language detection failed. Defaulting to English.")
        detected_lang = 'en'
    except Exception as e:
        print(f"Error during language detection: {e}")
        detected_lang = 'en'

    selected_voice = select_voice(engine_type, detected_lang)

    if engine_type == 'kokoro' and detected_lang not in kokoro_default_voice_mapping:
        print(f"No Kokoro voice available for '{detected_lang}'. Switching to Edge.")
        engine_type = 'edge'
        selected_voice = select_voice(engine_type, detected_lang)

    print(f"Using voice: {selected_voice}")

    if engine_type == 'edge':
        engine = EDGE_ENGINE
        stream = EDGE_STREAM
    else:
        engine = KOKORO_ENGINE
        stream = KOKORO_STREAM

    engine.set_voice(selected_voice)
    
    if post_process:
        if post_process == 'summary':
            text = prepare_text_for_speech(text, create_summary=True, provider=provider, detected_lang=detected_lang)
        elif post_process == 'optimization':
            text = prepare_text_for_speech(text, create_optimization=True, provider=provider, detected_lang=detected_lang)

    stream.feed(text).play_async(log_synthesized_text=True, fast_sentence_fragment_allsentences=False)

    # Start time to delay pause/resume hotkey reaction for 1 second.
    start_time = time.time()
    is_playing = True
    while stream.is_playing():
        # Only react to the hotkey if more than 1 second has passed.
        if keyboard.is_pressed(hotkey_to_use) and (time.time() - start_time >= 1):
            if is_playing:
                stream.pause()
                print("Paused")
            else:
                stream.resume()
                print("Resumed")
            is_playing = not is_playing
            while keyboard.is_pressed(hotkey_to_use):
                time.sleep(0.1)  # debounce delay
        if keyboard.is_pressed('esc'):
            print("Stopping stream...")
            stream.stop()
            print("Stream stopped...")
            break
        time.sleep(0.01)
    print("Finished reading.")


def speak_text(text, engine_type='kokoro', post_process="", hotkey_to_use='pause', provider='openrouter'):
    """
    Convenience function to speak the given text using the selected engine.
    """
    read_text_aloud(text, engine_type, post_process, hotkey_to_use=hotkey_to_use, provider=provider)
