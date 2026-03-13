import dash
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc

app = Dash(__name__, external_stylesheets=[dbc.themes.COSMO])

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Fuel Price Dashboard", style={'textAlign': 'center'})
        ], width=12)
    ])
])

app.layout = dbc.Container([
    html.Br(),
    dbc.Row([
        dbc.Col(
            html.H1("Fuel Price Dashboard", style={'textAlign': 'center'}),
            width=12
        )
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H4("Test Card"),
                    html.P("should show"),
                    dbc.Button("Test Button", color="primary")
                ])
            ),
            width=6
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    dcc.Markdown("### Price Spread Diff. between **Premium** and **Regular**"),
                    dcc.Markdown("Diff. between **Premium** and **Regular** fuel price."),
                    dcc.Markdown("**Positive** value indicates that Premium is more expensive than Regular, while **Negative** value indicates that Premium is cheaper than Regular. \n **hallo**")
                ])
            ),
            width=6
        )
    ])
], fluid=True)



if __name__ == '__main__':
    app.run(debug=True)