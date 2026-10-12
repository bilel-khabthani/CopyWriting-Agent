"""Build a clean one-page pricing PDF (marketing/pricing-menu.pdf)."""

import os
import sys
from types import SimpleNamespace

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from fpdf import FPDF
from fpdf.enums import XPos, YPos

from exporter import _find_font

OUT = os.path.join(HERE, "pricing-menu.pdf")


def main():
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(True, margin=15)
    pdf.set_margins(15, 15, 15)
    pdf.add_page()

    font = _find_font(bold=False)
    bold = _find_font(bold=True)
    family, bstyle = "Helvetica", "B"
    if font:
        pdf.add_font("Body", "", font)
        family = "Body"
        if bold:
            pdf.add_font("Body", "B", bold)
        else:
            bstyle = ""

    pdf.set_font(family, bstyle, 22)
    pdf.multi_cell(0, 10, "AdScript Studio", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font(family, "", 11)
    pdf.set_text_color(110, 110, 110)
    pdf.multi_cell(
        0,
        6,
        "Scripts de publicités vidéo courtes (Reels, TikTok, YouTube Shorts).",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )
    pdf.set_text_color(0, 0, 0)
    pdf.ln(4)

    pdf.set_font(family, "", 11)
    pdf.multi_cell(
        0,
        6,
        "Chaque script inclut : un brief stratégique, le script complet "
        "(accroche, problème, solution, appel à l'action) et un shot list "
        "découpé seconde par seconde.",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )
    pdf.ln(4)

    pdf.set_font(family, bstyle, 14)
    pdf.multi_cell(0, 8, "Offres", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font(family, "", 10)
    rows = [
        ["Offre", "Local (TND)", "International (€)", "Délai"],
        ["Échantillon", "Gratuit", "Free", "24 h"],
        ["1 script (~30 s)", "~40", "~50 €", "24 h"],
        ["Pack de 3 scripts", "~100", "~130 €", "48 h"],
        ["Retainer (4 / mois)", "~120 / mois", "~180 € / mois", "En continu"],
    ]
    epw = pdf.epw
    widths = (epw * 0.40, epw * 0.20, epw * 0.25, epw * 0.15)
    with pdf.table(col_widths=widths, line_height=7) as table:
        for row_data in rows:
            row = table.row()
            for cell in row_data:
                row.cell(cell)
    pdf.ln(4)

    pdf.set_font(family, bstyle, 13)
    pdf.multi_cell(0, 7, "Ce qui est inclus", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font(family, "", 11)
    for item in (
        "Scripts en français ou en anglais",
        "Adaptation à la plateforme (Reels, TikTok, Shorts, YouTube)",
        "Un brief stratégique pour comprendre l'angle choisi",
        "Un shot list prêt à tourner (voix-off + textes à l'écran)",
    ):
        pdf.multi_cell(0, 6, "- " + item, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(3)
    pdf.set_font(family, bstyle, 13)
    pdf.multi_cell(0, 7, "Conditions", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font(family, "", 11)
    for item in (
        "1 révision gratuite par script ; ensuite révisions facturées",
        "Livraison en 24 à 48 h",
        "Paiement à la livraison (ou 50 % à la commande pour les packs)",
        "Livraison par PDF et texte (WhatsApp / e-mail / Telegram)",
    ):
        pdf.multi_cell(0, 6, "- " + item, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(4)
    pdf.set_font(family, bstyle, 13)
    pdf.multi_cell(0, 7, "Contact", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font(family, "", 11)
    for item in ("Nom : Bilel", "Téléphone / WhatsApp : [à compléter]", "E-mail : [à compléter]"):
        pdf.multi_cell(0, 6, item, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.output(OUT)
    print("built", OUT)


if __name__ == "__main__":
    main()
