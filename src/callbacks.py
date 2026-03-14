from dash import Input, Output
from src.figures import plot_national_fuel_prices_year

def register_callbacks(app):
    @app.callback(
        Output("national-fuel-prices-graph", "figure"),
        Input("year-dropdown", "value")
    )
    def update_national_fuel_prices_graph(year):
        fig = plot_national_fuel_prices_year(year)
        return fig
    
    def update_plot():
        pass
    #Moin