from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

_DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "brands_vs_free"

_df_bvf = pd.read_csv(_DATA_DIR / "brand_vs_free_yearly_stats.csv")
_df_per_brand = pd.read_csv(_DATA_DIR / "per_brand_yearly_stats.csv")

_brand = _df_bvf[_df_bvf["station_type"] == "brand_station"].reset_index(drop=True)
_free = _df_bvf[_df_bvf["station_type"] == "free_station"].reset_index(drop=True)

_FUEL_COLS = ["diesel_mean", "e5_mean", "e10_mean"]
_FUEL_LABEL_LIST = ["Diesel", "E5", "E10"]
_FUEL_LABELS = {"diesel_mean": "Diesel", "e5_mean": "E5", "e10_mean": "E10"}
_COLORS = ["steelblue", "darkorange", "seagreen"]


def plot_brand_vs_free_prices() -> go.Figure:
    """Plot yearly mean prices for brand and free stations by fuel."""
    fig = make_subplots(
        rows=1,
        cols=3,
        shared_yaxes=True,
        subplot_titles=_FUEL_LABEL_LIST,
    )

    for i in range(3):
        col = _FUEL_COLS[i]
        col_i = i + 1
        show_legend = i == 0

        fig.add_trace(
            go.Scatter(
                x=_brand["year"],
                y=_brand[col].round(4),
                mode="lines+markers",
                name="Brand station",
                line=dict(color="steelblue", width=2),
                legendgroup="brand",
                showlegend=show_legend,
                hovertemplate="%{x}: %{y:.3f} EUR/L",
            ),
            row=1,
            col=col_i,
        )

        fig.add_trace(
            go.Scatter(
                x=_free["year"],
                y=_free[col].round(4),
                mode="lines+markers",
                name="Free station",
                line=dict(color="darkorange", width=2, dash="dash"),
                legendgroup="free",
                showlegend=show_legend,
                hovertemplate="%{x}: %{y:.3f} EUR/L",
            ),
            row=1,
            col=col_i,
        )

    fig.update_yaxes(ticksuffix=" EUR", col=1)
    fig.update_layout(
        title="Mean Fuel Prices: Brand vs. Free Stations",
        height=450,
        hovermode="x unified",
        template="plotly_white",
    )
    return fig


def plot_price_difference() -> go.Figure:
    """Plot yearly brand-minus-free price differences in ct/L."""
    years = _brand["year"].tolist()

    fig = go.Figure()
    fig.add_hline(y=0, line_color="black", line_width=1)

    for i in range(3):
        col = _FUEL_COLS[i]
        label = _FUEL_LABEL_LIST[i]

        brand_vals = _brand[col].tolist()
        free_vals = _free[col].tolist()
        diff_ct = [(brand_vals[j] - free_vals[j]) * 100 for j in range(len(years))]

        fig.add_trace(
            go.Scatter(
                x=years,
                y=diff_ct,
                mode="lines+markers",
                name=label,
                line=dict(color=_COLORS[i], width=2),
                hovertemplate="%{x}: %{y:+.2f} ct/L",
            )
        )

    fig.update_layout(
        title="Price Difference: Brand - Free (positive = brand is more expensive)",
        xaxis_title="Year",
        yaxis_title="Difference (ct/L)",
        yaxis_ticksuffix=" ct",
        hovermode="x unified",
        template="plotly_white",
        height=450,
        width=900,
    )
    return fig


def plot_brand_comparison(
    fuel: str = "diesel_mean",
    brands: list[str] | None = None,
) -> go.Figure:
    """Compare selected brands with the free-station average line."""
    if brands is None:
        brands = _df_per_brand["brand_normalized"].unique().tolist()

    subset = _df_per_brand[
        _df_per_brand["brand_normalized"].isin(brands)
    ].sort_values("year")

    free_line = _df_bvf[_df_bvf["station_type"] == "free_station"][
        ["year", fuel]
    ].copy()
    free_line["brand_normalized"] = "Free Station (avg)"

    combined = pd.concat(
        [subset[["year", fuel, "brand_normalized"]], free_line],
        ignore_index=True,
    )

    fig = px.line(
        combined,
        x="year",
        y=fuel,
        color="brand_normalized",
        markers=True,
        title=f"{_FUEL_LABELS[fuel]}: Selected brands vs. free stations",
        labels={
            "year": "Year",
            fuel: "Mean price (EUR/L)",
            "brand_normalized": "Brand",
        },
    )
    default_visible = {"ARAL", "OIL!", "Free Station (avg)"}
    for trace in fig.data:
        if trace.name not in default_visible:
            trace.visible = "legendonly"

    fig.update_layout(
        yaxis_ticksuffix=" EUR",
        hovermode="x unified",
        template="plotly_white",
    )
    return fig


def plot_avg_premium_per_brand(fuel: str = "e10_mean") -> go.Figure:
    """Plot the average brand premium versus free stations by brand."""
    free_col = "free_" + fuel

    joined = _df_per_brand.merge(
        _free[["year", fuel]].rename(columns={fuel: free_col}),
        on="year",
    )
    joined["premium_ct"] = (joined[fuel] - joined[free_col]) * 100

    avg_premium = (
        joined.dropna(subset=["premium_ct"])
        .groupby("brand_normalized")["premium_ct"]
        .mean()
        .reset_index()
        .sort_values("premium_ct", ascending=False)
    )

    fig = px.bar(
        avg_premium,
        x="brand_normalized",
        y="premium_ct",
        title=f"{_FUEL_LABELS[fuel]}: Brand vs. Free Station Average",
        labels={
            "premium_ct": "Price difference vs. free stations (ct/L)",
            "brand_normalized": "Brand",
        },
    )
    fig.update_layout(
        height=500,
        yaxis=dict(rangemode="normal"),
        template="plotly_white",
    )
    fig.add_hline(y=0, line_color="black", line_width=1)
    return fig
