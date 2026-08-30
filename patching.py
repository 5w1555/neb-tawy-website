import polib

PO_PATH = "locale/fr/LC_MESSAGES/django.po"

# Exact fixes for entries flagged in review.
# Key = exact msgid text, Value = corrected msgstr.
fixes = {
    # Real mistranslations
    "Host:": "Hébergeur :",
    "Signature Guidance": "Accompagnement signature",
    "Book": "Réserver",
    "Focused Reading": "Tirage ciblé",
    "Opportunity to ask questions during the reading": "Possibilité de poser des questions pendant le tirage",
    "30-minutes private phone call reading": "Séance téléphonique privée de 30 minutes",
    "Your reading has been reserved.": "Votre tirage a été réservé.",
    "Three-card draw": "Tirage de trois cartes",
    "Six-card draw": "Tirage de six cartes",

    # CTA consistency — unify to infinitive form, matching the nav "Book" fix above
    "Book a reading": "Réserver un tirage",
    "Book this session": "Réserver cette séance",

    # "Divination wands" terminology consistency — was rendered two ways
    # (baguettes divinatoires vs baguettes de divination) for the same object.
    # Standardizing on "baguettes de divination" to match the existing
    # "baguettes de sourcier" (dowsing rods) pattern elsewhere in the file.
    "The most complete experience Neb Tawy offers. For 45 minutes, we connect "
    "live to talk through your situation. Tarot guides the session, and where it "
    "feels right, divination wands are used as well — reserved exclusively for "
    "live video sessions.": (
        "L'expérience la plus complète proposée par Neb Tawy. Pendant 45 minutes, "
        "nous nous connectons en direct pour discuter de votre situation. Le tarot "
        "guide la séance et, lorsque cela semble approprié, nous utilisons également "
        "des baguettes de divination — une technique réservée exclusivement aux "
        "séances vidéo en direct."
    ),
}

po = polib.pofile(PO_PATH)

applied = []
missing = []

for entry in po:
    if entry.msgid in fixes:
        entry.msgstr = fixes[entry.msgid]
        applied.append(entry.msgid)

for msgid in fixes:
    if msgid not in applied:
        missing.append(msgid)

po.save(PO_PATH)

print(f"Applied {len(applied)} fixes:")
for m in applied:
    print(f"  - {m[:60]!r}")

if missing:
    print(f"\nWARNING: {len(missing)} fix(es) not found in file (check exact msgid text):")
    for m in missing:
        print(f"  - {m[:60]!r}")