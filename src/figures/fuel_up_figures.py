from __future__ import annotations

from pathlib import Path
from typing import Any

import polars as pl
import plotly.graph_objects as go
from dash import html

FUEL_UP_DATA_FILE = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "fuel_up_dashboard"
    / "station_price_observations_web_north_2026_02.parquet"
)

FUEL_UP_REQUIRED_COLUMNS = [
    "hour",
    "weekday",
    "fuel_type",
    "diff_to_min",
    "is_daily_min",
    "city_lc",
    "brand_lc",
    "post_code_str",
]

WEEKDAY_LABELS = ["Mon.", "Tue.", "Wed.", "Thu.", "Fri.", "Sat.", "Sun."]


def fuel_up_data_path() -> Path:
    return FUEL_UP_DATA_FILE


def load_fuel_up_lazy() -> pl.LazyFrame:
    data_path = fuel_up_data_path()
    if not data_path.exists():
        raise FileNotFoundError(
            f"Fuel-up data file not found: {data_path}. "
            "Expected path: data/fuel_up_dashboard/station_price_observations_web_north_2026_02.parquet"
        )

    lf = pl.scan_parquet(data_path)
    schema_names = set(lf.collect_schema().names())
    missing = [col for col in FUEL_UP_REQUIRED_COLUMNS if col not in schema_names]
    if missing:
        raise ValueError(
            "Missing expected columns in fuel-up parquet file: "
            + ", ".join(missing)
        )

    return lf.select(FUEL_UP_REQUIRED_COLUMNS)


def apply_fuel_up_filters_lazy(
    lf: pl.LazyFrame,
    fuel_type: str,
    city: str | None = None,
    brand: str | None = None,
    plz_prefix: str | None = None,
) -> pl.LazyFrame:
    selected_fuel = (fuel_type or "diesel").strip().lower()
    out = lf.filter(pl.col("fuel_type") == selected_fuel)

    city_norm = (city or "").strip().lower()
    brand_norm = (brand or "").strip().lower()
    plz_norm = (plz_prefix or "").strip()

    if city_norm:
        out = out.filter(
            pl.col("city_lc").fill_null("").str.contains(city_norm, literal=True)
        )
    if brand_norm:
        out = out.filter(
            pl.col("brand_lc").fill_null("").str.contains(brand_norm, literal=True)
        )
    if plz_norm:
        out = out.filter(
            pl.col("post_code_str").fill_null("").str.starts_with(plz_norm)
        )

    return out


def compute_fuel_up_meta(filtered_lf: pl.LazyFrame) -> dict[str, Any]:
    n_obs_df = filtered_lf.select(pl.len().alias("n_obs")).collect()
    n_obs = int(n_obs_df["n_obs"][0]) if len(n_obs_df) else 0
    return {"time_period": "2026-02", "n_obs": n_obs}


def compute_fuel_up_hour_stats(filtered_lf: pl.LazyFrame) -> pl.DataFrame:
    return (
        filtered_lf.filter(pl.col("hour").is_between(0, 23, closed="both"))
        .group_by("hour")
        .agg(
            pl.col("diff_to_min").mean().alias("mean_diff"),
            pl.col("is_daily_min").cast(pl.Float64).mean().alias("prob_min"),
        )
        .sort("hour")
        .collect()
    )


def compute_fuel_up_heatmap_stats(filtered_lf: pl.LazyFrame) -> pl.DataFrame:
    return (
        filtered_lf.filter(pl.col("hour").is_between(0, 23, closed="both"))
        .group_by(["weekday", "hour"])
        .agg(pl.col("diff_to_min").mean().alias("mean_diff"))
        .sort(["weekday", "hour"])
        .collect()
    )


def _safe_mean(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def _format_hour(hour: int) -> str:
    return f"{hour:02d}:00"


def _weekday_to_index(weekday_value: Any, one_based_ints: bool | None = None) -> int | None:
    if weekday_value is None:
        return None

    if isinstance(weekday_value, int):
        if one_based_ints is True and 1 <= weekday_value <= 7:
            return weekday_value - 1
        if one_based_ints is False and 0 <= weekday_value <= 6:
            return weekday_value
        if one_based_ints is None:
            if 0 <= weekday_value <= 6:
                return weekday_value
            if 1 <= weekday_value <= 7:
                return weekday_value - 1
        return None

    weekday_text = str(weekday_value).strip().lower()
    if weekday_text.isdigit():
        return _weekday_to_index(int(weekday_text), one_based_ints=one_based_ints)

    mapping = {
        "mon": 0,
        "monday": 0,
        "tue": 1,
        "tuesday": 1,
        "wed": 2,
        "wednesday": 2,
        "thu": 3,
        "thursday": 3,
        "fri": 4,
        "friday": 4,
        "sat": 5,
        "saturday": 5,
        "sun": 6,
        "sunday": 6,
    }
    return mapping.get(weekday_text)


def build_fuel_up_summary(
    meta: dict[str, Any],
    hour_stats: pl.DataFrame,
    fuel_type: str,
    city: str | None = None,
    brand: str | None = None,
    plz_prefix: str | None = None,
) -> html.Div:
    n_obs = int(meta.get("n_obs", 0))
    time_period = str(meta.get("time_period", "2026-02"))
    selected_fuel = (fuel_type or "diesel").strip().lower()
    clean_hour_stats = hour_stats.drop_nulls(["hour", "mean_diff", "prob_min"])

    if n_obs == 0 or clean_hour_stats.is_empty():
        return html.Div("No data after applying filters.")

    city_norm = (city or "").strip()
    brand_norm = (brand or "").strip()
    plz_norm = (plz_prefix or "").strip()

    optional_filters: list[str] = []
    if city_norm:
        optional_filters.append(f"City contains '{city_norm}'")
    if brand_norm:
        optional_filters.append(f"Brand contains '{brand_norm}'")
    if plz_norm:
        optional_filters.append(f"PLZ prefix '{plz_norm}'")

    filters_text = f"fuel_type={selected_fuel}"
    if optional_filters:
        filters_text = f"{filters_text}; " + "; ".join(optional_filters)

    mean_by_hour = {
        int(row["hour"]): float(row["mean_diff"])
        for row in clean_hour_stats.select(["hour", "mean_diff"]).iter_rows(named=True)
    }

    evening_hours = [18, 19, 20, 21]
    morning_hours = [6, 7, 8, 9]
    evening_vals = [mean_by_hour[h] for h in evening_hours if h in mean_by_hour]
    morning_vals = [mean_by_hour[h] for h in morning_hours if h in mean_by_hour]

    evening_mean = _safe_mean(evening_vals)
    morning_mean = _safe_mean(morning_vals)

    best_hour_row = clean_hour_stats.sort("mean_diff").row(0, named=True)
    best_hour = int(best_hour_row["hour"])
    best_hour_mean_ct = float(best_hour_row["mean_diff"]) * 100.0
    best_hour_prob_pct = float(best_hour_row["prob_min"]) * 100.0

    best_window: dict[str, Any] | None = None
    for width in (2, 3, 4):
        for start_hour in range(0, 24 - width + 1):
            window_hours = list(range(start_hour, start_hour + width))
            if any(h not in mean_by_hour for h in window_hours):
                continue

            window_mean = _safe_mean([mean_by_hour[h] for h in window_hours])
            if window_mean is None:
                continue

            if best_window is None or window_mean < best_window["mean_diff"]:
                best_window = {
                    "start_hour": start_hour,
                    "end_hour": start_hour + width - 1,
                    "width": width,
                    "mean_diff": window_mean,
                }

    if evening_mean is not None:
        evening_ct = evening_mean * 100.0
        evening_text = (
            f"Average price between 18-21h is {evening_ct:.2f} ct/L above the daily minimum."
        )
    else:
        evening_ct = None
        evening_text = "Average price between 18-21h could not be computed."

    if morning_mean is not None:
        morning_ct = morning_mean * 100.0
        morning_text = f"Between 6-9h it is {morning_ct:.2f} ct/L."
    else:
        morning_ct = None
        morning_text = "The 6-9h value could not be computed."

    if evening_ct is not None and morning_ct is not None:
        savings_ct = morning_ct - evening_ct
        if savings_ct >= 0:
            compare_text = (
                f"Evening refueling is therefore on average {savings_ct:.2f} ct/L cheaper."
            )
        else:
            compare_text = (
                "Evening refueling is therefore on average "
                f"{abs(savings_ct):.2f} ct/L more expensive."
            )
    else:
        compare_text = "Evening vs. morning comparison could not be computed."

    if best_window is None:
        best_window_text = "Best contiguous window could not be computed."
    else:
        best_window_text = (
            "Best contiguous window: "
            f"{_format_hour(best_window['start_hour'])}-"
            f"{best_window['end_hour']:02d}:59 "
            f"(width={best_window['width']}h), "
            f"{best_window['mean_diff'] * 100.0:.2f} ct/L above daily minimum on average."
        )

    return html.Div(
        [
            html.P(f"Time period: {time_period}"),
            html.P(f"Filters: {filters_text}"),
            html.P(f"Observations: {n_obs:,}"),
            html.P(evening_text),
            html.P(morning_text),
            html.P(compare_text),
            html.P(
                "Best single hour: "
                f"{_format_hour(best_hour)}, "
                f"{best_hour_mean_ct:.2f} ct/L above daily minimum on average, "
                f"{best_hour_prob_pct:.1f}% probability of exact daily minimum."
            ),
            html.P(best_window_text),
        ]
    )


def make_empty_fuel_up_figure(message: str) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        font={"size": 16},
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    fig.update_layout(
        title=message,
        template="plotly_white",
        margin={"l": 40, "r": 20, "t": 60, "b": 40},
    )
    return fig


def make_fuel_up_hour_plot(hour_stats: pl.DataFrame) -> go.Figure:
    plot_stats = hour_stats.drop_nulls(["hour", "mean_diff"])
    if plot_stats.is_empty():
        return make_empty_fuel_up_figure("No data after applying filters.")

    hours = plot_stats["hour"].to_list()
    mean_diff_ct = [(float(v) * 100.0) for v in plot_stats["mean_diff"].to_list()]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=hours,
            y=mean_diff_ct,
            mode="lines+markers",
            line={"width": 2, "color": "#4C78A8"},
            marker={"size": 6},
            hovertemplate="Hour %{x}:00<br>%{y:.2f} ct/L above daily min<extra></extra>",
            name="Mean diff",
        )
    )
    fig.update_layout(
        title="Average distance to daily minimum by hour",
        template="plotly_white",
        xaxis_title="Hour of day",
        yaxis_title="ct/L above daily minimum",
        margin={"l": 50, "r": 20, "t": 60, "b": 50},
    )
    fig.update_xaxes(dtick=1)
    return fig


def make_fuel_up_heatmap(heatmap_stats: pl.DataFrame) -> go.Figure:
    if heatmap_stats.is_empty():
        return make_empty_fuel_up_figure("No data after applying filters.")

    int_weekdays = [
        int(row["weekday"])
        for row in heatmap_stats.select(["weekday"]).iter_rows(named=True)
        if isinstance(row["weekday"], int)
    ]
    one_based_ints: bool | None = None
    if int_weekdays:
        if 0 in int_weekdays:
            one_based_ints = False
        elif 7 in int_weekdays:
            one_based_ints = True

    z_values: list[list[float | None]] = [[None for _ in range(24)] for _ in range(7)]
    for row in heatmap_stats.iter_rows(named=True):
        weekday_idx = _weekday_to_index(row["weekday"], one_based_ints=one_based_ints)
        hour = row["hour"]
        mean_diff = row["mean_diff"]
        if weekday_idx is None or hour is None or mean_diff is None:
            continue
        hour_int = int(hour)
        if not (0 <= hour_int <= 23):
            continue
        z_values[weekday_idx][hour_int] = float(mean_diff) * 100.0

    fig = go.Figure(
        data=[
            go.Heatmap(
                z=z_values,
                x=list(range(24)),
                y=WEEKDAY_LABELS,
                colorscale="YlOrRd",
                colorbar={"title": "ct/L"},
                hovertemplate=(
                    "Weekday: %{y}<br>"
                    "Hour: %{x}:00<br>"
                    "Mean diff: %{z:.2f} ct/L<extra></extra>"
                ),
            )
        ]
    )
    fig.update_layout(
        title="Weekday \u00d7 Hour",
        template="plotly_white",
        xaxis_title="Hour of day",
        yaxis_title="Weekday",
        margin={"l": 60, "r": 20, "t": 60, "b": 50},
    )
    fig.update_xaxes(dtick=1)
    return fig
