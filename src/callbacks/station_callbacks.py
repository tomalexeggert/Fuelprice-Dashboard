from dash import Input, Output
from src.figures.station_figures import plot_brand_comparison, plot_avg_premium_per_brand


def register_station_callbacks(app):
    @app.callback(
        Output("brand-comparison-graph", "figure"),
        Input("fuel-buttons", "value")
    )
    def update_brand_comparison_graph(fuel):
        return plot_brand_comparison(fuel=fuel)

    @app.callback(
        Output("avg-premium-graph", "figure"),
        Input("fuel-buttons", "value")
    )
    def update_avg_premium_graph(fuel):
        return plot_avg_premium_per_brand(fuel=fuel)