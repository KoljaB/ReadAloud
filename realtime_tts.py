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


# Voice mappings for EdgeEngine.
edge_default_voice_mapping = {
    # Preserving your original defaults
    'en': 'en-US-EmmaMultilingualNeural',
    'es': 'es-ES-ElviraNeural',
    'fr': 'fr-FR-DeniseNeural',
    'de': 'de-DE-SeraphinaMultilingualNeural',
    'af': 'af-ZA-AdriNeural',
    'am': 'am-ET-MekdesNeural',
    'ar': 'ar-SA-ZariyahNeural',
    'az': 'az-AZ-BanuNeural',
    'bg': 'bg-BG-KalinaNeural',
    'bn': 'bn-BD-NabanitaNeural',
    'bs': 'bs-BA-VesnaNeural',
    'ca': 'ca-ES-JoanaNeural',
    'cs': 'cs-CZ-VlastaNeural',
    'cy': 'cy-GB-NiaNeural',
    'da': 'da-DK-ChristelNeural',
    'el': 'el-GR-AthinaNeural',
    'et': 'et-EE-AnuNeural',
    'fa': 'fa-IR-DilaraNeural',
    'fi': 'fi-FI-NooraNeural',
    'fil': 'fil-PH-BlessicaNeural',
    'ga': 'ga-IE-OrlaNeural',
    'gl': 'gl-ES-SabelaNeural',
    'gu': 'gu-IN-DhwaniNeural',
    'he': 'he-IL-HilaNeural',
    'hi': 'hi-IN-SwaraNeural',
    'hr': 'hr-HR-GabrijelaNeural',
    'hu': 'hu-HU-NoemiNeural',
    'id': 'id-ID-GadisNeural',
    'is': 'is-IS-GudrunNeural',
    'it': 'it-IT-ElsaNeural',
    'iu-Cans': 'iu-Cans-CA-SiqiniqNeural',
    'iu-Latn': 'iu-Latn-CA-SiqiniqNeural',
    'ja': 'ja-JP-NanamiNeural',
    'jv': 'jv-ID-SitiNeural',
    'ka': 'ka-GE-EkaNeural',
    'kk': 'kk-KZ-AigulNeural',
    'km': 'km-KH-SreymomNeural',
    'kn': 'kn-IN-SapnaNeural',
    'ko': 'ko-KR-SunHiNeural',
    'lo': 'lo-LA-KeomanyNeural',
    'lt': 'lt-LT-OnaNeural',
    'lv': 'lv-LV-EveritaNeural',
    'mk': 'mk-MK-MarijaNeural',
    'ml': 'ml-IN-SobhanaNeural',
    'mn': 'mn-MN-YesuiNeural',
    'mr': 'mr-IN-AarohiNeural',
    'ms': 'ms-MY-YasminNeural',
    'mt': 'mt-MT-GraceNeural',
    'my': 'my-MM-NilarNeural',
    'nb': 'nb-NO-PernilleNeural',
    'ne': 'ne-NP-HemkalaNeural',
    'nl': 'nl-NL-FennaNeural',
    'pl': 'pl-PL-ZofiaNeural',
    'ps': 'ps-AF-LatifaNeural',
    'pt': 'pt-BR-FranciscaNeural',
    'ro': 'ro-RO-AlinaNeural',
    'ru': 'ru-RU-SvetlanaNeural',
    'si': 'si-LK-ThiliniNeural',
    'sk': 'sk-SK-ViktoriaNeural',
    'sl': 'sl-SI-PetraNeural',
    'so': 'so-SO-UbaxNeural',
    'sq': 'sq-AL-AnilaNeural',
    'sr': 'sr-RS-SophieNeural',
    'su': 'su-ID-TutiNeural',
    'sv': 'sv-SE-SofieNeural',
    'sw': 'sw-KE-ZuriNeural',
    'ta': 'ta-IN-PallaviNeural',
    'te': 'te-IN-ShrutiNeural',
    'th': 'th-TH-PremwadeeNeural',
    'tr': 'tr-TR-EmelNeural',
    'uk': 'uk-UA-PolinaNeural',
    'ur': 'ur-PK-UzmaNeural',
    'uz': 'uz-UZ-MadinaNeural',
    'vi': 'vi-VN-HoaiMyNeural',
    'zh': 'zh-CN-XiaoxiaoNeural',
    'zu': 'zu-ZA-ThandoNeural',
}


# Updated voice mappings for KokoroEngine.
# These voices correspond to those used in the kokoro_test.py example.
kokoro_default_voice_mapping = {
    'en': 'af_heart',    # American English
    'ja': 'jf_alpha',    # Japanese
    'zh': 'zf_xiaobei',  # Mandarin Chinese
    'es': 'ef_dora',     # Spanish
    'fr': 'ff_siwis',    # French
    'hi': 'hf_alpha',    # Hindi
    'it': 'if_sara',     # Italian
    'pt': 'pf_dora',     # Brazilian Portuguese
}


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

def read_text_aloud(text, engine_type='kokoro', post_process=False, hotkey_to_use='pause'):
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
        print("Detected languages with probabilities:")
        for lang in detected_langs:
            # Each 'lang' has attributes 'lang' and 'prob'
            print(f"  {lang.lang}: {lang.prob:.2f}")
        # Choose the most probable language (first in the list).
        detected_lang = detected_langs[0].lang
        print(f"Using detected language: {detected_lang} (Probability: {detected_langs[0].prob:.2f})")
    except LangDetectException:
        print("Language detection failed. Defaulting to English.")
        detected_lang = 'en'
    except Exception as e:
        print(f"Error during language detection: {e}")
        detected_lang = 'en'

    # First try to get a voice for the requested engine.
    selected_voice = select_voice(engine_type, detected_lang)

    # If we're using Kokoro but there's no matching voice in kokoro_default_voice_mapping,
    # switch to Edge.
    if engine_type == 'kokoro' and detected_lang not in kokoro_default_voice_mapping:
        print(f"No Kokoro voice available for '{detected_lang}'. Switching to Edge.")
        engine_type = 'edge'
        selected_voice = select_voice(engine_type, detected_lang)

    print(f"Using voice: {selected_voice}")

    # Choose the pre-created engine and stream based on engine type.
    if engine_type == 'edge':
        engine = EDGE_ENGINE
        stream = EDGE_STREAM
    else:
        engine = KOKORO_ENGINE
        stream = KOKORO_STREAM

    # Set the voice for the engine.
    engine.set_voice(selected_voice)
    
    # Optionally preprocess the text (e.g., summarization) if post_process is True.
    if post_process:
        text = prepare_text_for_speech(text, create_summary=True)

    # Feed the text into the pre-created stream and play asynchronously.
    stream.feed(text).play_async(log_synthesized_text=True, fast_sentence_fragment_allsentences=False)

    is_playing = True
    while stream.is_playing():
        if keyboard.is_pressed(hotkey_to_use):
            if is_playing:
                stream.pause()
                print("Paused")
            else:
                stream.resume()
                print("Resumed")
            is_playing = not is_playing
            time.sleep(0.3)  # debounce delay
        if keyboard.is_pressed('esc'):
            print("Stopping reading...")
            stream.stop()
            break
        time.sleep(0.1)
    print("Finished reading.")


def speak_text(text, engine_type='kokoro', post_process=False, hotkey_to_use='pause'):
    """
    Convenience function to speak the given text using the selected engine.
    """
    read_text_aloud(text, engine_type, post_process, hotkey_to_use=hotkey_to_use)
