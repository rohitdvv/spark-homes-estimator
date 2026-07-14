#!/usr/bin/env python3
"""Generate the Spark Homes build writeup as a single-page PDF."""

from fpdf import FPDF
import os

DIR = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(DIR, "Spark_Homes_Writeup.pdf")

# Brand colour
SPARK = (208, 80, 0)
BLACK = (26, 26, 26)
GREY = (100, 100, 100)
WHITE = (255, 255, 255)


class WriteupPDF(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="letter")
        self.set_auto_page_break(auto=False)


def build():
    pdf = WriteupPDF()
    pdf.add_page()
    pw = pdf.w - pdf.l_margin - pdf.r_margin  # printable width

    # ── HEADER ──
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(*SPARK)
    pdf.cell(pw * 0.6, 8, "Spark Homes - Build Writeup")
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(*GREY)
    pdf.cell(pw * 0.4, 8, "Repair Cost Estimator  |  Offline-First PWA  |  Single-File", align="R")
    pdf.ln(10)
    # orange rule
    pdf.set_draw_color(*SPARK)
    pdf.set_line_width(0.7)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
    pdf.ln(5)

    def section_heading(num, title):
        x0 = pdf.get_x()
        y0 = pdf.get_y()
        r = 3
        pdf.set_fill_color(*SPARK)
        pdf.ellipse(x0, y0 + 0.3, r * 2, r * 2, style="F")
        pdf.set_xy(x0, y0 + 0.1)
        pdf.set_text_color(*WHITE)
        pdf.set_font("Helvetica", "B", 8)
        pdf.cell(r * 2, r * 2, str(num), align="C")
        pdf.set_xy(x0 + r * 2 + 2, y0)
        pdf.set_text_color(*SPARK)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 6.5, title)
        pdf.ln(7.5)

    def body_text(text, size=9):
        pdf.set_font("Helvetica", "", size)
        pdf.set_text_color(*BLACK)
        pdf.multi_cell(0, 4.2, text)

    def bullet(bold_part, rest, size=9):
        x0 = pdf.l_margin + 4
        pdf.set_x(x0)
        pdf.set_font("Helvetica", "", size)
        pdf.set_text_color(*SPARK)
        bullet_char = "-"
        pdf.cell(4, 4.2, bullet_char + " ")
        bw = pdf.get_string_width(bold_part) + 0.5
        pdf.set_text_color(*BLACK)
        pdf.set_font("Helvetica", "B", size)
        pdf.cell(bw, 4.2, bold_part)
        pdf.set_font("Helvetica", "", size)
        w_remain = pdf.w - pdf.get_x() - pdf.r_margin
        pdf.multi_cell(w_remain, 4.2, rest)

    # ── 1. MOST INTERESTING DESIGN DECISION ──
    section_heading(1, "Most Interesting Design / UX Decision")
    body_text(
        'Composite flat-map keying instead of nested data. The entire estimate is stored as a flat '
        '"cells" map keyed by "roomId|groupId|itemId". Every room, group, and line-item interaction '
        'resolves to a single string lookup -- no tree traversal, no recursive serialization. '
        'This was counterintuitive for a hierarchical UI (rooms > groups > items), but it made the '
        'hardest operations trivial: deleting a room is a prefix sweep over Object.keys; computing a '
        'room total is a filter + reduce; the entire state serializes to localStorage in one JSON.stringify. '
        'It enabled a single render() function that rebuilds the screen in one pass with template literals. '
        'The trade-off is fragility to key-format changes, but for a contest-scoped app, the simplicity won -- '
        'and it eliminated a full class of stale-reference bugs from an earlier nested-object prototype.'
    )
    pdf.ln(3)

    # ── 2. BROKEN / FRAGILE ──
    section_heading(2, "What Is Broken or Fragile")
    bullet("localStorage quota on large projects. ",
           "Photos are base64-encoded inline. 50+ high-res photos approach the ~5 MB limit on some "
           "browsers, causing silent save failures. Images are compressed to <=1280 px and writes are "
           "quota-checked, but there is no migration to IndexedDB -- a production version needs that.")
    pdf.ln(1)
    bullet("Full re-render on every mutation. ",
           "The render()-rebuilds-everything pattern causes scroll-position loss and input-focus jank "
           "on fast interactions. Partial re-renders exist for the worst cases, but a keyed "
           "reconciliation or virtual DOM diff would be the real fix.")
    pdf.ln(1)
    bullet("AI model load time. ",
           "The Whisper + CLIP + MiniLM offline pack is ~90 MB. First download on slow connections "
           "can time out with no chunked/resumable download and limited error recovery.")
    pdf.ln(1)
    bullet("Single-file scale. ",
           "At 3,100+ lines / 230 KB in one file, index.html is near the maintainability limit. "
           "A production follow-up would split into ES modules behind a minimal bundler.")
    pdf.ln(3)

    # ── 3. CREATIVE ADDITION ──
    section_heading(3, "Creative Addition & Why")
    body_text(
        "The Deal Analyzer + AI Copilot layer -- built as a single creative system, not a cosmetic feature."
    )
    pdf.ln(1)
    bullet("Deal Analyzer: ",
           'The brief says the repair estimate is the most important number -- but an estimate alone '
           'doesn\'t answer "should I buy this house?" The Deal Analyzer pulls the live repair total, '
           'adds ARV, purchase price, holding/selling costs, then projects profit, ROI, and a 70%-rule '
           'max offer with a GO / CAUTION / NO-GO verdict. The agent gets a buy-or-walk answer while '
           'still standing in the house.')
    pdf.ln(1)
    bullet("AI Copilot (100% offline): ",
           "Four specialist modules -- Inspection Coverage (flags missed big-ticket systems like HVAC, "
           "foundation, rewire), Recommendations (commonly-paired work: flooring > trim-out, furnace > "
           "duct cleaning), Anomaly & Risk (outlier quantities, price-override fraud, conflicting scope), "
           "and a semantic chat Assistant backed by on-device MiniLM embeddings over a repair-guidelines "
           "knowledge base. No API key, no server.")
    pdf.ln(1)
    bullet("Voice Walkthrough + Camera Scope Detection: ",
           "Narrate repairs hands-free; on-device Whisper transcribes, a synonym + semantic matcher "
           "adds items with correct quantities. Point the camera at a fixture; CLIP classifies it and "
           "suggests the line item. Both work fully offline.")
    pdf.ln(3)

    # ── 4. SHIP NEXT ──
    section_heading(4, "What I'd Ship Next (Two More Days)")
    bullet("IndexedDB photo storage + cloud sync. ",
           "Migrate photos from base64-in-localStorage to IndexedDB blobs (removes the quota wall), "
           "then add optional Firebase/Supabase sync with conflict resolution so a team of agents can "
           "share estimates live. The flat-key data model makes merge logic straightforward -- "
           "last-write-wins per cell key.")
    pdf.ln(1)
    bullet("Comp-based ARV assistant. ",
           "Integrate a public MLS data source (Redfin/Zillow API or scraped comps) so the Deal "
           "Analyzer auto-suggests an ARV from recent sold comps. Display comps on a map with "
           "price/sqft overlays and confidence bands. This closes the last manual gap in deal math.")
    pdf.ln(4)

    # ── AI ROLE BOX ──
    y_box = pdf.get_y()
    x_box = pdf.l_margin

    # Measure the AI text first
    pdf.set_xy(x_box + 3, y_box + 3)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*SPARK)
    pdf.cell(0, 5.5, "Role of AI Tools in Development")
    pdf.ln(6.5)
    pdf.set_x(x_box + 3)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*BLACK)
    ai_text = (
        "AI coding assistants (Claude, Gemini) were used extensively as a pair-programming partner. "
        "Specifically: (a) architecture brainstorming -- sketching the flat-key data model, the layered "
        "Copilot resolver, and the offline-first service-worker strategy; (b) rapid prototyping -- generating "
        "boilerplate for the 108-item price-list mapping, SVG chart code (donut arcs, waterfall, speedometer), "
        "and the semantic-search pipeline; (c) debugging -- diagnosing scroll-position bugs in the re-render "
        "loop, iOS PWA quirks, and Transformers.js WASM threading issues; (d) writing -- drafting README, "
        "ARCHITECTURE.md, and this writeup. All AI-generated code was reviewed, tested, and iterated by hand. "
        "The AI did not autonomously design features or make product decisions; it accelerated implementation "
        "of decisions I made."
    )
    pdf.multi_cell(pw - 6, 4.2, ai_text)
    y_end = pdf.get_y() + 3

    # Draw border
    pdf.set_draw_color(*SPARK)
    pdf.set_line_width(0.4)
    pdf.rect(x_box, y_box, pw, y_end - y_box, style="D")

    # ── FOOTER ──
    pdf.set_y(y_end + 4)
    pdf.set_draw_color(200, 200, 200)
    pdf.set_line_width(0.2)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
    pdf.ln(2)
    pdf.set_font("Helvetica", "", 7)
    pdf.set_text_color(160, 160, 160)
    pdf.cell(0, 4, "Spark Homes Repair Estimator  |  github.com/rohitdvv/spark-homes-estimator  |  "
             "Built as a single self-contained HTML file, offline-first PWA", align="C")

    pdf.output(OUT)
    print(f"PDF saved to: {OUT}")


if __name__ == "__main__":
    build()
