import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/stations")

layout = dbc.Container([
    html.H1("Station Comparison"),
    html.P("Brand Comparison") # du musst "P" groß schreiben, nicht klein!!
])