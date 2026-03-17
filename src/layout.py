import dash
from dash import html, dcc
import dash_bootstrap_components as dbc


def create_navbar():
    return dbc.NavbarSimple(
        brand="Fuel Price Dashboard",
        children=[
            dbc.NavItem(dbc.NavLink("Home", href="/")),
            dbc.NavItem(dbc.NavLink("Oil Impact", href="/oil-impact")),
            dbc.NavItem(dbc.NavLink("Stations", href="/stations")),
            dbc.NavItem(dbc.NavLink("Competition", href="/competition"))
        ],
        color="primary",
        dark=True
    )


def create_main_layout():
    return dbc.Container([
        create_navbar(),
        html.Br(),
        dash.page_container
    ], fluid=True)