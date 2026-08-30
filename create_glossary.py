# create_glossary.py
import deepl

DEEPL_API_KEY = "ec9cd9d3-e769-42f3-8e6a-0ba0b173fba8:fx"
translator = deepl.Translator(DEEPL_API_KEY)

# English -> French pairs. Left side must match your .po msgid text EXACTLY
# (or at least the word/phrase within it) for DeepL to substitute it.
glossary_entries = {
    "reading": "tirage",
    "guidance": "accompagnement",
    "readings": "tirages",
}

glossary = translator.create_glossary(
    "neb-tawy-terms",
    source_lang="EN",
    target_lang="FR",
    entries=glossary_entries,
)

print(f"Glossary created. ID: {glossary.glossary_id}")
print("Save this ID — you'll need it for every translation call.")