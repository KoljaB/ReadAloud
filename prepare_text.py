"""
Text-to-Speech LLM Preprocessing Module

This module prepares text for speech synthesis by interfacing with an LLM API to
generate either a summarized or speech-optimized version of the input text. It
defines default settings for the model and API timeouts, and includes two
specialized prompt templates—one for creating natural, flowing summaries and
another for optimizing technical content for TTS.

The llm_tokens function can connect to either:
- OpenRouter (default), using OPENROUTER_API_KEY
- OpenAI, using OPENAI_API_KEY

The prepare_text_for_speech function formats the input text according to the
chosen prompt (summary or optimization) by replacing the {} placeholder with
the text content, then obtains the streamed response.

A sample usage in the main block demonstrates how to convert technical
installation instructions into TTS-friendly output.

Summary: Prepares text for speech synthesis by generating a summary or
optimized version via a streaming LLM API call.
"""

import os
import requests
import json

DEFAULT_MODEL_OPENAI = "gpt-4o-mini"
DEFAULT_MODEL_OPENROUTER = "google/gemini-2.0-pro-exp-02-05:free"
# DEFAULT_MODEL_OPENROUTER = "meta-llama/llama-3.1-405b-instruct:free"
# DEFAULT_MODEL_OPENROUTER = "google/gemini-2.0-flash-lite-preview-02-05:free"
# DEFAULT_MODEL_OPENROUTER = "deepseek/deepseek-r1:free"

DEFAULT_CONNECT_TIMEOUT = 5
DEFAULT_READ_TIMEOUT = 300

# Load localized prompt templates from external JSON files.
try:
    with open("prompts/localized_summary_prompts.json", "r", encoding="utf-8") as f:
        LOCALIZED_SUMMARY_PROMPTS = json.load(f)
except Exception as e:
    print(f"Error reading localized_summary_prompts.json: {e}")
    LOCALIZED_SUMMARY_PROMPTS = {
        "en": "You are an audio content specialist creating summaries. Transform the text into flowing natural speech WITHOUT ANY MARKDOWN OR LIST FORMATTING. {}"
    }

try:
    with open("prompts/localized_optimization_prompts.json", "r", encoding="utf-8") as f:
        LOCALIZED_OPTIMIZATION_PROMPTS = json.load(f)
except Exception as e:
    print(f"Error reading localized_optimization_prompts.json: {e}")
    LOCALIZED_OPTIMIZATION_PROMPTS = {
        "en": "You are a text-to-speech formatting specialist. Transform the following content into an optimal format for speech synthesis while PRESERVING EXACT CONTENT AND STRUCTURE. {}"
    }


def llm_tokens(
        prompt,
        connect_timeout=DEFAULT_CONNECT_TIMEOUT,
        read_timeout=DEFAULT_READ_TIMEOUT,
        provider="openrouter",
    ):
    """
    Call either OpenRouter or OpenAI with a prompt and yield tokens as they are received.
    Specify provider="openai" to use OpenAI, or stick with the default "openrouter".
    """

    if provider.lower() == "openai":
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            yield "\nError: OPENAI_API_KEY not set in environment."
            return

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {openai_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": DEFAULT_MODEL_OPENAI,
            "messages": [{"role": "user", "content": prompt}],
            "stream": True,
        }

    else:
        openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        if not openrouter_api_key:
            yield "\nError: OPENROUTER_API_KEY not set in environment."
            return

        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {openrouter_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": DEFAULT_MODEL_OPENROUTER,
            "messages": [{"role": "user", "content": prompt}],
            "stream": True
        }

    try:
        with requests.post(url, headers=headers, json=payload, stream=True,
                           timeout=(connect_timeout, read_timeout)) as response:
            for line in response.iter_lines():
                if not line:
                    continue
                if line.startswith(b"data: "):
                    data_part = line[len(b"data: "):].strip()
                    if data_part == b"[DONE]":
                        break
                    try:
                        data_obj = json.loads(data_part)
                        token = data_obj["choices"][0]["delta"].get("content")
                        if token:
                            yield token
                    except json.JSONDecodeError:
                        continue
    except requests.exceptions.Timeout:
        yield "\nError: Request timed out"
    except requests.exceptions.RequestException as e:
        yield f"\nError: {str(e)}"


def prepare_text_for_speech(
        text,
        connect_timeout=DEFAULT_CONNECT_TIMEOUT,
        read_timeout=DEFAULT_READ_TIMEOUT,
        create_summary=False,
        create_optimization=False,
        provider="openrouter",
        detected_lang="en",
    ):
    """
    Prepare text for speech using the LLM API. If create_summary is True,
    generate a concise TTS-friendly summary. If create_optimization is True,
    transform the text into a TTS-optimized format. You can also specify
    provider="openai" to use the OpenAI Chat Completions API.

    The chosen localized prompt (based on detected_lang) should contain a
    single '{}' placeholder which will be replaced by the provided text.
    """

    if create_summary:
        print("Creating summary")
        prompt_template = LOCALIZED_SUMMARY_PROMPTS.get(
            detected_lang, LOCALIZED_SUMMARY_PROMPTS.get("en")
        )
    elif create_optimization:
        print("Creating optimization")
        prompt_template = LOCALIZED_OPTIMIZATION_PROMPTS.get(
            detected_lang, LOCALIZED_OPTIMIZATION_PROMPTS.get("en")
        )
    else:
        # If neither summary nor optimization is requested, return the original text.
        return text

    # Replace the {} placeholder in the prompt with the text content.
    formatted_prompt = prompt_template.format(text)

    return llm_tokens(
        formatted_prompt,
        connect_timeout=connect_timeout,
        read_timeout=read_timeout,
        provider=provider
    )


if __name__ == "__main__":
    # Example usage:
    text = """
Installation#
This installation guide entails all necessary steps to set up Trafilatura.
Python#
Trafilatura runs using Python, currently one of the most frequently used programming languages.
It is tested on Linux, macOS and Windows systems and on all recent versions of Python.
Some systems already have such an environment installed, to check it just run the following command in a terminal window:
$ python3 --version # python can also work
Python 3.10.12 # version 3.6 or higher is fine
Trafilatura package#
Trafilatura is packaged as a software library available from the package repository PyPI. As such it can notably be installed with a package manager like pip
or pipenv
Additional compression algorithm for downloads
- cchardet / faust-cchardet (Python >= 3.11)
Faster encoding detection, also possibly more accurate (especially for encodings used in Asia)
- htmldate[all] / htmldate[speed]
Faster and more precise date extraction with a series of dedicated packages
- py3langid
Language detection on extracted main text
- pycurl
Faster downloads, useful where urllib3 fails
- urllib3[socks]
Downloads through SOCKS proxy with urllib3
- zstandard
Additional compression algorithm for downloads
"""

    # Replace provider="openai" with provider="openrouter" (or omit) to switch back to OpenRouter.
    tokens_generator = prepare_text_for_speech(
        text,
        create_summary=True,
        provider="openai"  # use "openrouter" for OpenRouter
    )

    for token in tokens_generator:
        print(token, end="", flush=True)
