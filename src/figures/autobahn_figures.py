import re
from pathlib import Path
from typing import Literal

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import polars as pl

PROJECT_ROOT = Path(__file__).resolve().parents[2]
AUTOBAHN_DIR = PROJECT_ROOT / "data" / "autobahn"
BORDER_DIR = PROJECT_ROOT / "data" / "border_stations"
WEATHER_DIR = PROJECT_ROOT / "data" / "weather_influence"
StatType = Literal["mean", "median"]


def show_median_price_heatmap_per_region() -> go.Figure:
    """Plot monthly regional median diesel prices for 2025 on a map."""
    monthly_median_prices = AUTOBAHN_DIR / "rq3_regional_median_prices_for_map.parquet"
    display_df = pl.read_parquet(monthly_median_prices)

    min_price = display_df["diesel_median_price"].min()
    max_price = display_df["diesel_median_price"].max()

    fig = px.scatter_map(
        display_df,
        lat="avg_lat",
        lon="avg_lng",
        color="diesel_median_price",
        center={"lat": 51.16, "lon": 10.45},
        animation_frame="month",
        hover_name="region",
        labels={"diesel_median_price": "Price (EUR)", "month": "Month"},
        range_color=[min_price, max_price],
        color_continuous_scale="RdYlBu_r",
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=40, b=10),
        map=dict(
            style="open-street-map",
            center=dict(lat=51.1657, lon=10.4515),
            zoom=2,
            bounds=dict(west=4.5, east=16.5, south=47.0, north=55.2),
        ),
        height=800,
        autosize=True,
    )
    fig.update_traces(marker=dict(size=15, opacity=1))
    return fig


def plot_border_stations() -> go.Figure:
    """Plot border and surrounding stations on a Germany map."""
    border_stations_file = BORDER_DIR / "lower_border_stations.csv"
    border_stations = pd.read_csv(border_stations_file)

    fig = px.scatter_map(
        border_stations,
        lat="latitude",
        lon="longitude",
        color="border_region",
        hover_name="neighbour_country",
        hover_data="neighbour_country",
        center={"lat": 51.16, "lon": 10.45},
        zoom=2,
        map_style="open-street-map",
        title="Border and surrounding stations in Germany",
    )
    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        map=dict(
            style="open-street-map",
            center=dict(lat=51.1657, lon=10.4515),
            zoom=2,
            bounds=dict(west=4.5, east=16.5, south=47.0, north=55.2),
        ),
        height=800,
        autosize=True,
    )
    fig.update_traces(marker=dict(size=15, opacity=1))
    return fig


def show_border_price_difference(country: str) -> go.Figure | None:
    """Plot yearly boxplots of border vs. surrounding diesel prices."""
    price_diff_path = BORDER_DIR / "rq3_median_border_distributions.parquet"
    yearly_df = pl.read_parquet(price_diff_path)

    plot_df = pd.DataFrame(
        yearly_df.filter(pl.col("neighbour_country") == country)
        .select(["border_region", "diesel_median_price", "year"])
        .to_dicts()
    )
    plot_df["year"] = pd.to_datetime(
        plot_df["year"].astype(int).astype(str),
        format="%Y",
    )

    if plot_df.empty:
        print(f"No data found for {country}.")
        return None

    fig = go.Figure()
    for label, color in [
        ("Border (0-8km)", "lightblue"),
        ("Surrounding (8-25km)", "violet"),
    ]:
        subset = plot_df[plot_df["border_region"] == label]
        fig.add_trace(
            go.Box(
                x=subset["year"],
                y=subset["diesel_median_price"],
                name=label,
                marker_color=color,
            )
        )

    fig.update_layout(
        title=(
            "Yearly distribution of median diesel prices: "
            f"border vs. surrounding-region stations ({country})"
        ),
        xaxis_title="Year",
        yaxis_title="Median price (EUR/liter)",
        boxmode="group",
    )
    fig.update_xaxes(tickformat="%Y", dtick="M12")
    return fig


def plot_yearly_autobahn_premium_line(
    fuel_type: str,
    statistic: StatType = "mean",
) -> go.Figure:
    """Plot yearly autobahn premium with confidence interval for one fuel."""
    summary_path = AUTOBAHN_DIR / "rq3_panel_summary.csv"
    yearly_df = pd.read_csv(summary_path)

    yearly_df = yearly_df[
        (yearly_df["statistic"] == statistic) & (yearly_df["fuel_type"] == fuel_type)
    ].copy()
    yearly_df["year"] = pd.to_datetime(
        yearly_df["year"].astype(int).astype(str),
        format="%Y",
    )

    fill_color_map = {
        "diesel": "rgba(0,176,246,0.2)",
        "e5": "rgba(0,100,80,0.2)",
        "e10": "rgba(231,107,243,0.2)",
    }
    line_color_map = {
        "diesel": "rgba(255,255,255,0)",
        "e5": "rgba(255,255,255,0)",
        "e10": "rgba(255,255,255,0)",
    }
    color_map = {
        "diesel": "rgb(0,176,246)",
        "e5": "rgb(0,100,80)",
        "e10": "rgb(231,107,243)",
    }

    df_sub = yearly_df.sort_values("year")
    x_vals = df_sub["year"].to_list()
    x_rev = x_vals[::-1]
    y_upper = df_sub["ci_high"].to_list()
    y_lower = df_sub["ci_low"].to_list()[::-1]
    y_line = df_sub["autobahn_coef"].to_list()

    custom_data = list(
        zip(
            df_sub["year"].dt.year,
            df_sub["autobahn_coef"],
            df_sub["ci_high"],
            df_sub["ci_low"],
        )
    )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x_vals + x_rev,
            y=y_upper + y_lower,
            fill="toself",
            fillcolor=fill_color_map[fuel_type],
            line_color=line_color_map[fuel_type],
            name=fuel_type,
            showlegend=False,
            hoverinfo="skip",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=x_vals,
            y=y_line,
            mode="lines+markers",
            line_color=color_map[fuel_type],
            showlegend=False,
            name=fuel_type,
            customdata=custom_data,
            hovertemplate=(
                "Year: %{customdata[0]}<br>"
                "Autobahn premium: %{customdata[1]:.3f} EUR/liter<br>"
                "Upper confidence bound: %{customdata[2]:.3f} EUR/liter<br>"
                "Lower confidence bound: %{customdata[3]:.3f} EUR/liter<br>"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Estimated autobahn premium (EUR/liter)",
        template="plotly_white",
        title=(
            f"{fuel_type} autobahn premium with 95% confidence interval over the years"
        ),
        height=400,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    fig.update_xaxes(tickformat="%Y", dtick="M12")
    return fig


def plot_autobahn_premium_barchart(statistic: StatType = "mean") -> go.Figure:
    """Plot yearly autobahn premium bars for diesel, E5, and E10."""
    summary_path = AUTOBAHN_DIR / "rq3_panel_summary.csv"
    yearly_df = pd.read_csv(summary_path)

    yearly_df = yearly_df[yearly_df["statistic"] == statistic].copy()
    yearly_df["year"] = pd.to_datetime(
        yearly_df["year"].astype(int).astype(str),
        format="%Y",
    )

    color_map = {
        "diesel": "rgb(0,176,246)",
        "e5": "rgb(0,100,80)",
        "e10": "rgb(231,107,243)",
    }

    y_diesel = yearly_df[yearly_df["fuel_type"] == "diesel"]
    y_e5 = yearly_df[yearly_df["fuel_type"] == "e5"]
    y_e10 = yearly_df[yearly_df["fuel_type"] == "e10"]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=yearly_df["year"].dt.year,
            y=y_diesel["autobahn_coef"],
            name="diesel",
            marker_color=color_map["diesel"],
            hovertemplate=(
                "Year: %{x}<br>"
                "Fuel: diesel<br>"
                "Autobahn premium: %{y:.3f} EUR/liter<br>"
                "<extra></extra>"
            ),
        )
    )
    fig.add_trace(
        go.Bar(
            x=yearly_df["year"].dt.year,
            y=y_e5["autobahn_coef"],
            name="e5",
            marker_color=color_map["e5"],
            hovertemplate=(
                "Year: %{x}<br>"
                "Fuel: e5<br>"
                "Autobahn premium: %{y:.3f} EUR/liter<br>"
                "<extra></extra>"
            ),
        )
    )
    fig.add_trace(
        go.Bar(
            x=yearly_df["year"].dt.year,
            y=y_e10["autobahn_coef"],
            name="e10",
            marker_color=color_map["e10"],
            hovertemplate=(
                "Year: %{x}<br>"
                "Fuel: e10<br>"
                "Autobahn premium: %{y:.3f} EUR/liter<br>"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        title=dict(text="Development of the autobahn premium from 2014-2026"),
        xaxis_tickfont_size=14,
        yaxis=dict(
            title=dict(text="Autobahn premium (EUR/liter)", font=dict(size=16)),
        ),
        legend=dict(
            x=0,
            y=1.0,
            bgcolor="rgba(255, 255, 255, 0)",
            bordercolor="rgba(255, 255, 255, 0)",
        ),
        template="plotly_white",
        barmode="group",
        bargap=0.15,
        bargroupgap=0.1,
    )
    return fig


def plot_wilcoxon_results_loolipop() -> go.Figure:
    """Plot yearly median volatility differences as a lollipop chart."""
    wilcoxon_df = load_wilcoxon_results()
    wilcoxon_df["year"] = pd.to_datetime(
        wilcoxon_df["year"].astype(int).astype(str),
        format="%Y",
    )

    x_stems = []
    y_stems = []
    for _, row in wilcoxon_df.iterrows():
        x_stems.extend([row["year"], row["year"], None])
        y_stems.extend([0, row["median_difference"], None])

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x_stems,
            y=y_stems,
            mode="lines",
            line=dict(width=2),
            showlegend=False,
            hoverinfo="skip",
        )
    )

    custom_data = list(
        zip(wilcoxon_df["year"].dt.year, wilcoxon_df["median_difference"])
    )
    fig.add_trace(
        go.Scatter(
            x=wilcoxon_df["year"],
            y=wilcoxon_df["median_difference"],
            mode="markers",
            marker=dict(size=12),
            name="Median volatility difference",
            customdata=custom_data,
            hovertemplate=(
                "Year: %{customdata[0]}<br>"
                "Median volatility difference: %{customdata[1]:.4f} EUR/liter<br>"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        title="Autobahn vs non-autobahn stations median volatility difference",
        xaxis_title="Year",
        yaxis_title="Median difference (EUR/liter)",
        template="plotly_white",
    )
    fig.update_xaxes(tickformat="%Y", dtick="M12")
    return fig


def display_weather_codes_per_region(year: int) -> go.Figure:
    """Plot hourly weather codes for region 24 for a selected year."""
    file_path = WEATHER_DIR / "weather_region24.csv"
    weather_codes = WEATHER_DIR / "weather_codes_descriptions.csv"

    df = pd.read_csv(file_path).drop(columns=["precipitation", "temperature_2m"])
    code_df = pd.read_csv(weather_codes)

    df["date"] = pd.to_datetime(df["date"])
    df["year"] = pd.to_datetime(df["date"]).dt.year
    df_plot = df[df["year"] == year]

    # Merge code descriptions to improve hover details.
    df_plot = df_plot.merge(code_df, on="weather_code", how="left")
    df_plot = df_plot.sort_values("weather_code", ascending=True)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df_plot["date"],
            y=df_plot["weather_code"],
            mode="markers",
            marker=dict(
                size=5,
                color=df_plot["weather_code"],
                colorscale="Turbo",
                opacity=0.6,
            ),
            customdata=df_plot[["description"]],
            name="",
            hovertemplate=(
                "Date: %{x|%Y-%m-%d %H:%M}<br>"
                "Weather code: %{y}<br>"
                "Description: %{customdata[0]}"
                "<extra></extra>"
            ),
        )
    )
    fig.update_layout(
        title_text=f"Weather codes for region 24 (Kiel and surrounding) in {year}",
        xaxis_title="Date",
        yaxis_title="Weather code",
        plot_bgcolor="white",
        hovermode="closest",
    )
    fig.update_yaxes(type="category", showgrid=True, gridcolor="lightgrey")
    fig.update_xaxes(showgrid=True, gridcolor="lightgrey")
    return fig


def load_autobahn_results() -> pd.DataFrame:
    """Load panel regression summary results for autobahn premium."""
    return pd.read_csv(AUTOBAHN_DIR / "rq3_panel_summary.csv")


def load_wilcoxon_results() -> pd.DataFrame:
    """Load Wilcoxon signed-rank test results for volatility differences."""
    wilcoxon_result_path = AUTOBAHN_DIR / "rq3_wilcoxon.csv"
    return pd.read_csv(wilcoxon_result_path)


def load_overall_border_mann_whitney_results() -> pd.DataFrame:
    """Load overall Mann-Whitney U test results for border stations."""
    test_result_path = BORDER_DIR / "rq3_overall_non_autobahn_border_test_result.csv"
    return pd.read_csv(test_result_path)


def load_yearly_border_mann_whitney_results() -> pd.DataFrame:
    """Load yearly Mann-Whitney U test results for border stations."""
    test_result_path = BORDER_DIR / "rq3_non_autobahn_yearly_border_test_result.csv"
    return pd.read_csv(test_result_path)


def get_country_options() -> list[dict[str, str]]:
    """Build dropdown options for countries in border test results."""
    df = load_overall_border_mann_whitney_results()
    countries = sorted(df["Country"].dropna().unique().tolist())
    return [{"label": country, "value": country} for country in countries]


def load_border_brand_structure() -> pd.DataFrame:
    """Load brand distribution for border-region stations."""
    filepath = BORDER_DIR / "rq3_border_brand_distribution.csv"
    return pd.read_csv(filepath)


def load_extreme_weather_regression() -> dict[str, float | int]:
    """Parse regression metrics for the extreme weather model."""
    result_path = WEATHER_DIR / "rq9_regression_result.txt"
    text = result_path.read_text(encoding="utf-8")

    r2_match = re.search(r"R-squared:\s+([0-9.]+)", text)
    obs_match = re.search(r"No\. Observations:\s+([0-9]+)", text)
    param_match = re.search(
        (
            r"extreme_weather\s+([-\deE.]+)\s+([-\deE.]+)\s+([-\deE.]+)\s+"
            r"([-\deE.]+)\s+([-\deE.]+)\s+([-\deE.]+)"
        ),
        text,
    )

    if not (r2_match and obs_match and param_match):
        raise ValueError("Could not parse regression summary file.")

    coefficient = float(param_match.group(1))
    std_err = float(param_match.group(2))
    t_stat = float(param_match.group(3))
    p_value = float(param_match.group(4))
    lower_ci = float(param_match.group(5))
    upper_ci = float(param_match.group(6))

    return {
        "coefficient": coefficient,
        "std_err": std_err,
        "t_stat": t_stat,
        "p_value": p_value,
        "lower_ci": lower_ci,
        "upper_ci": upper_ci,
        "observations": int(obs_match.group(1)),
        "r_squared": float(r2_match.group(1)),
    }
