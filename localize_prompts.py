import json
import asyncio
from googletrans import Translator

from default_voices import edge_default_voice_mapping

# Read the English base prompts
with open("prompts/summary_prompt.en.txt", "r", encoding="utf-8") as f:
    base_summary_prompt_en = f.read()

with open("prompts/optimization_prompt.en.txt", "r", encoding="utf-8") as f:
    base_optimization_prompt_en = f.read()

async def translate_prompts():
    translator = Translator()
    localized_summary_prompts = {}
    localized_optimization_prompts = {}

    for lang_code in edge_default_voice_mapping:
        # If English, just reuse the base text (no translation needed)
        if lang_code == 'en':
            localized_summary_prompts[lang_code] = base_summary_prompt_en
            localized_optimization_prompts[lang_code] = base_optimization_prompt_en
            continue

        # Translate summary prompt
        try:
            print(f"Translating summary prompt to '{lang_code}'...")
            result_summary = await translator.translate(base_summary_prompt_en, dest=lang_code)
            localized_summary_prompts[lang_code] = result_summary.text
        except Exception as e:
            localized_summary_prompts[lang_code] = (
                f"Translation error for '{lang_code}': {str(e)}"
            )

        # Translate optimization prompt
        try:
            print(f"Translating optimization prompt to '{lang_code}'...")
            result_optimization = await translator.translate(base_optimization_prompt_en, dest=lang_code)
            localized_optimization_prompts[lang_code] = result_optimization.text
        except Exception as e:
            localized_optimization_prompts[lang_code] = (
                f"Translation error for '{lang_code}': {str(e)}"
            )

    return localized_summary_prompts, localized_optimization_prompts

def main():
    # Run the async translation function in an event loop
    summary_prompts, optimization_prompts = asyncio.run(translate_prompts())

    # Write the localized summary prompts to JSON
    with open("prompts/localized_summary_prompts.json", "w", encoding="utf-8") as f_summary:
        json.dump(summary_prompts, f_summary, ensure_ascii=False, indent=4)

    # Write the localized optimization prompts to JSON
    with open("prompts/localized_optimization_prompts.json", "w", encoding="utf-8") as f_opt:
        json.dump(optimization_prompts, f_opt, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
