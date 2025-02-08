import os
import requests
import json

DEFAULT_MODEL = "google/gemini-2.0-pro-exp-02-05:free"
#DEFAULT_MODEL = "google/gemini-2.0-flash-lite-preview-02-05:free"
#DEFAULT_MODEL = "meta-llama/llama-3.1-405b-instruct:free"
#DEFAULT_MODEL = "deepseek/deepseek-r1:free"

DEFAULT_CONNECT_TIMEOUT = 5
DEFAULT_READ_TIMEOUT = 300

SUMMARY_PROMPT = """
You are an audio content specialist creating summaries. Transform the text into flowing natural speech WITHOUT ANY MARKDOWN OR LIST FORMATTING.

CRITICAL RULES:
1. PROSE FORMATTING:
   - Use ONLY continuous paragraphs with complete sentences
   - Forbid bullet points, asterisks, or numbering symbols (*, -, 1.)
   - Replace list markers with transitional phrases:
     "First... Next... Finally" → "The first aspect... Building on this... Ultimately"
   - Connect concepts using natural speech connectors ("Furthermore", "Additionally", "However")

2. LANGUAGE PRESERVATION:
   - Maintain EXACT original language and terminology
   - Keep technical terms in original form (case-sensitive)
   - Never use symbols - always verbalize them:
     "*" → removed entirely, "#" → "number"

3. TECHNICAL CONVERSION:
   - Expand abbreviations on first mention: "AGI" → "Artificial General Intelligence (AGI)"
   - Verbalize measurements: "5GHz" → "5 gigahertz"
   - Convert code elements: "Python3" → "Python 3"

STRUCTURAL REQUIREMENTS:
- Use 3-5 short paragraphs with natural pauses
- Maintain original information hierarchy
- Preserve ALL critical numbers and specifications
- Condense content by 50-70% through distillation, not deletion

Input text (IN ORIGINAL LANGUAGE):
{text}

Generate ONLY fluent spoken prose using THE SAME LANGUAGE. Remove ALL symbols and list markers while preserving 100% of crucial technical content.

Start your answer with:
"""

OPTIMIZATION_PROMPT = """
You are a text-to-speech formatting specialist. Transform the following technical content into an optimal format for speech synthesis while PRESERVING EXACT CONTENT AND STRUCTURE.

MANDATORY RULES:
1. LANGUAGE PRESERVATION:
   - Maintain ORIGINAL LANGUAGE exactly (never translate/localize)
   - Keep mixed-language content intact (e.g., code snippets, foreign terms)
   - Preserve ALL technical terminology verbatim
   - Never paraphrase or substitute synonyms

2. TECHNICAL ACCURACY:
   - Keep numerical values/units identical (5GHz → "5 gigahertz" not "five GHz")
   - Maintain code casing exactly (Python → "Python" not "python")
   - Preserve special characters through verbal equivalents:
     • "#" → "number", "±" → "plus minus", "μ" → "micro"
     • "C++" → "C plus plus", "REST" → "R E S T"

3. STRUCTURAL FIDELITY:
   - Maintain original paragraph order and section hierarchy
   - Keep all examples/code listings in original sequence
   - Preserve emphasis markers through vocal stress cues:
     • **bold** → [emphatic tone] "Important: ..."
     • _italic_ → [slightly slower pace] "..."

TRANSFORMATION RULES:
- Convert visual elements to verbal descriptions:
  • Table: "Table shows... Column 1:... Column 2:..."
  • Chart: "Chart comparing X (left axis) to Y (right axis)..."
  • Formula: "Equation: E equals m c squared"
- Expand abbreviations context-appropriately:
  • "e.g." → "for example", "i.e." → "that is"
  • "API" → "A P I" (after full initial expansion if needed)
- Add audio navigation markers:
  • "Chapter 3:", "Step 2:", "Important Note:", "Code Block:"

Input text (IN ORIGINAL LANGUAGE):
{text}

Output ONLY the speech-optimized text using THE SAME LANGUAGE AS INPUT. Preserve every technical detail and structural element exactly.

Start your answer with:
"""

def llm_tokens(
        prompt,
        model=DEFAULT_MODEL,
        connect_timeout=DEFAULT_CONNECT_TIMEOUT,
        read_timeout=DEFAULT_READ_TIMEOUT
    ):
    """
    Call the LLM API with a prompt and yield tokens as they are received.
    """
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {openrouter_api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": True
    }

    try:
        with requests.post(url, headers=headers, json=payload, stream=True,
                           timeout=(connect_timeout, read_timeout)) as response:
            for line in response.iter_lines():
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
        model=DEFAULT_MODEL,
        connect_timeout=DEFAULT_CONNECT_TIMEOUT,
        read_timeout=DEFAULT_READ_TIMEOUT,
        create_summary=False,
        create_optimization=False,
    ):
    """
    Prepare text for speech using the LLM API. If create_summary is True, generate a concise TTS-friendly summary.
    """

    if create_summary:
        print("Creating summary")
        # Append the first five words of the input text
        prompt_template = SUMMARY_PROMPT + " " + " ".join(text.split()[:5])
    elif create_optimization:
        print("Creating optimization")
        prompt_template = OPTIMIZATION_PROMPT + " " + " ".join(text.split()[:5])
    else:
        return text

    # Format the prompt with the input text
    formatted_prompt = prompt_template.format(text=text)

    return llm_tokens(
        formatted_prompt, 
        model=model, 
        connect_timeout=connect_timeout, 
        read_timeout=read_timeout
    )


if __name__ == "__main__":
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
.
Installing Python packages#
Straightforward: Official documentation
Advanced: Pipenv & Virtual Environments
Basics#
Here is how to install Trafilatura using pip:
Open a terminal or command prompt. Please refer to this section for an introduction on command-line usage.
Type the following command:
pip install trafilatura
(pip3
where applicable)Press Enter: pip will download and install Trafilatura and its dependencies.
This project is under active development, please make sure you keep it up-to-date to benefit from latest improvements:
# to make sure you have the latest version
$ pip install --upgrade trafilatura
# latest available code base
$ pip install --force-reinstall -U git+https://github.com/adbar/trafilatura
Hint
Installation on MacOS is generally easier with brew.
Older Python versions#
In case this does not happen automatically, specify the version number:
pip install trafilatura==number
Last version for Python 3.6 and 3.7:
1.12.2
Last version for Python 3.5:
0.9.3
Last version for Python 3.4:
0.8.2
Command-line tool#
If you installed the library successfully but cannot start the command-line tool, try adding the user-level bin
directory to your PATH
environment variable.
If you are using a Unix derivative (e.g. Linux, OS X), you can achieve this by running the following command: export PATH="$HOME/.local/bin:$PATH"
.
For local or user installations where trafilatura cannot be used from the command-line, please refer to the official Python documentation and this page on finding executables from the command-line.
Additional functionality#
Compression#
Trafilatura works best if compression modules in the Python standard library are available. If this is not the case the following modules are impacted: processing of compressed HTML data (less coverage), backup HTML storage (CLI), and UrlStore in the underlying courlan library (lesser capacity).
Optional modules#
A few additional libraries can be installed for extended functionality and faster processing: language detection and faster encoding detection: the cchardet
package may not work on all systems but it is highly recommended.
$ pip install cchardet # single package only
$ pip install trafilatura[all] # all additional functionality
For infos on dependency management of Python packages see this discussion thread.
Hint
Everything works even if not all packages are installed (e.g. because installation fails).
You can also install or update relevant packages separately, trafilatura will detect which ones are present on your system and opt for the best available combination.
- brotli
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
    for token in prepare_text_for_speech(text):
        print(token, end="", flush=True)
