import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from src.figures.station_figures import _FUEL_LABELS, plot_brand_vs_free_prices

dash.register_page(__name__, path="/stations")

layout = dbc.Container([
    html.Br(),
    dbc.Row([
        dbc.Col(html.H1("Brand gas stations vs. free gas stations", style={"textAlign": "center"}), width=12)
    ]),
    html.Br(),

    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    dcc.Markdown(
                        r"""
On this page you can see a comparison between branded gas stations and independent (free) gas stations
based on their average fuel prices over time.
The main purpose of the page is to allow users to explore long-term pricing differences between
the two station types across different fuel categories.
"""
                    )
                ])
            ])
        )
    ]),
    html.Br(),

    html.P("""
            In the following three plots, the mean fuel prices of brand gas stations and independent (free)
            gas stations are compared over time for three different fuel types: Diesel, E5, and E10.
            Each plot represents the average annual price from 2014 to 2025:
           """),
    dbc.Row([
        dbc.Col(dcc.Graph(figure=plot_brand_vs_free_prices()), width=11)
    ], justify="center"),
    html.Br(),
    
    html.P("""
            Across all three fuel types, the overall price trends follow a very similar pattern.
            A key observation across all three plots is that brand gas stations are consistently slightly more expensive than free gas stations.
            In every fuel category, the line representing brand stations lies marginally above the line representing free stations.
            Although the price differences are generally small, the pattern is consistent across Diesel, E5, and E10 throughout the entire time period.
            """
    ),
    html.Br(),

    dbc.Row([
        dbc.Col([
            dbc.RadioItems(
                id="fuel-buttons",
                options=[{"label": label, "value": col} for col, label in _FUEL_LABELS.items()],
                value="diesel_mean",
                inline=True,
                input_class_name="btn-check",
                label_class_name="btn btn-outline-primary",
                label_checked_class_name="active",
            )
        ], width=12, class_name="d-flex justify-content-center"),
    ]),
    html.Br(),
    
    html.P("""
            The following plot compares the mean annual Diesel prices of several major branded gas stations 
            with the average price of independent (free) gas stations between 2014 and 2025. Each line represents one brand,
            allowing a direct comparison of how individual brand pricing evolves over time relative to the market average of free stations.
            Using the legend on the right side of the plot, you can select specific brands to display, making it possible to compare individual brands directly
            with each other as well as with the average price of free stations.
           """
           ),
    dbc.Row([
        dbc.Col(dcc.Graph(id="brand-comparison-graph"), width=11)
    ], justify="center"),
    html.Br(),

    html.P("""
            The plot shows that pricing differences between individual brands exist but generally follow the same overall market trend.
            ARAL appears to be consistently the most expensive brand across the observed years, while some other brands occasionally price closer to or even slightly 
            below the average level of free gas stations. Despite these differences, all brands react similarly to broader market developments, such as the sharp price increase around 2022.
            The next visualization examines the magnitude of these price differences in more detail.
            """
    ),
    html.Br(),

    dbc.Row([
        dbc.Col(dcc.Graph(id="avg-premium-graph"), width=11)
    ], justify="center"),

    html.Br(),

    html.P("""
            The bar chart shows the average price difference between individual brand gas stations and the average price of free stations. Positive values indicate that a brand is more expensive
            than the average free station (line at 0), while negative values indicate that a brand is cheaper. The results show that most large brands charge slightly higher prices than free stations. ARAL exhibits the largest difference,
            with prices on average about 3 cents per liter higher than the free station average. Other major brands such as OMV, Shell, AGIP, and Esso also tend to price above the market average, although the differences are smaller.
            In contrast, several smaller brands, including OIL!, Star, and HEM, appear to offer slightly lower prices than the average free station. Overall, the price differences remain relatively small, suggesting that while branded stations
            tend to be marginally more expensive, the overall market pricing across brands remains fairly competitive.
            """
    ), 
], fluid=True)
