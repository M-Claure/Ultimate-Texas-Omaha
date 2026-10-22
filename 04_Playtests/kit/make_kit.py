"""Generate the UTO playtest kit PDFs (run: python3 make_kit.py OUTDIR).
Player mat, dealer mat, dealer reference card and session log. The player rules sheet is built by
make_rules_sheet.py (it carries the strategy book)."""
import sys, os
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle, Frame
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

OUT = sys.argv[1] if len(sys.argv) > 1 else "."
GREEN = colors.HexColor("#1d6b44"); DARK = colors.HexColor("#1b1b1b"); GOLD = colors.HexColor("#b8860b")
LIGHT = colors.HexColor("#e9f4ee")
TITLE = "ULTIMATE TEXAS OMAHA"
FOOT = "UTO playtest kit · Rules v0.3 · Prototype — confidential, do not distribute"
ss = getSampleStyleSheet()
body = ParagraphStyle("b", parent=ss["Normal"], fontName="Helvetica", fontSize=9.5, leading=12.5)
small = ParagraphStyle("s", parent=body, fontSize=8.5, leading=11)
h2 = ParagraphStyle("h2", parent=body, fontName="Helvetica-Bold", fontSize=11.5, leading=14, textColor=GREEN, spaceBefore=4, spaceAfter=2)


def card_spot(c, x, y, w=1.55 * inch, h=2.2 * inch, label=None):
    c.setStrokeColor(GREEN); c.setLineWidth(1.2); c.setDash(4, 3)
    c.roundRect(x, y, w, h, 8, stroke=1, fill=0); c.setDash()
    if label:
        c.setFillColor(GREEN); c.setFont("Helvetica", 8); c.drawCentredString(x + w / 2, y + h / 2 - 3, label)


def box(c, x, y, w, h, title, sub=None):
    c.setStrokeColor(GREEN); c.setLineWidth(2.2); c.setFillColor(LIGHT)
    c.roundRect(x, y, w, h, 14, stroke=1, fill=1)
    c.setFillColor(GREEN); c.setFont("Helvetica-Bold", 15); c.drawString(x + 14, y + h - 24, title)
    if sub:
        c.setFont("Helvetica", 9); c.setFillColor(DARK); c.drawString(x + 14, y + h - 38, sub)


def footer(c, W):
    c.setFont("Helvetica", 7.5); c.setFillColor(colors.grey); c.drawCentredString(W / 2, 0.3 * inch, FOOT)


def player_mat(path):
    W, H = landscape(letter); c = canvas.Canvas(path, pagesize=(W, H)); c.setTitle("UTO Player Mat")
    c.setFillColor(GREEN); c.setFont("Helvetica-Bold", 20); c.drawCentredString(W / 2, H - 0.55 * inch, TITLE)
    c.setFont("Helvetica", 9.5); c.setFillColor(DARK)
    c.drawCentredString(W / 2, H - 0.78 * inch, "Win BOTH hands to win  ·  win one = push  ·  a tie counts as a lost hand")
    # Hold'em box
    bx, by, bw, bh = 0.45 * inch, 3.15 * inch, 3.75 * inch, 3.95 * inch
    box(c, bx, by, bw, bh, "HOLD'EM", "2 cards · any 5 of 2 + board")
    for k in range(2):
        card_spot(c, bx + 0.25 * inch + k * 1.7 * inch, by + 0.35 * inch, label="card")
    # Omaha box
    ox, oy, ow, oh = 4.45 * inch, 3.15 * inch, 6.1 * inch, 3.95 * inch
    box(c, ox, oy, ow, oh, "OMAHA", "4 cards · exactly 2 of yours + exactly 3 board")
    for k in range(4):
        card_spot(c, ox + 0.22 * inch + k * 1.47 * inch, oy + 0.35 * inch, w=1.32 * inch, label="card")
    # Base circle
    c.setStrokeColor(GOLD); c.setLineWidth(3); c.setFillColor(colors.white)
    cx, cy, r = 1.75 * inch, 1.55 * inch, 0.95 * inch
    c.circle(cx, cy, r, stroke=1, fill=1)
    c.setFillColor(GOLD); c.setFont("Helvetica-Bold", 18); c.drawCentredString(cx, cy + 2, "BASE")
    c.setFont("Helvetica", 8.5); c.setFillColor(DARK); c.drawCentredString(cx, cy - 14, "pushes on a win")
    # Play box
    px, py, pw, ph = 3.25 * inch, 0.65 * inch, 3.3 * inch, 1.85 * inch
    c.setStrokeColor(GOLD); c.setLineWidth(3); c.setFillColor(colors.white); c.roundRect(px, py, pw, ph, 14, stroke=1, fill=1)
    c.setFillColor(GOLD); c.setFont("Helvetica-Bold", 18); c.drawCentredString(px + pw / 2, py + ph - 26, "PLAY")
    c.setFont("Helvetica-Bold", 10.5); c.setFillColor(DARK)
    for i, t in enumerate(["4×  before the flop", "2×  after the flop", "1×  after the river (required)"]):
        c.drawCentredString(px + pw / 2, py + ph - 50 - i * 15, t)
    c.setFont("Helvetica", 8.5); c.drawCentredString(px + pw / 2, py + 10, "one Play bet per hand · pays 1:1 on a win")
    # Pay reminder
    data = [["You win…", "Result", "Base", "Play"], ["both hands", "WIN", "push", "1:1"], ["one hand", "PUSH", "push", "push"], ["no hands", "LOSS", "lose", "lose"]]
    t = Table(data, colWidths=[0.95 * inch, 0.65 * inch, 0.6 * inch, 0.6 * inch])
    t.setStyle(TableStyle([("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 9), ("FONT", (0, 1), (-1, -1), "Helvetica", 9),
                           ("BACKGROUND", (0, 0), (-1, 0), GREEN), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                           ("GRID", (0, 0), (-1, -1), 0.5, colors.grey), ("ALIGN", (1, 0), (-1, -1), "CENTER")]))
    tw, th = t.wrap(0, 0); t.drawOn(c, 7.05 * inch, 0.85 * inch)
    c.setFont("Helvetica-Oblique", 8); c.setFillColor(DARK)
    c.drawString(7.05 * inch, 0.65 * inch, "Lock your split before the flop — no changes after.")
    footer(c, W); c.showPage(); c.save()


def dealer_mat(path):
    W, H = landscape(letter); c = canvas.Canvas(path, pagesize=(W, H)); c.setTitle("UTO Dealer Mat")
    c.setFillColor(GREEN); c.setFont("Helvetica-Bold", 20); c.drawCentredString(W / 2, H - 0.55 * inch, TITLE + " — DEALER")
    # board
    box(c, 0.45 * inch, 4.6 * inch, 10.1 * inch, 2.65 * inch, "BOARD")
    labels = ["FLOP", "FLOP", "FLOP", "TURN", "RIVER"]
    for k in range(5):
        card_spot(c, 0.8 * inch + k * 1.95 * inch, 4.75 * inch, w=1.55 * inch, h=2.1 * inch, label=labels[k])
    # dealer hands
    box(c, 0.45 * inch, 0.75 * inch, 3.75 * inch, 3.6 * inch, "DEALER HOLD'EM")
    for k in range(2):
        card_spot(c, 0.7 * inch + k * 1.7 * inch, 0.95 * inch, h=2.1 * inch)
    box(c, 4.45 * inch, 0.75 * inch, 6.1 * inch, 3.6 * inch, "DEALER OMAHA")
    for k in range(4):
        card_spot(c, 4.67 * inch + k * 1.47 * inch, 0.95 * inch, w=1.32 * inch, h=2.1 * inch)
    c.setFont("Helvetica-Oblique", 8.5); c.setFillColor(DARK)
    c.drawString(0.5 * inch, 0.55 * inch, "Dealer sets the hand by HOUSE WAY H (see dealer card) before any board card is shown. Burn one card before flop, turn and river.")
    footer(c, W); c.showPage(); c.save()


def dealer_card(path):
    W, H = letter; c = canvas.Canvas(path, pagesize=letter); c.setTitle("UTO Dealer Reference Card")
    c.setFillColor(GREEN); c.setFont("Helvetica-Bold", 17); c.drawString(0.6 * inch, H - 0.7 * inch, TITLE + " — Dealer Card")
    story = []
    P = lambda t, s=body: story.append(Paragraph(t, s))
    P("Procedure", h2)
    for t in ["1. Players place the <b>Base</b>. Shuffle one 52-card deck.",
              "2. Deal <b>6 cards</b> face down to each player and the dealer (max 6 players).",
              "3. Players set <b>2 cards in Hold'em</b> and <b>4 in Omaha</b>, face down, and tap the mat to lock. No changes after this.",
              "4. Dealer sets own hand by <b>House Way H</b> (below), face down.",
              "5. <b>Preflop:</b> each player may bet <b>4×</b> the Base in Play, or check.",
              "6. Burn 1, deal the <b>flop</b>. Players who have not bet may bet <b>2×</b>, or check.",
              "7. Burn 1, <b>turn</b>; burn 1, <b>river</b>. Players who have not bet <b>must bet 1×</b> (no folding).",
              "8. Dealer reveals and compares hand by hand: Hold'em vs Hold'em, Omaha vs Omaha (Omaha uses exactly 2 + 3). <b>A tie is a lost hand for the player.</b>",
              "9. Settle each player (table below)."]:
        P(t)
    P("House Way H — use the first step that applies", h2)
    for t in ["1. <b>Three or four of a kind:</b> two of them to Hold'em.",
              "2. <b>Two or three pairs:</b> the highest pair to Hold'em.",
              "3. <b>One pair:</b> 9s or higher → pair to Hold'em. 2s–8s → pair to Hold'em, <i>unless</i> you also hold two other cards both Jack or higher — then those two go to Hold'em.",
              "4. <b>No pair:</b> the two highest cards to Hold'em.",
              "5. <b>Suits:</b> if you can choose between cards of the same rank, keep same-suited cards together in Omaha; otherwise put the higher suit (♠ ♥ ♦ ♣) in Hold'em."]:
        P(t)
    P("Settlement", h2)
    t = Table([["Player wins…", "Result", "Base", "Play"], ["both hands", "WIN", "push (return)", "pay 1:1"],
               ["one hand", "PUSH", "push", "push"], ["no hands", "LOSS", "take", "take"]],
              colWidths=[1.5 * inch, 1.0 * inch, 1.3 * inch, 1.1 * inch])
    t.setStyle(TableStyle([("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 9.5), ("FONT", (0, 1), (-1, -1), "Helvetica", 9.5),
                           ("BACKGROUND", (0, 0), (-1, 0), GREEN), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                           ("GRID", (0, 0), (-1, -1), 0.5, colors.grey)]))
    story.append(t)
    P("Examples (Base $10)", h2)
    for t in ["• Played 4× ($40), won both → pay $40; Base returned.",
              "• Played 2× ($20), won Hold'em, lost Omaha → push everything.",
              "• Played 1× ($10), won Hold'em, <b>tied</b> Omaha → push (tie = lost hand, one win).",
              "• Played 1× ($10), lost both → take $20."]:
        P(t)
    P("House Way examples", h2)
    t = Table([["Dealer's six cards", "Hold'em", "Why"],
               ["5♣ 5♦ A♠ K♥ 9♣ 2♦", "A♠ K♥", "small pair, A & K both J+"],
               ["5♣ 5♦ A♠ T♥ 9♣ 2♦", "5♣ 5♦", "T is below Jack"],
               ["9♣ 9♦ A♠ K♥ 7♣ 2♦", "9♣ 9♦", "9s or higher"],
               ["9♣ 9♦ 4♠ 4♥ A♣ 2♦", "9♣ 9♦", "highest pair"],
               ["A♣ J♦ 9♠ 7♥ 4♣ 2♦", "A♣ J♦", "no pair: two highest"]],
              colWidths=[2.0 * inch, 1.0 * inch, 2.4 * inch])
    t.setStyle(TableStyle([("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 9), ("FONT", (0, 1), (-1, -1), "DejaVu" if False else "Helvetica", 9),
                           ("BACKGROUND", (0, 0), (-1, 0), LIGHT), ("GRID", (0, 0), (-1, -1), 0.5, colors.grey)]))
    story.append(t)
    Frame(0.6 * inch, 0.55 * inch, W - 1.2 * inch, H - 1.45 * inch, showBoundary=0).addFromList(story, c)
    footer(c, W); c.showPage(); c.save()


def session_log(path):
    W, H = landscape(letter); c = canvas.Canvas(path, pagesize=(W, H)); c.setTitle("UTO Playtest Session Log")
    c.setFillColor(GREEN); c.setFont("Helvetica-Bold", 16); c.drawString(0.5 * inch, H - 0.6 * inch, "UTO Playtest — Session Log")
    c.setFont("Helvetica", 9.5); c.setFillColor(DARK)
    c.drawString(0.5 * inch, H - 0.85 * inch, "Session ID (PT-###): ________   Date: ____________   Rules version: v0.3   Dealer: ______________   Players (initials, NDA Y/N): ______________________________________")
    cols = ["Hand", "Seat", "Split time (s)", "Bet (4/2/1×)", "Hold'em W/L/T", "Omaha W/L/T", "Result W/P/L", "Net (units)", "Dealer error?", "Notes / questions asked"]
    widths = [0.45, 0.45, 0.85, 0.85, 0.9, 0.9, 0.85, 0.75, 0.8, 3.2]
    data = [cols] + [[""] * len(cols) for _ in range(24)]
    t = Table(data, colWidths=[w * inch for w in widths], rowHeights=[0.32 * inch] + [0.255 * inch] * 24)
    t.setStyle(TableStyle([("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 7.5), ("BACKGROUND", (0, 0), (-1, 0), LIGHT),
                           ("GRID", (0, 0), (-1, -1), 0.4, colors.grey), ("VALIGN", (0, 0), (-1, 0), "MIDDLE")]))
    tw, th = t.wrap(0, 0); t.drawOn(c, 0.5 * inch, H - 1.05 * inch - th)
    footer(c, W); c.showPage()
    # feedback page
    c.setFillColor(GREEN); c.setFont("Helvetica-Bold", 16); c.drawString(0.5 * inch, H - 0.6 * inch, "UTO Playtest — Player Feedback (one per player)")
    qs = ["How easy was it to understand the rules? (1 = very hard … 5 = very easy)",
          "How long did splitting your six cards feel? (1 = way too long … 5 = quick)",
          "How fun was the game overall? (1 … 5)",
          "How did the frequent pushes feel? (1 = boring … 5 = fine / exciting)",
          "How did it feel that a tie counts as a lost hand? (1 = unfair … 5 = fine)",
          "How did it feel that the Base never wins (it pushes when you win)? (1 = bad … 5 = fine)",
          "How did the required 1× bet at the river feel? (1 = bad … 5 = fine)",
          "Would you play this in a casino over Ultimate Texas Hold'em? (Y / N / Maybe)",
          "What confused you?",
          "What would make it more fun?"]
    y = H - 1.1 * inch
    c.setFont("Helvetica", 10); c.setFillColor(DARK)
    c.drawString(0.5 * inch, y, "Player initials: ______    Poker experience: none / casual / regular    Plays casino table games: Y / N"); y -= 0.42 * inch
    for i, q in enumerate(qs, 1):
        c.drawString(0.5 * inch, y, f"{i}. {q}")
        y -= 0.2 * inch
        c.setStrokeColor(colors.lightgrey); c.line(0.75 * inch, y, W - 0.5 * inch, y)
        y -= (0.42 if i >= 9 else 0.3) * inch
    footer(c, W); c.showPage(); c.save()


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    player_mat(os.path.join(OUT, "UTO_Player_Mat.pdf"))
    dealer_mat(os.path.join(OUT, "UTO_Dealer_Mat.pdf"))
    dealer_card(os.path.join(OUT, "UTO_Dealer_Card.pdf"))
    session_log(os.path.join(OUT, "UTO_Session_Log.pdf"))
    print("ok")
