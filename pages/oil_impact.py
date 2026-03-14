import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/oil-impact")

layout = dbc.Container([
    html.H1("Oil Price Impact"),
    dcc.Graph(id="oil-impact-graph")
])