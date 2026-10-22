# Strategy book v2 (EXP-005) — text for the player rules sheet
STRATEGY = [
    ("1. Set your hand (2 cards to Hold'em, 4 to Omaha)", [
        "<b>Three or four of a kind:</b> two of them in Hold'em.",
        "<b>Two or three pairs:</b> your highest pair in Hold'em.",
        "<b>One pair:</b> the pair in Hold'em. <i>Exception:</i> a pair of Tens or lower plus an unpaired <b>Ace and King</b> — put A-K in Hold'em.",
        "<b>No pair:</b>",
        "&nbsp;&nbsp;&nbsp;• second-highest card is a <b>Queen or higher</b> → your <b>two highest</b> cards in Hold'em;",
        "&nbsp;&nbsp;&nbsp;• otherwise, highest card is an <b>Ace or King</b> → that card with the <b>lowest card of its suit</b> (no card of its suit: with your lowest card);",
        "&nbsp;&nbsp;&nbsp;• otherwise → your <b>two lowest</b> cards in Hold'em.",
        "<b>Suits:</b> when you can choose, keep same-suited cards together in Omaha.",
        "<i>Why low cards?</i> You only lose your Base when you lose <b>both</b> hands — one very strong Omaha hand protects it.",
    ]),
    ("2. Before the flop — bet 4× with", [
        "• a Hold'em pair of <b>Jacks or better</b>;",
        "• <b>Tens</b> if 2+ of your Omaha cards are Ten or higher;",
        "• <b>Nines</b> if 3+ of your Omaha cards are Ten or higher;",
        "• <b>Ace-King</b> if 2+ of your Omaha cards are Ten or higher.",
        "Otherwise check.",
    ]),
    ("3. On the flop — bet 2× if any of these", [
        "• your <b>Omaha</b> hand already has <b>three of a kind or better</b> (using exactly 2 of its cards);",
        "• unpaired flop, and your <b>Hold'em</b> has <b>top pair or better</b> (top pair, overpair, two pair+) — on flops whose highest card is 7 or lower you need <b>two pair or better</b>;",
        "• unpaired flop, your <b>Omaha</b> has <b>two pair</b> and your <b>Hold'em</b> has any pair using one of its own cards;",
        "• paired flop, and your <b>Hold'em</b> has <b>three of a kind or better</b>.",
        "Otherwise check.",
    ]),
    ("4. At the river", ["If you haven't bet yet, bet <b>1×</b> (required)."]),
]
STRATEGY_NOTE = ("Strategy book v2. Against a perfect player the house edge is about 4.6% of the Base; "
                 "following this page gives a house edge of about 7.3%. Prototype math (simulation), not certified.")
