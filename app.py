import dash
from dash import Dash, html, dcc, dash_table
import dash_bootstrap_components as dbc
from src.layout import create_layout, create_main_layout

app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.SLATE])

app.layout = create_main_layout()

if __name__ == "__main__":
    app.run(debug=True)