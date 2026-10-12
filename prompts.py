"""Prompt definitions for the two-agent ad-script pipeline.

Agent 1 (Strategist): brief -> consumer-psychology strategy as strict JSON.
Agent 2 (Scriptwriter): brief + strategy -> full video script + shot list.

Tuned for a small (3B) model: short rules, an explicit output shape, a worked
few-shot example, and anti-generic guardrails.

Key guarantees:
- Output language follows the brief's language (F1).
- Few-shot examples are language-matched (EN/FR) so the model stylises directly
  in the target language instead of translating an English template (F9).
- CTA matches the product type (physical vs app vs service) (F3).
- Never copy numbers/phrases from the examples (F8).
- HOOK and PROBLEM are complete, natural sentences (F11).
"""

import re

BRIEF_FIELDS = (
    "brand",
    "product",
    "details",
    "audience",
    "goal",
    "platform",
    "product_type",
    "tone",
)

REQUIRED_STRATEGY_KEYS = (
    "language",
    "audience",
    "pains",
    "desires",
    "positioning",
    "hook_angles",
    "emotion_target",
)

DEFAULT_TONE = "confident and clear"
DEFAULT_PLATFORM = "Instagram Reels / TikTok"
DEFAULT_PRODUCT_TYPE = "unspecified - infer it from the description and goal"

EN = "en"
FR = "fr"

_FRENCH_STOPWORDS = {
    "le", "la", "les", "des", "une", "un", "pour", "qui", "avec", "vous", "nous",
    "est", "sont", "dans", "sur", "plus", "votre", "notre", "et", "ou", "au", "aux",
    "du", "de", "ce", "cette", "son", "ses", "mais", "tout", "tous", "tre", "avoir",
}
_ENGLISH_STOPWORDS = {
    "the", "a", "an", "and", "or", "for", "with", "you", "we", "is", "are", "in",
    "on", "to", "of", "your", "our", "this", "that", "it", "they", "but", "all",
    "be", "have", "who",
}


def detect_language(text: str) -> str:
    """Lightweight heuristic returning 'fr' or 'en' (defaults to 'en')."""
    text = (text or "").lower()
    if not text.strip():
        return EN
    if re.search(r"[àâäéèêëïîôöùûüçœ]", text):
        return FR
    words = set(re.findall(r"[a-z]+", text))
    french_hits = len(words & _FRENCH_STOPWORDS)
    english_hits = len(words & _ENGLISH_STOPWORDS)
    return FR if french_hits > english_hits else EN


def _strategy_language_code(strategy: dict) -> str:
    lang = str((strategy or {}).get("language", "")).lower()
    if "fr" in lang or "fran" in lang:
        return FR
    if "en" in lang or "ang" in lang:
        return EN
    return ""


# --------------------------------------------------------------------------- #
# Agent 1: Strategist
# --------------------------------------------------------------------------- #

SYSTEM_STRATEGIST = """You are a senior consumer-psychology strategist for direct-response advertising.
You read a product brief and produce a compact strategy a copywriter will use.

Rules:
- Write everything in the SAME language as the brief. If the brief is French, write French. Never translate to English.
- Be specific and concrete. Never use filler such as "in today's world".
- pains are real problems or frustrations the customer ALREADY feels, in their own words. NEVER put a benefit, a want, or a to-do in pains.
- desires are what the customer WANTS to achieve or feel. NEVER put a problem in desires.
  Example - good pain: "Vous oubliez de boire."  Wrong pain (it is a desire): "Rester hydraté toute la journée."
- pains must be concrete and everyday (cost, time, comfort, durability). NEVER invent fears about theft, humiliation, or social rejection.
- Never write a pain that contradicts the product's stated features (if the product is "light", do not say it is "heavy").
- Use the exact product and brand from the brief. NEVER replace the product with a different item (if the brief says "crampons", never write "chaussettes").
- Use the FEATURES listed in the brief (DETAILS) to ground the positioning and hook_angles.
- hook_angles must be 3 DIFFERENT angles (e.g. problem, curiosity, social proof).
- Use only facts stated in the brief. Never invent numbers or claims.
- If writing in French, check gender and agreement (une bouteille -> elle; l'eau fraîche, not frais) and contractions (de boire, not d'boire).
- Answer with a single valid JSON object only. No markdown, no commentary.

Return exactly this JSON shape:
{
  "language": "the language of the brief, e.g. French",
  "audience": "one sentence describing the buyer",
  "pains": ["pain 1", "pain 2", "pain 3"],
  "desires": ["desire 1", "desire 2", "desire 3"],
  "positioning": "one sentence: what the product is and who it is for",
  "hook_angles": ["angle 1", "angle 2", "angle 3"],
  "emotion_target": "one word emotion the ad should trigger"
}"""

STRATEGIST_EXAMPLE_USER_EN = """BRAND: BlendGo
PRODUCT: A rechargeable portable blender that makes a smooth smoothie in 30 seconds. USB-C, 16oz, blends in the bottle you drink from.
DETAILS: USB-C rechargeable, blends straight in the 16oz bottle, fits in a gym bag.
AUDIENCE: gym-goers and busy professionals aged 22-40
GOAL: sell the product
PLATFORM: Instagram Reels
PRODUCT TYPE: physical product
TONE: energetic and motivating"""

STRATEGIST_EXAMPLE_ASSISTANT_EN = """{
  "language": "English",
  "audience": "Gym-goers and busy professionals who want a healthy drink without the hassle of a full kitchen blender.",
  "pains": ["Never enough time to eat well on the go", "Smoothie shops cost a fortune", "Kitchen blenders are a pain to clean"],
  "desires": ["A fresh smoothie anywhere", "Save money every week", "Hit protein goals easily"],
  "positioning": "BlendGo is a rechargeable portable blender that makes a smooth smoothie anywhere in 30 seconds.",
  "hook_angles": ["Speed: a real smoothie in 30 seconds, anywhere", "Money: stop paying for smoothie-shop cups", "Convenience: blend and drink from the same bottle"],
  "emotion_target": "motivation"
}"""

STRATEGIST_EXAMPLE_USER_FR = """BRAND: SafePack
PRODUCT: Un sac à dos antivol avec poche verrouillée, port de charge USB et compartiment ordinateur, pensé pour les déplacements en ville.
DETAILS: poche verrouillée, port de charge USB, compartiment ordinateur rembourré.
AUDIENCE: citadins et étudiants de 20 à 35 ans
GOAL: vendre le produit
PLATFORM: Instagram Reels
PRODUCT TYPE: produit physique
TONE: dynamique et rassurant"""

STRATEGIST_EXAMPLE_ASSISTANT_FR = """{
  "language": "French",
  "audience": "Citadins et étudiants qui transportent un ordinateur et des affaires de valeur en ville et craignent de se les faire voler.",
  "pains": ["Peur de se faire voler dans les transports", "Trop d'affaires à ranger", "Téléphone déchargé en fin de journée"],
  "desires": ["Se déplacer sans stress", "Tout garder trié et sécurisé", "Recharger son téléphone partout"],
  "positioning": "SafePack est un sac à dos antivol avec poche verrouillée et port USB, conçu pour protéger vos affaires en ville.",
  "hook_angles": ["Sécurité : vos affaires à l'abri des pickpockets", "Organisation : une place pour chaque objet", "Confort : rechargez votre téléphone en déplacement"],
  "emotion_target": "confiance"
}"""

STRATEGIST_USER_TEMPLATE = """BRAND: {brand}
PRODUCT: {product}
DETAILS: {details}
AUDIENCE: {audience}
GOAL: {goal}
PLATFORM: {platform}
PRODUCT TYPE: {product_type}
TONE: {tone}"""


# --------------------------------------------------------------------------- #
# Agent 2: Scriptwriter
# --------------------------------------------------------------------------- #

SYSTEM_SCRIPTWRITER = """You are an award-winning direct-response video ad copywriter.
You turn a strategy into a short, high-converting video commercial script.

Rules:
- Write the whole script and shot list in the SAME language as the brief. Never translate to English.
- Follow the structure exactly, in this order: HOOK, PROBLEM, SOLUTION, CTA.
- The HOOK must state the product's single biggest concrete benefit within the first 3 seconds.
- The HOOK must open on the product's biggest concrete benefit OR a real frustration listed in the strategy's pains. Never invent a fear, humiliation, or problem that is not in the brief or the strategy.
- The HOOK and PROBLEM must each be ONE complete, natural sentence in the customer's voice. Never output fragments or lists.
- Choose ONE way to address the customer and keep it consistent in EVERY line. French: use "tu" OR "vous" (never mix them). English: use "you". Never switch to first person (je/I).
- Use the exact product and brand from the brief. Never change the product into a different item (if the brief says "crampons", never write "chaussettes").
- If writing in French, check gender and agreement (une bouteille -> elle; l'eau fraîche, not frais) and contractions (de boire, not d'boire).
- Never introduce unrelated items (coffee, tea, etc.) unless they are part of the product.
- Use only facts, numbers and claims stated in the brief. Never copy words, numbers or phrases from the examples.
- Use the customer's own words and the chosen emotion from the strategy.
- Name the product/brand in the SOLUTION and the CTA.
- Match the CTA to the product type:
    * physical product -> "Order now", "Buy now", "Pre-order"
    * app or software -> "Download", "Sign up", "Try it free"
    * service -> "Book now", "Contact us", "Get a quote"
  Never say "download" or "app" for a physical product.
- Write spoken copy that is easy to read aloud. Keep it tight.
- Then output a shot list table mapping each beat to visual, audio, and on-screen text.
- Output plain markdown only. Output ONLY the title, the four labelled lines, and the shot-list table. No notes, commentary, or extra sentences before or after."""

SCRIPTWRITER_FORMAT = """Output format (markdown):

## Title
<short working title>

**HOOK:** <biggest concrete benefit, 0-3s, one complete punchy sentence>
**PROBLEM:** <the pain, in one complete sentence in the customer's words>
**SOLUTION:** <how the product solves it, naming the brand>
**CTA:** <one clear action, naming the brand and matching the product type>

### Shot list
| # | Time | Visual | Audio / Voice-over | Text on screen |
|---|------|--------|--------------------|----------------|
| 1 | 0-3s | ... | ... | ... |
| 2 | 3-10s | ... | ... | ... |
| 3 | 10-25s | ... | ... | ... |
| 4 | 25-30s | ... | ... | ... |"""

SCRIPTWRITER_EXAMPLE_ASSISTANT_EN = """## Blend Anywhere

**HOOK:** You pay more for smoothie-shop cups than a kitchen full of fruit would cost.
**PROBLEM:** You want a healthy drink, but you never have time and cleaning a kitchen blender is a hassle.
**SOLUTION:** BlendGo is a rechargeable portable blender that turns fruit and protein into a smooth smoothie anywhere, and you drink straight from the bottle.
**CTA:** Order your BlendGo today and blend your first smoothie tomorrow.

### Shot list
| # | Time | Visual | Audio / Voice-over | Text on screen |
|---|------|--------|--------------------|----------------|
| 1 | 0-3s | Person walks past a smoothie shop, checks a price board | "You pay more for smoothie-shop cups..." | Too expensive? |
| 2 | 3-10s | Cluttered kitchen, blender parts in the sink | "...for a drink you could blend yourself." | Blenders are a hassle |
| 3 | 10-25s | Person adds fruit to BlendGo, presses a button, drinks | "BlendGo blends a smoothie anywhere." | Blend. Drink. Go. |
| 4 | 25-30s | Person smiles, holds BlendGo, store page on phone | "Order your BlendGo today." | Order now |"""

SCRIPTWRITER_EXAMPLE_ASSISTANT_FR = """## SafePack, Vos Affaires en Sécurité

**HOOK:** Dans les transports bondés, un pickpocket peut vous prendre votre ordinateur en une seconde.
**PROBLEM:** Vous ne savez jamais si vos affaires sont vraiment à l'abri quand vous êtes dans la foule.
**SOLUTION:** SafePack est un sac à dos antivol avec poche verrouillée et port USB, pour transporter et recharger vos affaires sereinement.
**CTA:** Commandez votre SafePack et déplacez-vous l'esprit tranquille.

### Shot list
| # | Time | Visual | Audio / Voice-over | Text on screen |
|---|------|--------|--------------------|----------------|
| 1 | 0-3s | Une personne dans le métro, sac sur le dos, regard inquiet | "Un pickpocket peut tout prendre en une seconde." | La peur du vol |
| 2 | 3-10s | La foule du métro, la personne change de position, anxieuse | "Vos affaires ne sont jamais vraiment à l'abri dans la foule." | Aucun contrôle |
| 3 | 10-25s | La personne ouvre la poche verrouillée de SafePack et branche son téléphone | "SafePack protège vos affaires et recharge votre téléphone." | Verrouillé et port USB |
| 4 | 25-30s | La personne souriante, sac sur le dos, marche sereinement | "Commandez votre SafePack dès aujourd'hui." | Commandez maintenant |"""

SCRIPTWRITER_USER_TEMPLATE = """STRATEGY (JSON):
{strategy}

BRIEF:
BRAND: {brand}
PRODUCT: {product}
DETAILS: {details}
AUDIENCE: {audience}
GOAL: {goal}
PLATFORM: {platform}
PRODUCT TYPE: {product_type}
TONE: {tone}

Write the video ad script now, in the SAME language as the brief."""


def normalize_brief(brief: dict) -> dict:
    """Fill missing brief fields with sensible defaults.

    Extra keys (format-specific answers such as 'offer', 'channels' or 'specs')
    are preserved as trimmed strings so per-format prompts can use them.
    """
    brief = brief or {}
    clean = {field: str(brief.get(field, "")).strip() for field in BRIEF_FIELDS}
    if not clean["tone"]:
        clean["tone"] = DEFAULT_TONE
    if not clean["platform"]:
        clean["platform"] = DEFAULT_PLATFORM
    if not clean["product_type"]:
        clean["product_type"] = DEFAULT_PRODUCT_TYPE
    for key, value in brief.items():
        if key not in BRIEF_FIELDS and value:
            clean[key] = str(value).strip()
    return clean


def _brief_text(clean: dict) -> str:
    return " ".join(
        [
            clean["brand"],
            clean["product"],
            clean["details"],
            clean["audience"],
            clean["goal"],
            clean["tone"],
        ]
    )


def build_strategist_messages(brief: dict) -> list:
    """Messages for Agent 1 (expects a JSON object reply), language-matched."""
    clean = normalize_brief(brief)
    if detect_language(_brief_text(clean)) == FR:
        example_user = STRATEGIST_EXAMPLE_USER_FR
        example_assistant = STRATEGIST_EXAMPLE_ASSISTANT_FR
    else:
        example_user = STRATEGIST_EXAMPLE_USER_EN
        example_assistant = STRATEGIST_EXAMPLE_ASSISTANT_EN
    return [
        {"role": "system", "content": SYSTEM_STRATEGIST},
        {"role": "user", "content": example_user},
        {"role": "assistant", "content": example_assistant},
        {"role": "user", "content": STRATEGIST_USER_TEMPLATE.format(**clean)},
    ]


def build_scriptwriter_messages(brief: dict, strategy: dict) -> list:
    """Messages for Agent 2 (markdown script + shot list), language-matched."""
    import json

    clean = normalize_brief(brief)
    lang = _strategy_language_code(strategy) or detect_language(_brief_text(clean))
    example = SCRIPTWRITER_EXAMPLE_ASSISTANT_FR if lang == FR else SCRIPTWRITER_EXAMPLE_ASSISTANT_EN
    strategy_text = json.dumps(strategy, ensure_ascii=False, indent=2)
    user_message = SCRIPTWRITER_USER_TEMPLATE.format(strategy=strategy_text, **clean)
    return [
        {"role": "system", "content": SYSTEM_SCRIPTWRITER + "\n\n" + SCRIPTWRITER_FORMAT},
        {"role": "assistant", "content": example},
        {"role": "user", "content": user_message},
    ]


def validate_strategy(strategy: dict) -> list:
    """Return a list of problems with a strategy dict (empty if valid)."""
    problems = []
    if not isinstance(strategy, dict):
        return ["strategy is not a JSON object"]
    for key in REQUIRED_STRATEGY_KEYS:
        if key not in strategy:
            problems.append("missing key: {0}".format(key))
    for key in ("pains", "desires", "hook_angles"):
        value = strategy.get(key)
        if not isinstance(value, list) or len(value) == 0:
            problems.append("{0} must be a non-empty list".format(key))
    return problems


if __name__ == "__main__":
    import json

    from ollama_client import OllamaClient

    sample = {
        "brand": "AquaSmart",
        "product": (
            "Une bouteille d'eau isotherme intelligente en acier inoxydable qui affiche "
            "la temperature de l'eau sur un ecran LED tactile sur le bouchon. Elle rappelle "
            "de s'hydrater toutes les heures par une vibration et garde l'eau glacee 24h "
            "ou le cafe chaud 12h."
        ),
        "audience": (
            "Les jeunes professionnels et sportifs de 25 a 40 ans qui passent de longues "
            "heures au bureau ou a la salle de sport et oublient de boire assez d'eau."
        ),
        "goal": "sell the product",
        "platform": "Instagram Reels",
        "product_type": "physical product",
        "tone": "modern and motivating",
    }

    print("detected language:", detect_language(sample["product"] + sample["audience"]))

    client = OllamaClient()
    print("\n=== AGENT 1: STRATEGIST ===")
    strategy = client.chat_json(build_strategist_messages(sample), temperature=0.3)
    print(json.dumps(strategy, indent=2, ensure_ascii=False))
    print("valid:", not validate_strategy(strategy))

    print("\n=== AGENT 2: SCRIPTWRITER ===")
    script = client.chat(
        build_scriptwriter_messages(sample, strategy),
        temperature=0.8,
        num_predict=1200,
    )
    print(script)
    client.close()
