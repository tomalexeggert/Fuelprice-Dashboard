TARGETS = {
    "stations-total": 14442,
    "repo-size": 125,
    "rows-total": 2323917540,
    "price-changes": 470297,
}

def ease_out(progress: float) -> float:
    return 1 - (1 - progress) ** 3


def format_number(value):
    return f"{value:,}".replace(",", ".")