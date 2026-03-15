import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/oil-impact")

layout = dbc.Container([
    html.Br(),
    dbc.Row([
        dbc.Col(
            html.H1("Oil Price Impact", style={"textAlign": "center"}),
            width=12
        )
    ]),
    html.Br(),
    dbc.Row([ # Year Dropdown
        dbc.Col([
            html.Label("Year"),
            dcc.Dropdown(
                id="year-dropdown",
                options=[{"label": str(y), "value": y} for y in range(2014, 2027)],
                value=2025,
                clearable=False
            )
        ], width=12),
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col(
            dcc.Graph(id="national-fuel-prices-graph"),
            width=12
        )
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardHeader("Explaining the CCF Plot and Log-Returns"),
                dbc.CardBody([
                    dcc.Markdown(
                        r"""
### Using
Log-Return:
$$
r_t = \log(P_t) - \log(P_{t-1}) = \log\left(\frac{P_t}{P_{t-1}}\right)
$$
therefore we get approximate %-change (for smaller changes):
$$
r_t \approx \frac{P_t - P_{t-1}}{P_{t-1}}
$$
thus the process is now $\approx$ stationary.
Now you can use the Cross-Correlation-Function (CCF):
$$
\text{corr}(r_t^{fuel}, r_{t-k}^{oil})
$$
### Significance of Cross-Correlations
To determine whether a correlation is statistically significant we use an approximate **95\% confidence interval**.  
A lag $k$ is considered statistically significant if
$$
|\hat{\rho}_k| > \frac{1.96}{\sqrt{N}}
$$
In the CCF plot these thresholds appear as horizontal dashed lines.  
Any lag outside this band indicates a statistically significant relationship
between oil price changes and fuel price changes.
                        """,
                        mathjax=True,
                    ),
                ])
            ]),
            width=12
        )
    ]),
    html.Br(),
], fluid=True)
