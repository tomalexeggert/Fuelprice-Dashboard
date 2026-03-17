import dash
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/competition")

layout = dbc.Container([
    html.Br(),
    dbc.Row([
        dbc.Col([
            html.H1("dfgdfgn")
        ])
    ])
])