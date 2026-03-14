from pathlib import Path
from typing import Literal
import pandas as pd
import plotly.express as px

# Data root:
PROJECT_ROOT = Path(__file__).resolve().parents[1]

DEFAULT_DERIVED_DIR = PROJECT_ROOT / "data" / "national_daily_last"
StatType = Literal["mean", "median"]


def plot_national_fuel_prices_year(year: int, stat: StatType = "mean"):
    if stat not in ("mean", "median"):
        raise ValueError("stat must be 'mean' or 'median'")

    file_path = DEFAULT_DERIVED_DIR / f"national_daily_last_{year}.csv"
    df = pd.read_csv(file_path)

    df["day"] = pd.to_datetime(df["day"])
    df = df.sort_values("day")

    fuels = ["e5", "e10", "diesel"]
    value_cols = [f"{fuel}_{stat}_last" for fuel in fuels]

    df_long = df.melt(
        id_vars="day",
        value_vars=value_cols,
        var_name="fuel_type",
        value_name="price"
    )
    df_long["fuel_type"] = df_long["fuel_type"].str.replace(f"_{stat}_last", "", regex=False)

    fig = px.line(
        df_long,
        x="day",
        y="price",
        color="fuel_type",
        title=f"National fuel prices ({stat}) – {year}",
        labels={
            "day": "Day",
            "price": f"Price ({stat})",
            "fuel_type": "Fuel type"
        }
    )
    fig.update_layout(
        template="plotly_white",
        xaxis_title="Day",
        yaxis_title=f"Price ({stat})",
        legend_title="Fuel type"
    )

    return fig

