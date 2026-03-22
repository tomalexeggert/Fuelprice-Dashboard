import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/references")

layout = dbc.Container([
    dbc.Row([
        html.H1("References", style={"textAlign": "center"}, className="my-4"),
    ]),
    dbc.Row(
        dbc.Col(dbc.Card([
            dbc.CardHeader(html.H5("Data Sources", className="mb-0 text-center")),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.H6(html.A("Tankerkönig – Historical Fuel Prices (Germany)", href="https://tankerkoenig.de", target="_blank")),
                        html.P("Provides daily CSV files with fuel prices (E5, E10, Diesel) and gas station data across Germany. "
                               "Data is structured by date: prices/YYYY/MM/YYYY-MM-DD-prices.csv and "
                               "stations/YYYY/MM/YYYY-MM-DD-stations.csv."),
                        html.P([html.Strong("License: "), html.A("Creative Commons BY-NC-SA 4.0 (non-commercial)", href="https://creativecommons.org/licenses/by-nc-sa/4.0/", target="_blank")]),
                    ], md=4),
                    dbc.Col([
                        html.H6(html.A("Yahoo Finance – Oil Prices (via yfinance)", href="https://finance.yahoo.com", target="_blank")),
                        html.P("Provides historical and real-time commodity market data. Used in this dashboard to retrieve "
                               "crude oil price data (e.g. Brent, WTI) as a macroeconomic reference for fuel price analysis."),
                        html.P([html.Strong("Access: "), "Python library ", html.Code("yfinance"), " (open source)"]),
                    ], md=4),
                    dbc.Col([
                        html.H6(html.A("OpenStreetMap – Map Tiles & Geodata", href="https://www.openstreetmap.org", target="_blank")),
                        html.P("Free, editable geographic database maintained by a global community. "
                               "Used in this dashboard as the base map layer for displaying gas station locations across Germany."),
                        html.P([html.Strong("License: "), html.A("Open Data Commons ODbL", href="https://opendatacommons.org/licenses/odbl/", target="_blank")]),
                    ], md=4),
                ], className="text-center"),
                html.Hr(),
                dbc.Row([
                    dbc.Col([
                        html.H6(html.A("Open-Meteo – Weather Data", href="https://open-meteo.com", target="_blank")),
                        html.P("Free weather API providing historical and forecast data including temperature, precipitation, "
                               "wind speed, and more. Used in this dashboard to correlate weather conditions with fuel consumption patterns."),
                        html.P([html.Strong("License: "), "Free for non-commercial use – ", html.A("open-meteo.com/en/license", href="https://open-meteo.com/en/license", target="_blank")]),
                    ], md=4),
                    dbc.Col([
                        html.H5(html.A("Other References:")),
                        html.P("Statistisches Bundesamt (DESTATIS)"),
                        html.P("ADAC"),
                        html.P("Spiegel Online"),
                        html.P("Wikipedia"),                       
                        html.A("WBZ Social Science Center", href="https://github.com/WZBSocialScienceCenter/plz_geocoord", target="_blank")
                    ])
                ], className="text-center mt-3 justify-content-center"),
            ])
        ]), md=10, className="mx-auto"),
        className="mb-4 justify-content-center",
    ),
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("Some of our frequently used Libraries"),
            dbc.CardBody(
                dbc.Table([
                    html.Thead(html.Tr([html.Th("Library"), html.Th("Version"), html.Th("Purpose")])),
                    html.Tbody([
                        html.Tr([html.Td(html.A("polars",                    href="https://pola.rs",                                                target="_blank")), html.Td("1.39.2"), html.Td("PERFORMANT data manipulation and analysis")]),
                        html.Tr([html.Td(html.A("dash",                      href="https://dash.plotly.com",                                        target="_blank")), html.Td("4.0.0"),  html.Td("Web application framework")]),
                        html.Tr([html.Td(html.A("dash-bootstrap-components", href="https://dash-bootstrap-components.opensource.faculty.ai",        target="_blank")), html.Td("2.0.4"),  html.Td("Bootstrap UI components for Dash")]),
                        html.Tr([html.Td(html.A("plotly",                    href="https://plotly.com/python",                                      target="_blank")), html.Td("6.6.0"),  html.Td("Interactive charts and graphs")]),
                        html.Tr([html.Td(html.A("pandas",                    href="https://pandas.pydata.org",                                      target="_blank")), html.Td("3.0.1"),  html.Td("Data manipulation and analysis")]),
                        html.Tr([html.Td(html.A("numpy",                     href="https://numpy.org",                                              target="_blank")), html.Td("2.4.3"),  html.Td("Numerical computing")]),
                        html.Tr([html.Td(html.A("statsmodels",               href="https://www.statsmodels.org",                                    target="_blank")), html.Td("0.14.6"), html.Td("Statistical models and tests")]),
                        html.Tr([html.Td(html.A("yfinance",                  href="https://github.com/ranaroussi/yfinance",                         target="_blank")), html.Td("1.2.0"),  html.Td("Yahoo Finance market data")]),
                    ])
                ], bordered=True, hover=True, striped=True, size="sm")
            )
        ]), md=12),
    ]),
    html.Hr(className="mt-4"),
    html.P("Tom · Sebastian · Bjarne · Marvin", className="text-center text-muted mb-1"),
    html.P("Data Science Project · Christian-Albrechts-Universität zu Kiel · March 2026", className="text-center text-muted mb-4"),
])
