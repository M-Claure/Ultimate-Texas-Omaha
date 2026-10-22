"""One-page player rules sheet (front: how to play; back: strategy book). Run: python3 make_rules_sheet.py OUTDIR"""
import sys, os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle, Frame, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from strategy_text import STRATEGY, STRATEGY_NOTE

OUT = sys.argv[1] if len(sys.argv) > 1 else "."
GREEN = colors.HexColor("#1d6b44"); LIGHT = colors.HexColor("#e9f4ee")
ss = getSampleStyleSheet()
body = ParagraphStyle("b", parent=ss["Normal"], fontName="Helvetica", fontSize=10, leading=13.2)
h2 = ParagraphStyle("h2", parent=body, fontName="Helvetica-Bold", fontSize=12, leading=15, textColor=GREEN, spaceBefore=6, spaceAfter=2)
note = ParagraphStyle("n", parent=body, fontSize=8.5, leading=11, textColor=colors.HexColor("#444444"))
FOOT = "UTO playtest kit · Rules v0.3 · Prototype — confidential, do not distribute"


def page(c, title, story):
    W, H = letter
    c.setFillColor(GREEN); c.setFont("Helvetica-Bold", 18); c.drawString(0.6 * inch, H - 0.7 * inch, title)
    Frame(0.6 * inch, 0.55 * inch, W - 1.2 * inch, H - 1.4 * inch, showBoundary=0).addFromList(story, c)
    c.setFont("Helvetica", 7.5); c.setFillColor(colors.grey); c.drawCentredString(W / 2, 0.3 * inch, FOOT)
    c.showPage()


def tbl(data, widths, header=True):
    t = Table(data, colWidths=[w * inch for w in widths])
    st = [("FONT", (0, 0), (-1, -1), "Helvetica", 9.5), ("GRID", (0, 0), (-1, -1), 0.5, colors.grey)]
    if header:
        st += [("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 9.5), ("BACKGROUND", (0, 0), (-1, 0), GREEN), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white)]
    t.setStyle(TableStyle(st)); return t


def build(path):
    c = canvas.Canvas(path, pagesize=letter); c.setTitle("UTO Player Rules")
    P = lambda t, s=body: Paragraph(t, s)
    s1 = [P("Two hands, one board. Beat the dealer with <b>both</b> to win.", h2),
          P("You and the dealer each get <b>six cards</b>. Split yours into a <b>2-card Texas Hold'em</b> hand and a <b>4-card Omaha</b> hand. Both hands play against the same five community cards."),
          P("How a hand goes", h2)]
    for t in ["<b>1. Bet the Base.</b> One unit, before the cards are dealt.",
              "<b>2. Set your hands.</b> Put 2 cards in the Hold'em box and 4 in the Omaha box. Tap to lock — no changes after this. The dealer sets their hand by a fixed house way.",
              "<b>3. Make one Play bet</b> — the earlier, the bigger:",
              "&nbsp;&nbsp;&nbsp;• before the flop: <b>4×</b> your Base, or check",
              "&nbsp;&nbsp;&nbsp;• after the flop: <b>2×</b>, or check",
              "&nbsp;&nbsp;&nbsp;• after the river: <b>1×</b> — required if you haven't bet yet (no folding)",
              "<b>4. Showdown.</b> Your Hold'em plays the dealer's Hold'em; your Omaha plays the dealer's Omaha."]:
        s1.append(P(t))
    s1 += [P("Hand rules", h2),
           P("• <b>Hold'em:</b> best five cards from your 2 cards and the 5 board cards — any combination (you may play the board)."),
           P("• <b>Omaha:</b> exactly <b>2</b> of your 4 cards plus exactly <b>3</b> board cards."),
           P("• <b>A tie counts as a lost hand.</b>"),
           P("Payouts", h2),
           tbl([["You win…", "Result", "Base", "Play"], ["both hands", "WIN", "push (returned)", "pays 1:1"],
                ["one hand", "PUSH", "push", "push"], ["no hands", "LOSS", "loses", "loses"]], [1.6, 1.0, 1.5, 1.2]),
           Spacer(1, 6), P("Examples ($10 Base)", h2),
           tbl([["Play bet", "What happened", "You get"], ["4× ($40)", "Won both hands", "+$40"],
                ["2× ($20)", "Won Hold'em, lost Omaha", "$0 (push)"], ["1× ($10)", "Won Hold'em, tied Omaha", "$0 (tie = lost hand → push)"],
                ["1× ($10)", "Lost both", "−$20"]], [1.2, 2.6, 2.4]),
           Spacer(1, 6), P("Tip: you only lose your Base when you lose <b>both</b> hands. Turn the page for how to play your hand.", note)]
    page(c, "ULTIMATE TEXAS OMAHA — How to Play", s1)
    s2 = []
    for title, lines in STRATEGY:
        s2.append(P(title, h2))
        for ln in lines:
            s2.append(P(ln))
    s2 += [Spacer(1, 8), P(STRATEGY_NOTE, note)]
    page(c, "ULTIMATE TEXAS OMAHA — How to Play Your Hand", s2)
    c.save()


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True); build(os.path.join(OUT, "UTO_Player_Rules_Sheet.pdf")); print("ok")
