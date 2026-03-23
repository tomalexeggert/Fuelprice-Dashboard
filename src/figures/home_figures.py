TARGETS = {
    "stations-total": 14442,
    "repo-size": 125,
    "rows-total": 2323917540,
    "price-changes": 470297,
}


def ease_out(progress: float) -> float:
    """Apply a cubic ease-out curve to an animation progress value."""
    return 1 - (1 - progress) ** 3


def format_number(value: int | float) -> str:
    """Format a number with German-style thousands separators."""
    return f"{value:,}".replace(",", ".")
