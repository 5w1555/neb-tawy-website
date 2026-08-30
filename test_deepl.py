# test_deepl.py
import deepl

DEEPL_API_KEY = "ec9cd9d3-e769-42f3-8e6a-0ba0b173fba8:fx"

translator = deepl.Translator(DEEPL_API_KEY)

usage = translator.get_usage()
print(f"Character usage: {usage.character.count} / {usage.character.limit}")

test_strings = [
    "Book a reading",
    "Private guidance · from €25",
    "Each reading is private and centered on your question or intention.",
]

for text in test_strings:
    result = translator.translate_text(text, source_lang="EN", target_lang="FR")
    print(f"{text!r} -> {result.text!r}")