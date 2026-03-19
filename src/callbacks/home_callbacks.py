from dash import Input, Output
from src.figures.home_figures import TARGETS, ease_out, format_number

def register_home_callbacks(app):

    @app.callback(
        Output("stations-total", "children"),
        Output("repo-size", "children"),
        Output("rows-total", "children"),
        Output("price-changes", "children"),
        Input("counter-interval", "n_intervals"),
    )
    def animate_counters(n):
        max_steps = 80
        progress = min(n / max_steps, 1)
        progress = ease_out(progress)

        stations = int(TARGETS["stations-total"] * progress)
        repo = int(TARGETS["repo-size"] * progress)
        rows = int(TARGETS["rows-total"] * progress)
        changes = int(TARGETS["price-changes"] * progress)

        return (
            format_number(stations),
            f"{repo} GB",
            format_number(rows),
            format_number(changes),
        )