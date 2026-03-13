import dash
from dash import Dash, html, dcc, Input, Output

app = Dash(__name__)

app.layout = html.Div([
    html.H1("Fuel Price Dashboard"),
    html.P("Dash test")
])

if __name__ == '__main__':
    app.run(debug=True)