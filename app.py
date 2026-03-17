import dash
from dash import Dash, html, dcc, dash_table
import dash_bootstrap_components as dbc
from src.layout import create_main_layout
from src.callbacks import register_callbacks

app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.DARKLY], suppress_callback_exceptions=True)

app.layout = create_main_layout()
register_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True)