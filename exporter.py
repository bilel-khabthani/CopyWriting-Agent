"""PDF export for a pipeline Result.

Turns the scriptwriter's markdown into a branded, client-ready PDF:
- Parses the predictable structure (``## title``, ``**HOOK:** ...``,
  ``### Shot list`` + markdown table).
- Renders a real table for the shot list.
- Uses a Unicode TTF (Windows Arial) so French accents render; falls back to
  the built-in Helvetica (latin-1) when unavailable.

Public API:
    build_pdf(result, path, client_view=True)  -> writes a PDF file
    build_pdf_file(result, client_view=True)   -> returns (path, filename)
"""

import os
import re
import tempfile

try:
    from fpdf import FPDF
    from fpdf.enums import XPos, YPos
except Exception:  # pragma: no cover - import guard
    FPDF = None
    XPos = YPos = None

from formats import get_format

MARGIN = 15
SECTION_LABELS = ("HOOK", "PROBLEM", "SOLUTION", "CTA")


def _find_font(bold: bool = False):
    windir = os.environ.get("WINDIR", r"C:\Windows")
    font_dir = os.path.join(windir, "Fonts")
    names = ("arialbd.ttf", "segoeuib.ttf") if bold else ("arial.ttf", "segoeui.ttf")
    for name in names:
        path = os.path.join(font_dir, name)
        if os.path.exists(path):
            return path
    return None


def parse_script(script: str) -> dict:
    """Split the script markdown into {title, sections, shot_header, shot_rows}."""
    title = ""
    sections = []
    table_lines = []
    in_shot_list = False

    for raw in (script or "").splitlines():
        line = raw.strip()
        if not line:
            continue

        heading = re.match(r"^#{1,6}\s+(.*)$", line)
        if heading:
            text = heading.group(1).strip()
            if "shot" in text.lower():
                in_shot_list = True
            elif not title:
                title = text
            continue

        if line.startswith("|"):
            table_lines.append(line)
            continue

        section = re.match(r"^\*\*(.+?)\*\*\s*(.*)$", line)
        if section:
            label = section.group(1).strip().strip(":").strip()
            value = section.group(2).strip()
            sections.append((label, value))
            continue

        if in_shot_list:
            continue

        if sections:
            label, value = sections[-1]
            sections[-1] = (label, (value + " " + line).strip())
        else:
            sections.append(("", line))

    shot_header, shot_rows = _parse_table(table_lines)
    return {
        "title": title,
        "sections": sections,
        "shot_header": shot_header,
        "shot_rows": shot_rows,
    }


def _parse_table(table_lines):
    """Parse markdown pipe-table lines into (header, rows)."""
    if not table_lines:
        return [], []

    def cells(line):
        line = line.strip()
        if line.startswith("|"):
            line = line[1:]
        if line.endswith("|"):
            line = line[:-1]
        return [c.strip() for c in line.split("|")]

    parsed = [cells(line) for line in table_lines]
    header = parsed[0]
    body = parsed[1:]

    if body and all(re.fullmatch(r"[\s:-]*", c or "") for c in body[0]):
        body = body[1:]

    width = max([len(header)] + [len(r) for r in body]) if body else len(header)
    header = header + [""] * (width - len(header))
    body = [r + [""] * (width - len(r)) for r in body]
    return header, body


def _safe(text) -> str:
    return str(text if text is not None else "")


def _plain(text: str) -> str:
    """Strip inline markdown markers (used for headings)."""
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    return text.strip()


def _write_md_line(pdf, text, family, bold, size=11, line_h=6, indent=0):
    """Write one line, honouring inline **bold**, wrapping at the right margin."""
    if indent:
        pdf.set_x(pdf.l_margin + indent)
    parts = re.split(r"\*\*(.+?)\*\*", text)
    pdf.set_font(family, "", size)
    for index, part in enumerate(parts):
        if not part:
            continue
        pdf.set_font(family, bold if index % 2 == 1 else "", size)
        pdf.write(line_h, part)
    pdf.ln(line_h)


def _render_table(pdf, block, family, bold):
    header, rows = _parse_table(block)
    if not header:
        return
    weights = _column_weights(header, ("voice", "audio", "visual", "text", "screen"))
    epw = pdf.epw
    col_widths = tuple(round(epw * w, 2) for w in weights)
    pdf.set_font(family, "", 9)
    with pdf.table(col_widths=col_widths, line_height=5) as table:
        head = table.row()
        for cell in header:
            head.cell(cell)
        for row in rows:
            r = table.row()
            for cell in row:
                r.cell(cell)


def _render_markdown(pdf, script, family, bold):
    """Generic renderer for any markdown deliverable (headings, bullets, tables)."""
    lines = (script or "").splitlines()
    total = len(lines)
    i = 0
    while i < total:
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        if line.startswith("|"):
            block = []
            while i < total and lines[i].strip().startswith("|"):
                block.append(lines[i].strip())
                i += 1
            _render_table(pdf, block, family, bold)
            pdf.ln(2)
            continue

        heading = re.match(r"^(#{1,6})\s+(.*)$", line)
        if heading:
            level = len(heading.group(1))
            size = 15 if level <= 2 else 12
            pdf.ln(2)
            pdf.set_font(family, bold, size)
            pdf.multi_cell(
                0, 8 if level <= 2 else 6, _plain(heading.group(2)),
                new_x=XPos.LMARGIN, new_y=YPos.NEXT,
            )
            pdf.ln(1)
            i += 1
            continue

        bullet = re.match(r"^[-*]\s+(.*)$", line)
        if bullet:
            _write_md_line(pdf, "\u2022 " + bullet.group(1), family, bold, indent=3)
            i += 1
            continue

        numbered = re.match(r"^(\d+)\.\s+(.*)$", line)
        if numbered:
            _write_md_line(
                pdf, numbered.group(1) + ". " + numbered.group(2), family, bold
            )
            i += 1
            continue

        _write_md_line(pdf, line, family, bold)
        i += 1


def _write_header(pdf, title, meta_line, family, bold):
    pdf.set_font(family, bold, 20)
    pdf.multi_cell(0, 9, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    if meta_line:
        pdf.set_font(family, "", 10)
        pdf.set_text_color(110, 110, 110)
        pdf.multi_cell(0, 5, meta_line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_text_color(0, 0, 0)
    pdf.ln(3)
    pdf.set_draw_color(210, 210, 210)
    y = pdf.get_y()
    pdf.line(MARGIN, y, pdf.w - MARGIN, y)
    pdf.ln(4)


def _write_strategy_page(pdf, strategy, family, bold):
    pdf.add_page()
    pdf.set_font(family, bold, 16)
    pdf.multi_cell(0, 8, "Strategy brief (internal)", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(2)
    for key, label in (
        ("audience", "Audience"),
        ("emotion_target", "Emotion target"),
        ("positioning", "Positioning"),
        ("pains", "Pains"),
        ("desires", "Desires"),
        ("hook_angles", "Hook angles"),
    ):
        value = strategy.get(key)
        if not value:
            continue
        if isinstance(value, (list, tuple)):
            value = " | ".join(_safe(v) for v in value)
        pdf.set_font(family, bold, 11)
        pdf.multi_cell(0, 6, label, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font(family, "", 11)
        pdf.multi_cell(0, 6, _safe(value), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(1)


def build_pdf(result, path: str, client_view: bool = True) -> str:
    """Render *result* to a PDF at *path*. Returns the path.

    Video ads keep their dedicated layout (labelled beats + shot-list table).
    Every other format uses a generic markdown layout so headings, bullets and
    tables all survive the export.
    """
    if FPDF is None:
        raise RuntimeError("fpdf2 is not installed. Run: pip install fpdf2")

    script = getattr(result, "script", "") or ""
    brief = getattr(result, "brief", {}) or {}
    strategy = getattr(result, "strategy", {}) or {}

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(True, margin=MARGIN)
    pdf.set_margins(MARGIN, MARGIN, MARGIN)
    pdf.add_page()

    font_path = _find_font(bold=False)
    bold_path = _find_font(bold=True)
    family = "Helvetica"
    bold = "B"
    if font_path:
        pdf.add_font("AdBody", "", font_path)
        family = "AdBody"
        if bold_path:
            pdf.add_font("AdBody", "B", bold_path)
        else:
            bold = ""

    brand = _safe(brief.get("brand")).strip()
    platform = _safe(brief.get("platform")).strip()
    goal = _safe(brief.get("goal")).strip()
    tone = _safe(brief.get("tone")).strip()

    meta = get_format(getattr(result, "format", "video_ad"))
    format_key = meta["key"] if meta else "video_ad"
    format_name = meta["name"] if meta else "Deliverable"

    if format_key == "video_ad":
        parsed = parse_script(script)
        title = parsed["title"] or (
            brand + " - " + format_name if brand else format_name
        )
        _write_header(pdf, title, "  |  ".join(p for p in (platform, goal, tone) if p), family, bold)

        for label, value in parsed["sections"]:
            if not value:
                continue
            if label:
                pdf.set_font(family, bold, 12)
                pdf.multi_cell(0, 6, label, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font(family, "", 12)
            pdf.multi_cell(0, 6, value, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(2)

        if parsed["shot_header"] and parsed["shot_rows"]:
            pdf.ln(3)
            pdf.set_font(family, bold, 14)
            pdf.multi_cell(0, 8, "Shot list", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            header, rows = parsed["shot_header"], parsed["shot_rows"]
            weights = _column_weights(header, ("voice", "audio", "visual", "text", "screen"))
            epw = pdf.epw
            col_widths = tuple(round(epw * w, 2) for w in weights)
            pdf.set_font(family, "", 9)
            with pdf.table(col_widths=col_widths, line_height=5) as table:
                head = table.row()
                for cell in header:
                    head.cell(cell)
                for row in rows:
                    r = table.row()
                    for cell in row:
                        r.cell(cell)
    else:
        title = brand + " - " + format_name if brand else format_name
        _write_header(pdf, title, "  |  ".join(p for p in (goal, tone) if p), family, bold)
        _render_markdown(pdf, script, family, bold)

    if not client_view and strategy:
        _write_strategy_page(pdf, strategy, family, bold)

    pdf.set_y(-15)
    pdf.set_font(family, "", 8)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 5, "AdScript Studio", align="C")

    pdf.output(path)
    return path


def _column_weights(header, wide_keywords):
    """Give wide columns (visual/audio/text) more room than short ones."""
    weights = []
    for col in header:
        lowered = _safe(col).lower()
        if any(k in lowered for k in ("visual", "audio", "voice", "text", "screen")):
            weights.append(3.0)
        elif any(k in lowered for k in ("time",)):
            weights.append(1.2)
        else:
            weights.append(0.8)
    total = sum(weights) or 1.0
    return [w / total for w in weights]


def _slug(text: str) -> str:
    text = _safe(text).strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "ad"


def build_pdf_file(result, client_view: bool = True, out_dir: str = None):
    """Build a PDF in a temp dir. Returns (path, filename)."""
    brief = getattr(result, "brief", {}) or {}
    slug = _slug(brief.get("brand") or "ad")
    suffix = "client" if client_view else "full"
    filename = "{0}-{1}.pdf".format(slug, suffix)
    directory = out_dir or tempfile.gettempdir()
    path = os.path.join(directory, filename)
    build_pdf(result, path, client_view=client_view)
    return path, filename
