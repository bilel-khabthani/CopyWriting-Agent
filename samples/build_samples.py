"""Build the portfolio sample PDFs (hand-polished, deterministic).

Run:  python samples/build_samples.py
Outputs <slug>.pdf and <slug>.md into this folder.

Covers the video-ad flow (labelled beats + shot list) plus the newer
multi-format deliverables (landing page, online ad, email, sales letter).
"""

import os
import sys
from types import SimpleNamespace

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import exporter  # noqa: E402
import formats  # noqa: E402

SAMPLES = [
    {
        "slug": "le-jardin",
        "brief": {
            "brand": "Le Jardin",
            "product": "Restaurant de quartier, cuisine méditerranéenne fraîche et faite maison.",
            "audience": "Familles et jeunes couples de 25 à 45 ans.",
            "goal": "get leads",
            "platform": "Instagram Reels",
            "product_type": "service",
            "tone": "warm and friendly",
        },
        "strategy": {
            "audience": "Familles et jeunes couples de 25 à 45 ans du quartier qui aiment bien manger et sortir le week-end.",
            "emotion_target": "sympathie",
            "positioning": "Le Jardin sert une cuisine méditerranéenne fraîche et faite maison, dans une ambiance chaleureuse et conviviale.",
            "pains": ["Pas le temps de cuisiner", "Toujours les mêmes adresses sans saveur", "Chercher un bon restaurant"],
            "desires": ["Un dîner agréable entre amis", "De nouvelles saveurs", "Se sentir bien reçu"],
            "hook_angles": ["Fait maison : le goût vrai", "Chaleureux : comme à la maison", "Fraîcheur : produits du jour"],
        },
        "script": """## Le Jardin — Le goût du fait maison

**HOOK:** Vous n'avez ni le temps ni l'envie de cuisiner ce soir.
**PROBLEM:** Et vous en avez assez des adresses sans saveur qui déçoivent vos soirées.
**SOLUTION:** Au Jardin, on vous sert une cuisine méditerranéenne fraîche et faite maison, dans une ambiance chaleureuse où l'on se sent bien.
**CTA:** Réservez votre table au Jardin et régalez-vous dès ce soir.

### Shot list
| # | Time | Visual | Audio / Voice-over | Text on screen |
|---|------|--------|--------------------|----------------|
| 1 | 0-3s | Une personne fatiguée ouvre un frigo presque vide en soupirant | "Vous n'avez ni le temps ni l'envie de cuisiner ce soir." | Ce soir, on mange quoi ? |
| 2 | 3-10s | La même personne, déçue, repousse une assiette fade | "Et vous en avez assez des adresses sans saveur." | Assez des restos décevants |
| 3 | 10-25s | Plats méditerranéens généreux, convives qui partagent et sourient | "Au Jardin, une cuisine méditerranéenne fraîche et faite maison vous attend." | Frais, fait maison, chaleureux |
| 4 | 25-30s | Table dressée, service souriant, logo Le Jardin | "Réservez votre table au Jardin et régalez-vous dès ce soir." | Réservez votre table |
""",
    },
    {
        "slug": "pulsefit",
        "brief": {
            "brand": "PulseFit",
            "product": "Salle de sport : coachs, cours collectifs dynamiques, abonnements sans engagement.",
            "audience": "Jeunes actifs de 20 à 35 ans qui veulent se remettre au sport.",
            "goal": "get leads",
            "platform": "TikTok",
            "product_type": "service",
            "tone": "bold and energetic",
        },
        "strategy": {
            "audience": "Jeunes actifs de 20 à 35 ans qui veulent retrouver la forme rapidement.",
            "emotion_target": "enthousiasme",
            "positioning": "PulseFit propose des cours collectifs dynamiques encadrés par des coachs, avec des abonnements sans engagement.",
            "pains": ["Abandonner quand on s'entraîne seul", "Pas de coach ni d'horaire fixe", "Manque de motivation"],
            "desires": ["Se sentir en forme", "Être motivé et encadré", "Des résultats rapides"],
            "hook_angles": ["Dynamique : cours collectifs", "Confiance : coachs experts", "Facile : sans engagement"],
        },
        "script": """## PulseFit — Reprenez le sport, sans engagement

**HOOK:** Seul, vous abandonnez votre entraînement au bout de deux semaines.
**PROBLEM:** Et sans coach ni horaire fixe, difficile de rester motivé et de tenir la cadence.
**SOLUTION:** Avec PulseFit, vous rejoignez des cours collectifs dynamiques encadrés par nos coachs, avec des abonnements sans engagement.
**CTA:** Réservez votre séance d'essai gratuite chez PulseFit.

### Shot list
| # | Time | Visual | Audio / Voice-over | Text on screen |
|---|------|--------|--------------------|----------------|
| 1 | 0-3s | Un jeune actif seul dans son salon abandonne un exercice, l'air déçu | "Seul, vous abandonnez au bout de deux semaines." | Motivé... 2 semaines |
| 2 | 3-10s | Il regarde son téléphone, découragé, dans un salon vide | "Difficile de rester motivé sans coach ni horaire fixe." | Pas de motivation |
| 3 | 10-25s | Groupe en pleine séance, coachs énergiques, sourires, musique rythmée | "Avec PulseFit, des cours collectifs dynamiques encadrés par nos coachs." | Cours collectifs + coachs |
| 4 | 25-30s | Le jeune actif, souriant et en forme, logo PulseFit | "Réservez votre séance d'essai gratuite chez PulseFit." | Essai gratuit — Réservez |
""",
    },
    {
        "slug": "botaniqa",
        "brief": {
            "brand": "Botaniqa",
            "product": "Crème hydratante bio à l'huile d'argan et à l'acide hyaluronique, nourrit 24 h, sans parfum de synthèse.",
            "audience": "Femmes de 25 à 45 ans soucieuses de leur peau et de la composition des produits.",
            "goal": "sell the product",
            "platform": "Instagram Reels",
            "product_type": "physical product",
            "tone": "warm and friendly",
        },
        "strategy": {
            "audience": "Femmes de 25 à 45 ans qui veulent nourrir leur peau avec des produits naturels.",
            "emotion_target": "satisfaction",
            "positioning": "Botaniqa est une crème hydratante bio à l'huile d'argan et à l'acide hyaluronique, nourrissante 24 h et sans parfum de synthèse.",
            "pains": ["Peau desséchée après le nettoyage", "Crèmes trop parfumées", "Besoin d'un soin quotidien efficace"],
            "desires": ["Un soin doux et naturel", "Une hydratation durable", "Confiance dans la composition"],
            "hook_angles": ["Doux : votre peau respire", "Rapide : hydratation immédiate", "Naturel : composition transparente"],
        },
        "script": """## Botaniqa — La peau hydratée 24 h, naturellement

**HOOK:** Après le nettoyage, votre peau tiraille et vous cherchez un soin vraiment doux.
**PROBLEM:** Beaucoup de crèmes sentent trop fort et laissent un film gras au lieu d'hydrater.
**SOLUTION:** Botaniqa, la crème bio à l'huile d'argan et à l'acide hyaluronique, nourrit votre peau pendant 24 heures, sans parfum de synthèse.
**CTA:** Offrez à votre peau Botaniqa dès aujourd'hui.

### Shot list
| # | Time | Visual | Audio / Voice-over | Text on screen |
|---|------|--------|--------------------|----------------|
| 1 | 0-3s | Une femme se regarde dans le miroir, la peau tendue après le nettoyage | "Après le nettoyage, votre peau tiraille." | La peau qui tiraille ? |
| 2 | 3-10s | Elle teste une crème trop parfumée et fait la grimace | "Beaucoup de crèmes sentent trop fort et laissent un film gras." | Trop parfumée, trop lourde |
| 3 | 10-25s | Une goutte de Botaniqa appliquée, la peau paraît douce et lumineuse | "Botaniqa nourrit votre peau 24 heures, sans parfum de synthèse." | Argan + acide hyaluronique |
| 4 | 25-30s | La femme sereine, peau lumineuse, produit Botaniqa en main | "Offrez à votre peau Botaniqa dès aujourd'hui." | Commander maintenant |
""",
    },
    {
        "slug": "quickfix-mobile",
        "brief": {
            "brand": "QuickFix Mobile",
            "product": "Phone repair shop: cracked screens and water damage fixed in under 30 minutes.",
            "audience": "Busy professionals and students aged 18-40 whose phone is broken.",
            "goal": "get leads",
            "platform": "TikTok",
            "product_type": "service",
            "tone": "bold and energetic",
        },
        "strategy": {
            "audience": "Busy professionals and students aged 18-40 who cannot afford to be without their phone.",
            "emotion_target": "relief",
            "positioning": "QuickFix Mobile repairs cracked screens and water damage in under 30 minutes, backed by a 6-month warranty.",
            "pains": ["A broken phone is unusable", "Repair shops take too long", "Worries about the warranty"],
            "desires": ["Get the phone back fast", "Peace of mind with a warranty", "Save time and money"],
            "hook_angles": ["Speed: fixed in 30 minutes", "Warranty: 6 months of peace of mind", "Efficiency: no long waits"],
        },
        "script": """## QuickFix Mobile — Your phone, fixed in 30 minutes

**HOOK:** A cracked screen shouldn't cost you a day without your phone.
**PROBLEM:** Slow repair shops keep you waiting, while every minute offline costs you time and money.
**SOLUTION:** QuickFix Mobile repairs cracked screens and water damage in under 30 minutes, backed by a 6-month warranty.
**CTA:** Book your repair today and get your phone back in 30 minutes.

### Shot list
| # | Time | Visual | Audio / Voice-over | Text on screen |
|---|------|--------|--------------------|----------------|
| 1 | 0-3s | A professional stares at a badly cracked phone, frustrated | "A cracked screen shouldn't cost you a day." | Your phone is broken |
| 2 | 3-10s | Close-up of the shattered screen; they miss an important call | "Slow repairs keep you waiting — every minute costs you." | Every minute offline costs you |
| 3 | 10-25s | A QuickFix technician expertly swaps the screen, a timer running | "QuickFix Mobile repairs it in under 30 minutes." | 30-minute repair |
| 4 | 25-30s | A relieved customer happily uses the fixed phone; warranty badge | "Backed by a 6-month warranty." | Book now — 6-month warranty |
""",
    },
    {
        "slug": "fitloop",
        "brief": {
            "brand": "FitLoop",
            "product": "Fitness app: personalized home workout plan with streaks and reminders.",
            "audience": "Beginners aged 20-40 who want to get fit at home.",
            "goal": "sell the product",
            "platform": "YouTube Shorts",
            "product_type": "app or software",
            "tone": "playful and fun",
        },
        "strategy": {
            "audience": "Beginners aged 20-40 who want to get fit at home but struggle with motivation.",
            "emotion_target": "motivation",
            "positioning": "FitLoop builds a personalized home workout plan and keeps you motivated with streaks and friendly reminders.",
            "pains": ["Losing motivation easily", "Not knowing where to start", "Skipping workouts"],
            "desires": ["A personalized plan", "Staying consistent", "Feeling accomplished"],
            "hook_angles": ["Fun: start the day right", "Motivation: friendly reminders", "Effortless: a plan built for you"],
        },
        "script": """## FitLoop — Your personal workout, every single day

**HOOK:** You want to get fit at home, but you never know where to start.
**PROBLEM:** Without a plan, motivation fades fast and workouts get skipped.
**SOLUTION:** FitLoop builds a personalized home plan and keeps you going with streaks and friendly reminders.
**CTA:** Download FitLoop and start your first workout today.

### Shot list
| # | Time | Visual | Audio / Voice-over | Text on screen |
|---|------|--------|--------------------|----------------|
| 1 | 0-3s | A beginner sits on the couch in workout clothes, unsure | "You want to get fit, but you don't know where to start." | Where do I start? |
| 2 | 3-10s | Days pass; the workout clothes stay untouched | "Without a plan, motivation fades fast." | Motivation fading |
| 3 | 10-25s | FitLoop opens, showing a personalized plan and a growing streak | "FitLoop builds your plan and keeps you going with streaks." | Your plan + daily streaks |
| 4 | 25-30s | The beginner finishes a workout, smiling, streak hits day 7 | "Download FitLoop and start your first workout today." | Download today |
""",
    },
    {
        "slug": "atelier-lumen",
        "format": "landing_page",
        "brief": {
            "brand": "Atelier Lumen",
            "product": "Atelier de poterie en ligne : la terre est livrée et les cours se donnent en visio.",
            "details": "mini-tour inclus, sessions live de 45 min, replays",
            "audience": "Débutants de 25 à 50 ans qui veulent créer de leurs mains.",
            "goal": "sell the product",
            "tone": "warm and friendly",
            "offer": "Box de départ : terre, outils et mini-tour",
        },
        "strategy": {
            "audience": "Adultes débutants qui veulent créer de leurs mains sans suivre un cours en présentiel.",
            "emotion_target": "fierté",
            "positioning": "Atelier Lumen est un atelier de poterie en ligne : vous recevez la terre et tournez avec un prof en visio.",
            "pains": ["Pas le temps d'aller en cours", "Peur de ne pas y arriver seul", "Les places partent vite"],
            "desires": ["Créer quelque chose soi-même", "Être guidé pas à pas", "Apprendre à son rythme"],
            "hook_angles": ["Un vrai tour chez soi", "Un prof en direct", "Zéro pression"],
        },
        "script": """## Headline
Apprenez la poterie avec un vrai tour, depuis votre salon.

## Subheadline
Atelier Lumen vous envoie la terre et vous guide en direct, étape par étape.

## Hero CTA
Réserver ma première séance - 19 €

## Problem
Vous rêvez de créer de vos mains, mais un cours en présentiel demande du temps et les places partent vite.

## Solution
Atelier Lumen est un atelier de poterie en ligne : vous recevez la terre, et vous tournez avec un prof en visio.
- **Un vrai tour** - un mini-tour est inclus dans la box de départ.
- **Un prof en direct** - des sessions live de 45 minutes chaque semaine.
- **Zéro pression** - revoyez chaque étape en replay quand vous voulez.

## Social proof
[élève] - "En trois séances, j'ai façonné mon premier bol."

## Offer
La box de départ comprend [la terre], [les outils] et [le mini-tour].

## Final CTA
Réservez votre première séance.

## FAQ
**Q :** Faut-il un four chez soi ?
**R :** Non, on vous indique où faire cuire vos pièces près de chez vous.
**Q :** Et si je débute vraiment ?
**R :** Chaque séance commence par les gestes de base, pas à pas.
""",
    },
    {
        "slug": "snapchef-adcopy",
        "format": "ad_copy",
        "brief": {
            "brand": "SnapChef",
            "product": "Meal kit: fresh ingredients and 20-minute recipes delivered weekly.",
            "details": "fresh pre-portioned ingredients, 20-minute recipes, skip anytime",
            "audience": "Busy couples and young professionals aged 24-40.",
            "goal": "get leads",
            "tone": "playful and fun",
            "channels": "Facebook + Instagram",
        },
        "strategy": {
            "audience": "Busy couples who dread deciding what to cook after work.",
            "emotion_target": "relief",
            "positioning": "SnapChef delivers fresh ingredients and 20-minute recipes so dinner is decided for you.",
            "pains": ["No plan at 6pm", "Wasted groceries", "Takeaway costs too much"],
            "desires": ["Easy weeknight dinners", "Less food waste", "Save money"],
            "hook_angles": ["Speed: 20-minute dinners", "Ease: no planning", "Value: cheaper than takeaway"],
        },
        "script": """### Variant 1 - Problem
**Primary text:** 6 p.m. again. Everyone's hungry and you have no plan. SnapChef sends fresh ingredients and a 20-minute recipe.
**Headline:** Dinner solved, not scrambled
**Description:** Fresh meals, zero guesswork.
**CTA:** Get my first box

### Variant 2 - Curiosity
**Primary text:** What if dinner took 20 minutes and you never had to plan it? That's a SnapChef week.
**Headline:** 20-minute dinners, done
**Description:** Cook tonight, relax after.
**CTA:** Try it free

### Variant 3 - Social proof
**Primary text:** Join [number] home cooks who stopped dreading 6 p.m. with SnapChef.
**Headline:** The end of "what's for dinner"
**Description:** Fresh, simple, weekly.
**CTA:** Start now
""",
    },
    {
        "slug": "maison-olive-email",
        "format": "email_newsletter",
        "brief": {
            "brand": "Maison Olive",
            "product": "Épicerie fine : coffrets d'huiles d'olive sélectionnées avec fiches de dégustation.",
            "details": "trois huiles par coffret, fiches de dégustation, livraison mensuelle",
            "audience": "Amateurs de cuisine de 30 à 60 ans.",
            "goal": "sell the product",
            "tone": "warm and friendly",
            "subject_goal": "annoncer la sélection du mois",
        },
        "strategy": {
            "audience": "Amateurs de bonne cuisine qui veulent des produits de qualité sans se tromper.",
            "emotion_target": "gourmandise",
            "positioning": "Maison Olive sélectionne des huiles d'olive fines et les livre avec une fiche de dégustation.",
            "pains": ["Ne pas savoir quelle huile choisir", "Produits décevants en supermarché", "Manque d'inspiration en cuisine"],
            "desires": ["Des produits qui ont du goût", "Des idées simples", "Se faire plaisir"],
            "hook_angles": ["Sélection : le bon goût", "Conseils : fiches de dégustation", "Fraîcheur : livraison mensuelle"],
        },
        "script": """## Objets possibles
1. Vos trois huiles d'olive préférées sont de retour
2. Maison Olive : le goût du Sud dans votre cuisine
3. Vous cuisinez à l'huile, mais laquelle ?

## Texte d'aperçu
Trois huiles d'olive sélectionnées, livrées avec leur fiche de dégustation.

## Corps de l'e-mail
Bonjour [prénom],

Toutes les huiles d'olive ne se valent pas : certaines sont faites pour la cuisson, d'autres pour finir un plat à cru. Maison Olive sélectionne trois huiles, chacune avec sa fiche de dégustation.

Ce mois-ci : [nom de l'huile], idéale pour vos salades.

Envie de goûter la différence ?

Découvrir les huiles du mois

À bientôt,
L'équipe Maison Olive
""",
    },
    {
        "slug": "taxflow-letter",
        "format": "sales_letter",
        "brief": {
            "brand": "TaxFlow",
            "product": "Accounting software that prepares VAT returns automatically.",
            "details": "automatic expense capture, VAT-ready reports, deadline reminders",
            "audience": "Small business owners and freelancers in the UK.",
            "goal": "sell the product",
            "tone": "professional",
            "offer": "Free 30-day trial",
        },
        "strategy": {
            "audience": "Small business owners who handle their own tax and dread the paperwork.",
            "emotion_target": "relief",
            "positioning": "TaxFlow keeps expenses in order and prepares your VAT return automatically.",
            "pains": ["Chasing receipts at deadline", "Fearing a costly mistake", "Losing evenings to spreadsheets"],
            "desires": ["File with confidence", "Get time back", "Never miss a deadline"],
            "hook_angles": ["Speed: returns in minutes", "Certainty: nothing missed", "Time: evenings back"],
        },
        "script": """## Headline
Get your VAT return done before your coffee gets cold

## Opening
If tax season turns into panic season, you are not alone - and it is not your fault.

## The problem
You scramble through receipts and spreadsheets while deadlines loom, hoping nothing is missed.

## The offer
TaxFlow keeps every expense in order and prepares your VAT return automatically, so filing becomes a review, not a rescue.

## What you get
- **Automatic expense capture** - [detail from the brief]
- **VAT-ready reports** - [detail from the brief]
- **Deadline reminders** - [detail from the brief]

## Guarantee
[guarantee from the brief, or 30-day money-back guarantee]

## CTA
Start your free trial

## P.S.
You became a business owner to build something - not to fight spreadsheets at midnight.
""",
    },
]


def main():
    for sample in SAMPLES:
        result = SimpleNamespace(
            script=sample["script"],
            strategy=sample["strategy"],
            brief=sample["brief"],
            format=sample.get("format", "video_ad"),
        )
        pdf_path = os.path.join(HERE, sample["slug"] + ".pdf")
        exporter.build_pdf(result, pdf_path, client_view=True)

        brief = sample["brief"]
        meta = formats.get_format(result.format)
        meta_bits = [b for b in (brief.get("platform", ""), brief.get("goal", ""), brief.get("tone", "")) if b]
        md = "# {0} - {1}\n\n_{2}_\n\n{3}".format(
            brief["brand"],
            meta["name"] if meta else "Deliverable",
            " | ".join(meta_bits),
            sample["script"],
        )
        with open(os.path.join(HERE, sample["slug"] + ".md"), "w", encoding="utf-8") as handle:
            handle.write(md)
        print("built", sample["slug"], "({0})".format(result.format))


if __name__ == "__main__":
    main()
