from dash import Dash
import dash_bootstrap_components as dbc
from src.layout import create_layout

app = Dash(__name__, external_stylesheets=[dbc.themes.COSMO])

app.layout = create_layout()

if __name__ == "__main__":
    app.run(debug=True)