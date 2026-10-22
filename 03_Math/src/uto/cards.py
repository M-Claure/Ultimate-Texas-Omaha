"""Card helpers (pure Python, for I/O and tests)."""
RANKS = "23456789TJQKA"
SUITS = "cdhs"  # suit order for tie-breaks: s > h > d > c


def card(s: str) -> int:
    """'As' -> 51, '2c' -> 0."""
    return RANKS.index(s[0].upper()) * 4 + SUITS.index(s[1].lower())


def cards(s: str) -> list[int]:
    """'As Kd 7h' -> [51, 45, 22]."""
    return [card(t) for t in s.split()]


def name(c: int) -> str:
    return RANKS[c // 4] + SUITS[c % 4]


def names(cs) -> str:
    return " ".join(name(int(c)) for c in cs)
