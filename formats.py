"""Format registry for multi-format copywriting.

Central place defining every supported copywriting format and its category.
Kept intentionally dependency-free so bot, pipeline and exporter can all
import it without cycles.

The original video-ad flow is preserved as ``FORMAT_VIDEO_AD``.
"""

FORMAT_VIDEO_AD = "video_ad"
FORMAT_PODCAST_SCRIPT = "podcast_script"
FORMAT_LANDING_PAGE = "landing_page"
FORMAT_PRODUCT_SHEET = "product_sheet"
FORMAT_AD_COPY = "ad_copy"
FORMAT_EMAIL_NEWSLETTER = "email_newsletter"
FORMAT_SOCIAL_POST = "social_post"
FORMAT_NEWSLETTER_PAID = "newsletter_paid"
FORMAT_FLYER_BROCHURE = "flyer_brochure"
FORMAT_POSTER = "poster"
FORMAT_SALES_LETTER = "sales_letter"

# Ordered category list (used to build the Telegram menus).
CATEGORIES = [
    ("webmarketing", "Webmarketing"),
    ("loyalty", "Loyalty & Engagement"),
    ("audio", "Audio & Visual"),
    ("traditional", "Traditional Media"),
]

# (key, display name, category)
FORMATS = [
    # Audio / Visual
    (FORMAT_VIDEO_AD, "Video Ad (30s)", "audio"),
    (FORMAT_PODCAST_SCRIPT, "Podcast Script", "audio"),
    # Webmarketing
    (FORMAT_LANDING_PAGE, "Landing Page", "webmarketing"),
    (FORMAT_PRODUCT_SHEET, "E-commerce Product Sheet", "webmarketing"),
    (FORMAT_AD_COPY, "Online Ad (FB/Google/LinkedIn/IG)", "webmarketing"),
    # Loyalty & Engagement
    (FORMAT_EMAIL_NEWSLETTER, "Email / Newsletter", "loyalty"),
    (FORMAT_SOCIAL_POST, "Social Post (LinkedIn/IG)", "loyalty"),
    (FORMAT_NEWSLETTER_PAID, "Paid / Private Newsletter", "loyalty"),
    # Traditional Media
    (FORMAT_FLYER_BROCHURE, "Flyer / Brochure", "traditional"),
    (FORMAT_POSTER, "Poster / Slogan", "traditional"),
    (FORMAT_SALES_LETTER, "Sales Letter", "traditional"),
]

_BY_KEY = {key: (key, name, category) for key, name, category in FORMATS}


def get_format(key):
    """Return {key, name, category} for a format key, or None."""
    item = _BY_KEY.get(key)
    if not item:
        return None
    return {"key": item[0], "name": item[1], "category": item[2]}


def formats_in_category(category):
    """Return [(key, name), ...] for one category, in display order."""
    return [(key, name) for key, name, cat in FORMATS if cat == category]


def category_name(category):
    for key, name in CATEGORIES:
        if key == category:
            return name
    return category


# --------------------------------------------------------------------------- #
# Per-format brief schemas
# --------------------------------------------------------------------------- #
# Fields every format always collects (reused from the existing video-ad form).
BASE_FIELDS = ("brand", "product", "details", "audience", "goal", "tone")

# Extra questions asked only for specific formats.
# Each entry: field name -> question text shown in Telegram.
FORMAT_EXTRA_FIELDS = {
    FORMAT_AD_COPY: {
        "channels": "Which channels? (e.g. Facebook + Instagram, or Google Search)",
    },
    FORMAT_EMAIL_NEWSLETTER: {
        "subject_goal": "What should the email do? (newsletter, promote an offer, re-engage...)",
    },
    FORMAT_SOCIAL_POST: {
        "network": "Which network? (LinkedIn, Instagram, or both)",
    },
    FORMAT_NEWSLETTER_PAID: {
        "audience_relation": "Who reads it? (paying members, subscribers, customers)",
    },
    FORMAT_LANDING_PAGE: {
        "offer": "What is the main offer or promise? (e.g. free trial, 20% off, book a demo)",
    },
    FORMAT_PRODUCT_SHEET: {
        "specs": "Paste the key specs or technical points to convert into benefits.",
    },
    FORMAT_PODCAST_SCRIPT: {
        "topic": "What is the episode about, and who is the guest/host?",
    },
    FORMAT_FLYER_BROCHURE: {
        "contact": "Contact info / address / QR to include.",
    },
    FORMAT_POSTER: {
        "context": "Where will it be displayed? (street, bus, shop window)",
    },
    FORMAT_SALES_LETTER: {
        "offer": "What is the offer, and what action should the reader take?",
    },
}


def extra_fields_for(key):
    """Ordered list of (field, question) for a format (possibly empty)."""
    return list(FORMAT_EXTRA_FIELDS.get(key, {}).items())
