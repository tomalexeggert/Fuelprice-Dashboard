from dash import Input, Output
from src.figures.station_figures import plot_brand_comparison


def register_station_callbacks(app):
    @app.callback(
        Output("brand-comparison-graph", "figure"),
        Input("fuel-dropdown", "value")
    )
    def update_brand_comparison_graph(fuel):
        return plot_brand_comparison(fuel=fuel)
