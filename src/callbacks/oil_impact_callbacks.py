from dash import Input, Output
from src.figures.oil_impact_figures import plot_national_fuel_prices_year,plot_ccf_oil_to_fuel

def register_oil_callbacks(app):
    @app.callback(
        Output("national-fuel-prices-graph", "figure"),
        Input("year-dropdown", "value")
    )
    def update_national_fuel_prices_graph(year):
        fig = plot_national_fuel_prices_year(year)
        return fig
    
    @app.callback(
        Output("diesel-ccf-graph-year", "figure"),
        Output("e5-ccf-graph-year", "figure"),
        Output("e10-ccf-graph-year", "figure"),
        Input("year-dropdown", "value")
    )
    def update_ccf_oil_to_fuel_graphs(year):
        diesel_fig = plot_ccf_oil_to_fuel(year=year, fuel_type="diesel")
        e5_fig = plot_ccf_oil_to_fuel(year=year, fuel_type="e5")
        e10_fig = plot_ccf_oil_to_fuel(year=year, fuel_type="e10")
        return diesel_fig, e5_fig, e10_fig