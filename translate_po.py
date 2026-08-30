import time
import deepl
import polib

DEEPL_API_KEY = "ec9cd9d3-e769-42f3-8e6a-0ba0b173fba8:fx"
GLOSSARY_ID = "cffbbfd2-96bb-4a18-9288-7311bab5a0d8"
PO_PATH = "locale/fr/LC_MESSAGES/django.po"

translator = deepl.Translator(DEEPL_API_KEY)
po = polib.pofile(PO_PATH)

entries_to_translate = [e for e in po if not e.msgstr]
print(f"{len(entries_to_translate)} entries need translation.")

for i, entry in enumerate(entries_to_translate, 1):
    max_attempts = 4
    for attempt in range(1, max_attempts + 1):
        try:
            result = translator.translate_text(
                entry.msgid,
                source_lang="EN",
                target_lang="FR",
                glossary=GLOSSARY_ID,
            )
            entry.msgstr = result.text
            print(f"[{i}/{len(entries_to_translate)}] OK: {entry.msgid[:40]!r}")
            break
        except deepl.exceptions.TooManyRequestsException:
            wait = 10 * attempt  # 10s, 20s, 30s, 40s back-off
            print(f"  Rate limited, waiting {wait}s (attempt {attempt}/{max_attempts})...")
            time.sleep(wait)
        except Exception as e:
            print(f"  FAILED on {entry.msgid[:40]!r}: {type(e).__name__}: {e}")
            break
    else:
        print(f"  Giving up on this entry after {max_attempts} attempts — left blank, rerun script later to retry.")

    # Save progress after every entry, not just at the end —
    # if the script dies partway through, nothing already done is lost.
    po.save(PO_PATH)

    # Pace requests so we don't trigger rate limiting in the first place
    time.sleep(1)

print("Done. Re-run this script anytime — it only translates entries still blank.")