"""Per-format prompt definitions for the multi-format copywriting pipeline.

Phase 1 keeps the proven video-ad prompts untouched: the ``video_ad`` format
delegates to :mod:`prompts`, so existing behaviour cannot regress. Every other
format is built here on top of a shared quality-rule core (product fidelity,
single register, language lock, no invented facts) plus a format-specific
role, rules and output shape.

Public API
----------
build_strategist_messages(brief, format_key="video_ad")
build_writer_messages(brief, strategy, format_key="video_ad")
writer_spec(format_key)
"""

import prompts
from prompts import FR, EN, detect_language, normalize_brief

# Fields handled by the shared brief form; anything else in the brief is a
# format-specific extra answer that must still reach the model.
STANDARD_FIELDS = set(prompts.BRIEF_FIELDS)


def _extras(clean):
    """Return [(field, value), ...] for non-standard (format-specific) answers."""
    return [
        (key, value)
        for key, value in clean.items()
        if key not in STANDARD_FIELDS and value
    ]


def _extras_text(clean):
    return "\n".join(
        "{0}: {1}".format(key.replace("_", " ").upper(), value)
        for key, value in _extras(clean)
    )

# --------------------------------------------------------------------------- #
# Shared writer core (anti-hallucination / style rules reused by all formats)
# --------------------------------------------------------------------------- #

SHARED_WRITER_RULES = """Global rules (apply to every format):
- Write everything in the SAME language as the brief. If the brief is French, write French. Never translate to English.
- Use the EXACT product and brand from the brief. Never swap the product for a different item (if the brief says "crampons", never write "chaussettes").
- Use only facts, features and numbers stated in the brief (DETAILS). Never invent claims, statistics, testimonials or guarantees.
- Choose ONE way to address the reader and keep it consistent everywhere. French: "tu" OR "vous" (never mix). English: "you". Never switch to first person (je/I).
- If writing in French, check gender and agreement (une bouteille -> elle; l'eau fraîche, not frais) and contractions (de boire, not d'boire).
- Never introduce unrelated items unless they are part of the product.
- Use the customer's own words and the chosen emotion from the strategy.
- Name the product/brand where it helps conversion.
- Match the call to action to the product type: physical product -> order/buy/pre-order; app or software -> download/sign up/try free; service -> book/contact/get a quote.
- If a required detail is unknown, write a clearly bracketed placeholder like [testimonial] instead of inventing one.
- Output plain markdown ONLY, with exactly the sections requested below. No notes, no commentary, no extra sentences before or after."""

_FALLBACK_WRITER_ROLE = "You are a senior direct-response copywriter."


def _not_video(format_key):
    return bool(format_key) and format_key != "video_ad"


# --------------------------------------------------------------------------- #
# Per-format specifications
# --------------------------------------------------------------------------- #
# Each spec: role (str), rules (str), output_format (str), examples {EN, FR}

_FORMAT_SPECS = {
    "landing_page": {
        "name": "Landing Page",
        "role": "You are a conversion copywriter who writes high-converting landing pages.",
        "rules": (
            "- Follow the exact section order below.\n"
            "- The headline states the single biggest concrete benefit in one punchy sentence.\n"
            "- Each benefit block pairs a real feature from DETAILS with the outcome it creates.\n"
            "- The final CTA repeats one clear action matching the product type."
        ),
        "output_format": """## Headline
<one punchy sentence, biggest benefit>

## Subheadline
<one supporting sentence>

## Hero CTA
<button label + one line>

## Problem
<2-3 sentences on the real frustration from the strategy's pains>

## Solution
<one short paragraph naming the brand, then 3 benefit blocks:>
- **<Benefit title>** - <feature from DETAILS + outcome>
- **<Benefit title>** - <feature from DETAILS + outcome>
- **<Benefit title>** - <feature from DETAILS + outcome>

## Social proof
<one line; use bracketed placeholder like "[client name]" if no fact is given>

## Offer
<what the reader gets, from the brief only>

## Final CTA
<one clear action matching the product type>

## FAQ
**Q:** <likely objection>
**A:** <honest answer from the brief>
**Q:** <likely objection>
**A:** <honest answer from the brief>""",
        "examples": {
            EN: """## Wake Up Without the Back Pain
**Subheadline:** CloudNine is the mattress-in-a-box that gives side sleepers real support from night one.

**Hero CTA:** Shop CloudNine - free 100-night trial

## Problem
You wake up stiff and tired, and your old mattress gives your back no support. You keep putting off buying a new one because shopping for mattresses feels like a trap.

## Solution
CloudNine is a mattress-in-a-box built with [support layers] for side sleepers, so your spine stays aligned all night.
- **Support where you need it** - [support layers] cradle your shoulders and hips instead of letting them sink.
- **Cool all night** - [breathable cover] keeps heat from building up.
- **Easy setup** - [unboxes and expands] so you sleep on it the same day.

## Social proof
[testimonial]

## Offer
100-night trial, so you can test it risk-free.

## Final CTA
Order your CloudNine today and wake up without the ache.

## FAQ
**Q:** Will it feel too firm for a side sleeper?
**A:** It is built with [support layers] to keep side sleepers aligned.
**Q:** What if I don't like it?
**A:** The 100-night trial lets you send it back.""",
            FR: """## Réveillez-vous Sans Mal de Dos
**Sous-titre :** CloudNine est le matelas livré en boîte qui soutient vraiment les dormeurs sur le côté dès la première nuit.

**CTA principal :** Commander CloudNine - essai 100 nuits

## Problème
Vous vous réveillez raide et fatigué, et votre vieux matelas ne soutient pas votre dos. Vous repoussez l'achat parce que choisir un matelas ressemble à un piège.

## Solution
CloudNine est un matelas livré en boîte, conçu avec [couches de soutien] pour les dormeurs sur le côté, afin que votre colonne reste alignée toute la nuit.
- **Un soutien ciblé** - [couches de soutien] épousent les épaules et les hanches au lieu de les laisser s'enfoncer.
- **Frais toute la nuit** - [housse respirante] empêche la chaleur de s'accumuler.
- **Installation facile** - [se déplie tout seul] pour dormir dessus le jour même.

## Preuve sociale
[témoignage]

## Offre
Essai de 100 nuits, pour tester sans risque.

## CTA final
Commandez votre CloudNine et réveillez-vous sans douleur.

## FAQ
**Q :** Sera-t-il trop ferme pour un dormeur sur le côté ?
**R :** Il est conçu avec [couches de soutien] pour garder l'alignement.
**Q :** Et si je ne l'aime pas ?
**R :** L'essai de 100 nuits vous permet de le renvoyer.""",
        },
    },
    "product_sheet": {
        "name": "E-commerce Product Sheet",
        "role": "You are an e-commerce copywriter who turns specs into buying reasons.",
        "rules": (
            "- Follow the section order below.\n"
            "- Turn each real spec from DETAILS into a benefit ('because X, you get Y').\n"
            "- Keep it scannable: short lines, no long paragraphs.\n"
            "- Never invent specs that are not in the brief."
        ),
        "output_format": """## Product title
<brand + product, benefit-led>

## Short description
<2-3 sentences a shopper reads first>

## Key benefits
- **<Benefit>** - <spec from DETAILS that proves it>
- **<Benefit>** - <spec from DETAILS that proves it>
- **<Benefit>** - <spec from DETAILS that proves it>

## Who it's for
<one sentence on the buyer>

## What's included
- <items from the brief only>

## CTA
<one action matching the product type>""",
        "examples": {
            EN: """## TerraGrip All-Terrain Hikers - Grip That Holds on Wet Rock
**Short description:** TerraGrip keeps you steady on trails, rain or shine. Deep lugs bite into mud and wet stone so you can hike with confidence.

## Key benefits
- **Confidence on wet ground** - [rubber outsole] with [deep lugs] grips slippery rock and mud.
- **Dry feet all day** - [waterproof membrane] keeps water out while letting sweat escape.
- **All-day comfort** - [cushioned midsole] absorbs impact on long descents.

## Who it's for
Hikers who want one dependable shoe for varied terrain.

## What's included
- One pair of TerraGrip hikers
- [spare laces]

## CTA
Add TerraGrip to your cart.""",
            FR: """## TerraGrip Chaussures Tout-Terrain - Une Adhérence qui Tient sur la Roche Mouillée
**Description courte :** TerraGrip vous garde stable sur les sentiers, pluie ou grand soleil. Des crampons profonds mordent la boue et la pierre mouillée pour randonner en confiance.

## Bénéfices clés
- **Confiance sur sol mouillé** - [semelle en caoutchouc] à [crampons profonds] adhère à la roche glissante et à la boue.
- **Pieds au sec toute la journée** - [membrane imperméable] bloque l'eau tout en laissant respirer le pied.
- **Confort toute la journée** - [semelle intermédiaire amortissante] absorbe les chocs en descente.

## Pour qui
Les randonneurs qui veulent une seule chaussure fiable sur tous les terrains.

## Contenu de la boîte
- Une paire de TerraGrip
- [lacets de rechange]

## CTA
Ajoutez TerraGrip à votre panier.""",
        },
    },
    "ad_copy": {
        "name": "Online Ad",
        "role": "You are a paid-social and paid-search copywriter.",
        "rules": (
            "- Produce exactly 3 clearly different variants (different angle, not just wording).\n"
            "- Keep primary text short and scannable; headlines are punchy.\n"
            "- Respect any platform limits mentioned in the brief."
        ),
        "output_format": """### Variant 1 - <angle>
**Primary text:** <1-3 short sentences>
**Headline:** <short punchy headline>
**Description:** <one line>
**CTA:** <button label + action>

### Variant 2 - <angle>
**Primary text:** ...
**Headline:** ...
**Description:** ...
**CTA:** ...

### Variant 3 - <angle>
**Primary text:** ...
**Headline:** ...
**Description:** ...
**CTA:** ...""",
        "examples": {
            EN: """### Variant 1 - Problem
**Primary text:** Your inbox is a wall of unread mail. InboxZero clears the clutter so you only see what matters.
**Headline:** An inbox that stays clean
**Description:** Tidy up in minutes, not hours.
**CTA:** Try it free

### Variant 2 - Curiosity
**Primary text:** What if you never had to "catch up" on email again? InboxZero keeps it empty for you.
**Headline:** Zero unread, every day
**Description:** Set it once and forget the clutter.
**CTA:** Start free

### Variant 3 - Social proof
**Primary text:** Join the [number] people who left email chaos behind with InboxZero.
**Headline:** Inbox calm, finally
**Description:** Clean up and stay clean.
**CTA:** Get started""",
            FR: """### Variante 1 - Problème
**Texte principal :** Votre boîte mail est un mur de messages non lus. InboxZero fait le tri pour que vous ne voyiez que l'essentiel.
**Titre :** Une boîte mail toujours propre
**Description :** Rangez en quelques minutes, pas en heures.
**CTA :** Essayez gratuitement

### Variante 2 - Curiosité
**Texte principal :** Et si vous n'aviez plus jamais à « rattraper » vos e-mails ? InboxZero la garde vide pour vous.
**Titre :** Zéro non lu, chaque jour
**Description :** Réglez-le une fois, oubliez le désordre.
**CTA :** Commencer gratuitement

### Variante 3 - Preuve sociale
**Texte principal :** Rejoignez les [nombre] personnes qui ont quitté le chaos des e-mails grâce à InboxZero.
**Titre :** Le calme dans la boîte mail
**Description :** Rangez, puis restez rangé.
**CTA :** Commencer""",
        },
    },
    "email_newsletter": {
        "name": "Email / Newsletter",
        "role": "You are an email copywriter who gets opens and clicks.",
        "rules": (
            "- Give 3 subject line options, then one clean email body.\n"
            "- The first line earns the second: no generic greetings that waste the preview.\n"
            "- One clear CTA, matching the product type."
        ),
        "output_format": """## Subject line options
1. <option>
2. <option>
3. <option>

## Preview text
<one line that complements the subject>

## Email body
<greeting>

<short body, 2-4 short paragraphs, customer's voice>

<CTA line>

<sign-off>""",
        "examples": {
            EN: """## Subject line options
1. Your plants called - they want a friend
2. Fern & Fir: fresh greenery at your door
3. What is quietly dying on your windowsill?

## Preview text
New plants, delivered healthy and ready to grow.

## Email body
Hi [first name],

Most houseplants die from kindness - too much water, too little light. Fern & Fir sends plants matched to your space, with a simple care card for each one.

This month: [plant name], chosen because it thrives in low light.

Ready to add some green?

Browse this month's plants

Grow well,
The Fern & Fir team""",
            FR: """## Objets possibles
1. Vos plantes vous réclament une amie
2. Fern & Fir : de la verdure fraîche devant votre porte
3. Qu'est-ce qui dépérit sur votre rebord de fenêtre ?

## Texte d'aperçu
De nouvelles plantes, livrées en pleine santé, prêtes à pousser.

## Corps de l'e-mail
Bonjour [prénom],

La plupart des plantes d'intérieur meurent par excès de soins : trop d'eau, pas assez de lumière. Fern & Fir vous envoie des plantes adaptées à votre intérieur, avec une fiche d'entretien simple pour chacune.

Ce mois-ci : [nom de la plante], choisie parce qu'elle s'épanouit à l'ombre.

Envie d'un peu de verdure ?

Découvrir les plantes du mois

Cultivez bien,
L'équipe Fern & Fir""",
        },
    },
    "social_post": {
        "name": "Social Post",
        "role": "You are a social media copywriter.",
        "rules": (
            "- Write one post: a scroll-stopping first line, a short body, and a CTA.\n"
            "- End with 3-5 relevant hashtags.\n"
            "- Keep the register natural for the network in the brief."
        ),
        "output_format": """## Post
<hook line>

<body, 2-4 short lines>

<CTA line>

<3-5 hashtags>""",
        "examples": {
            EN: """## Post
You don't need more willpower. You need dinner already in the fridge.

GreenRush preps fresh meals for the week so 6pm is solved before it starts.

Fresh. Simple. Done.

Get your first box
#MealPrep #HealthyEating #GreenRush #WeeknightDinner""",
            FR: """## Publication
Vous n'avez pas besoin de plus de volonté. Vous avez besoin d'un dîner déjà prêt au frigo.

GreenRush prépare vos repas frais de la semaine : à 19h, tout est déjà réglé.

Frais. Simple. Fait.

Recevez votre première box
#BatchCooking #MangerSain #GreenRush #DinerFacile""",
        },
    },
    "newsletter_paid": {
        "name": "Paid / Private Newsletter",
        "role": "You are a paid-newsletter writer who earns renewals.",
        "rules": (
            "- Address paying members directly and make them feel the value.\n"
            "- Structure: a hook, 2-3 short sections with a takeaway each, a closing CTA.\n"
            "- Do not invent data or stories that are not in the brief."
        ),
        "output_format": """## Title
<edition title>

## Opening
<2-3 sentences hooking the member>

## Section 1 - <heading>
<short body> 
**Takeaway:** <one line>

## Section 2 - <heading>
<short body>
**Takeaway:** <one line>

## Section 3 - <heading>
<short body>
**Takeaway:** <one line>

## Closing
<short CTA / next edition tease, from the brief only>""",
        "examples": {
            EN: """## Title
The Signal - Issue [number]: [topic]

## Opening
Every week I read the reports so you don't have to. Here is what actually matters for [industry] this week.

## Section 1 - What changed
[one change, from the brief]
**Takeaway:** [one line]

## Section 2 - What it means for you
[implication, from the brief]
**Takeaway:** [one line]

## Section 3 - What to do next
[one action, from the brief]
**Takeaway:** [one line]

## Closing
That's it for this week. Next issue: [tease from the brief]. Reply and tell me what you'd like covered.""",
            FR: """## Titre
The Signal - Édition [numéro] : [sujet]

## Introduction
Chaque semaine, je lis les rapports pour vous. Voici ce qui compte vraiment pour [secteur] cette semaine.

## Section 1 - Ce qui a changé
[un changement, issu du brief]
**À retenir :** [une ligne]

## Section 2 - Ce que cela implique pour vous
[conséquence, issue du brief]
**À retenir :** [une ligne]

## Section 3 - Que faire ensuite
[une action, issue du brief]
**À retenir :** [une ligne]

## Conclusion
C'est tout pour cette semaine. Prochaine édition : [teaser issu du brief]. Répondez pour me dire ce que vous voulez voir traité.""",
        },
    },
    "podcast_script": {
        "name": "Podcast Script",
        "role": "You are a podcast scriptwriter.",
        "rules": (
            "- Include a cold open, intro, 3 segments with talking points, and an outro.\n"
            "- Keep it spoken: short sentences the host can read aloud.\n"
            "- Use only the topic and guest details from the brief."
        ),
        "output_format": """## Episode title
<working title>

## Cold open
<2-3 spoken lines hooking the listener>

## Intro
<welcome + what this episode covers>

## Segment 1 - <heading>
- <talking point>
- <talking point>
Transition: <one spoken line>

## Segment 2 - <heading>
- <talking point>
- <talking point>
Transition: <one spoken line>

## Segment 3 - <heading>
- <talking point>
- <talking point>

## Outro
<recap + CTA matching the product type>""",
        "examples": {
            EN: """## Episode title
Deep Work #[number] - [topic] with [guest]

## Cold open
Most people think focus is a talent. [guest] says it is a system - and today we build it.

## Intro
Welcome back to Deep Work. I'm [host], and today [guest] and I break down [topic].

## Segment 1 - The myth
- Why "just try harder" fails
- What [guest] does instead
Transition: Let's get practical.

## Segment 2 - The system
- [talking point from the brief]
- [talking point from the brief]
Transition: So how do you start?

## Segment 3 - Start today
- [first step from the brief]
- [first step from the brief]

## Outro
That's it for today. Full notes and the [product] link are in the show notes - sign up at [where].""",
            FR: """## Titre de l'épisode
Deep Work #[numéro] - [sujet] avec [invité]

## Accroche
Beaucoup croient que la concentration est un talent. [invité] dit que c'est un système - et on le construit aujourd'hui.

## Introduction
Bienvenue dans Deep Work. Je suis [animateur], et aujourd'hui [invité] et moi décortiquons [sujet].

## Segment 1 - Le mythe
- Pourquoi « fais plus d'efforts » échoue
- Ce que [invité] fait à la place
Transition : Passons à la pratique.

## Segment 2 - Le système
- [point de discussion issu du brief]
- [point de discussion issu du brief]
Transition : Alors, comment commencer ?

## Segment 3 - Commencer aujourd'hui
- [première étape issue du brief]
- [première étape issue du brief]

## Conclusion
C'est tout pour aujourd'hui. Les notes et le lien [produit] sont dans les notes de l'épisode - inscrivez-vous sur [où].""",
        },
    },
    "flyer_brochure": {
        "name": "Flyer / Brochure",
        "role": "You are a print copywriter for flyers and brochures.",
        "rules": (
            "- Print must be scannable: a headline, a subheadline, a few blocks of print.\n"
            "- Put the offer and the contact details where they are easy to find.\n"
            "- Use the contact info from the brief exactly; never invent an address or number."
        ),
        "output_format": """## Headline
<big print headline>

## Subheadline
<one supporting line>

## Benefit blocks
- **<Heading>** - <one line>
- **<Heading>** - <one line>
- **<Heading>** - <one line>

## Offer
<the offer, from the brief only>

## Contact
<contact info / address / QR from the brief exactly>

## CTA
<one action matching the product type>""",
        "examples": {
            EN: """## Headline
A healthy smile, without the wait

## Subheadline
BrightSmile Dental - gentle care for the whole family.

## Benefit blocks
- **Same-week appointments** - [detail from the brief]
- **Gentle, painless care** - [detail from the brief]
- **Transparent prices** - [detail from the brief]

## Offer
[offer from the brief, e.g. first check-up]

## Contact
[address] | [phone] | [QR code]

## CTA
Book your visit""",
            FR: """## Titre
Un sourire sain, sans attendre

## Sous-titre
BrightSmile Dental - des soins tout en douceur pour toute la famille.

## Blocs bénéfices
- **Rendez-vous la semaine même** - [détail issu du brief]
- **Des soins doux et indolores** - [détail issu du brief]
- **Des prix transparents** - [détail issu du brief]

## Offre
[offre issue du brief, ex. premier contrôle]

## Contact
[adresse] | [téléphone] | [QR code]

## CTA
Réservez votre visite""",
        },
    },
    "poster": {
        "name": "Poster / Slogan",
        "role": "You are a poster and slogan copywriter.",
        "rules": (
            "- The slogan is the hero: maximum 7 words.\n"
            "- Everything else is minimal and readable from a distance.\n"
            "- Never invent a tagline fact that is not in the brief."
        ),
        "output_format": """## Slogan
<max 7 words, the hero line>

## Subline
<one short supporting line>

## Details
<only the essentials: what, where, when from the brief>

## CTA
<one short action matching the product type>""",
        "examples": {
            EN: """## Slogan
Three days. One sound.

## Subline
SoundWave Festival - [dates], [city].

## Details
[dates] | [venue] | [city]

## CTA
Get tickets""",
            FR: """## Slogan
Trois jours. Un seul son.

## Accroche
Festival SoundWave - [dates], [ville].

## Détails
[dates] | [lieu] | [ville]

## CTA
Prenez vos places""",
        },
    },
    "sales_letter": {
        "name": "Sales Letter",
        "role": "You are a classic long-form direct-response sales-letter writer.",
        "rules": (
            "- Use the classic structure: headline, opening, problem/agitate, offer, bullets, guarantee, CTA, P.S.\n"
            "- Write in the customer's voice; build the desire with the brief's facts only.\n"
            "- Any guarantee must come from the brief; otherwise use a bracketed placeholder."
        ),
        "output_format": """## Headline
<the big promise>

## Opening
<2-3 sentences that pull the reader in>

## The problem
<agitate the real frustration from the strategy's pains>

## The offer
<what you get, naming the brand>

## What you get
- <bullet from the brief>
- <bullet from the brief>
- <bullet from the brief>

## Guarantee
<from the brief, or [guarantee] placeholder>

## CTA
<one clear action matching the product type>

## P.S.
<one reinforcing line>""",
        "examples": {
            EN: """## Headline
Close your books in a day, not a week

## Opening
If month-end feels like a fire drill, you are not alone - and it is not your fault.

## The problem
You spend nights chasing receipts and reconciling by hand, while the real work waits.

## The offer
LedgerPro watches your accounts automatically and flags what needs you, so closing becomes a checklist, not a crisis.

## What you get
- **Automatic reconciliation** - [detail from the brief]
- **One-click reports** - [detail from the brief]
- **Live dashboard** - [detail from the brief]

## Guarantee
[guarantee from the brief, or 30-day money-back guarantee]

## CTA
Start your free trial

## P.S.
You did not start your business to do paperwork. Let LedgerPro handle it.""",
            FR: """## Titre
Clôturez vos comptes en un jour, pas en une semaine

## Introduction
Si la clôture mensuelle ressemble à un exercice de crise, vous n'êtes pas seul - et ce n'est pas votre faute.

## Le problème
Vous passez vos soirées à courir après les justificatifs et à rapprocher les comptes à la main, pendant que le vrai travail attend.

## L'offre
LedgerPro surveille vos comptes automatiquement et signale ce qui vous concerne : la clôture devient une checklist, pas une urgence.

## Ce que vous obtenez
- **Rapprochement automatique** - [détail issu du brief]
- **Rapports en un clic** - [détail issu du brief]
- **Tableau de bord en direct** - [détail issu du brief]

## Garantie
[garantie issue du brief, ou satisfait ou remboursé 30 jours]

## CTA
Démarrez votre essai gratuit

## P.-S.
Vous n'avez pas créé votre entreprise pour faire de la paperasse. Laissez LedgerPro s'en occuper.""",
        },
    },
}

_GENERIC_USER_TEMPLATE = """STRATEGY (JSON):
{strategy}

BRIEF:
{brief_fields}

Write the {format_name} now, in the SAME language as the brief."""


def writer_spec(format_key):
    """Return the spec dict for a non-video format, or None for video_ad."""
    if not _not_video(format_key):
        return None
    return _FORMAT_SPECS.get(format_key)


def _brief_fields_text(clean):
    lines = [
        ("BRAND", clean["brand"]),
        ("PRODUCT", clean["product"]),
        ("DETAILS", clean["details"]),
        ("AUDIENCE", clean["audience"]),
        ("GOAL", clean["goal"]),
    ]
    if clean.get("platform"):
        lines.append(("PLATFORM", clean["platform"]))
    if clean.get("product_type"):
        lines.append(("PRODUCT TYPE", clean["product_type"]))
    if clean.get("tone"):
        lines.append(("TONE", clean["tone"]))
    text = "\n".join("{0}: {1}".format(k, v) for k, v in lines if v)
    extras = _extras_text(clean)
    if extras:
        text += "\n" + extras
    return text


# --------------------------------------------------------------------------- #
# Public builders
# --------------------------------------------------------------------------- #

def build_strategist_messages(brief, format_key="video_ad"):
    """Agent 1 messages. Non-video formats reuse the shared strategist with a
    short format hint appended so angles suit the deliverable."""
    if not _not_video(format_key):
        return prompts.build_strategist_messages(brief)

    spec = _FORMAT_SPECS.get(format_key)
    clean = normalize_brief(brief)
    messages = list(prompts.build_strategist_messages(brief))
    if spec:
        hint = "\n\nFORMAT FOCUS: the deliverable is a {0}. Aim the hook_angles and positioning at what this format must achieve.".format(
            spec["name"]
        )
        messages[0] = {
            "role": "system",
            "content": messages[0]["content"] + hint,
        }
    extras = _extras_text(clean)
    if extras:
        messages[-1] = {
            "role": "user",
            "content": messages[-1]["content"]
            + "\n\nADDITIONAL DETAILS:\n"
            + extras,
        }
    return messages


def build_writer_messages(brief, strategy, format_key="video_ad"):
    """Agent 2 messages. video_ad delegates to :mod:`prompts` unchanged."""
    if not _not_video(format_key):
        return prompts.build_scriptwriter_messages(brief, strategy)

    import json

    spec = _FORMAT_SPECS.get(format_key)
    if spec is None:
        raise ValueError("Unknown format: {0}".format(format_key))

    clean = normalize_brief(brief)
    lang = prompts._strategy_language_code(strategy) or detect_language(
        prompts._brief_text(clean)
    )

    system = "\n\n".join(
        [
            spec["role"],
            SHARED_WRITER_RULES,
            "Format-specific rules:\n" + spec["rules"],
            "Output format (markdown):\n\n" + spec["output_format"],
        ]
    )

    messages = [{"role": "system", "content": system}]

    examples = spec.get("examples") or {}
    example = examples.get(lang)
    if example:
        messages.append({"role": "assistant", "content": example})

    user_message = _GENERIC_USER_TEMPLATE.format(
        strategy=json.dumps(strategy, ensure_ascii=False, indent=2),
        brief_fields=_brief_fields_text(clean),
        format_name=spec["name"],
    )
    messages.append({"role": "user", "content": user_message})
    return messages


__all__ = [
    "build_strategist_messages",
    "build_writer_messages",
    "writer_spec",
    "SHARED_WRITER_RULES",
]
