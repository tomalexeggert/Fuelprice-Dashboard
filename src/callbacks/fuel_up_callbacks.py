from dash import Input, Output

from src.figures.fuel_up_figures import (
    apply_fuel_up_filters_lazy,
    build_fuel_up_summary,
    compute_fuel_up_heatmap_stats,
    compute_fuel_up_hour_stats,
    compute_fuel_up_meta,
    load_fuel_up_lazy,
    make_empty_fuel_up_figure,
    make_fuel_up_heatmap,
    make_fuel_up_hour_plot,
)


def register_fuel_up_callbacks(app):
    @app.callback(
        Output("fuel-up-hour-graph", "figure"),
        Output("fuel-up-heatmap-graph", "figure"),
        Output("fuel-up-summary", "children"),
        Input("fuel-up-fuel-dropdown", "value"),
        Input("fuel-up-city-input", "value"),
        Input("fuel-up-brand-input", "value"),
        Input("fuel-up-plz-input", "value"),
    )
    def update_fuel_up_dashboard(fuel_type, city, brand, plz_prefix):
        try:
            lf = load_fuel_up_lazy()
            filtered_lf = apply_fuel_up_filters_lazy(
                lf=lf,
                fuel_type=fuel_type or "diesel",
                city=city,
                brand=brand,
                plz_prefix=plz_prefix,
            )

            meta = compute_fuel_up_meta(filtered_lf)
            if meta["n_obs"] == 0:
                empty = make_empty_fuel_up_figure("No data after applying filters.")
                return empty, empty, "No data after applying filters."

            hour_stats = compute_fuel_up_hour_stats(filtered_lf)
            heatmap_stats = compute_fuel_up_heatmap_stats(filtered_lf)

            if hour_stats.is_empty() or heatmap_stats.is_empty():
                empty = make_empty_fuel_up_figure("No data after applying filters.")
                return empty, empty, "No data after applying filters."

            hour_fig = make_fuel_up_hour_plot(hour_stats)
            heatmap_fig = make_fuel_up_heatmap(heatmap_stats)
            summary = build_fuel_up_summary(
                meta=meta,
                hour_stats=hour_stats,
                fuel_type=fuel_type or "diesel",
                city=city,
                brand=brand,
                plz_prefix=plz_prefix,
            )
            return hour_fig, heatmap_fig, summary

        except Exception as exc:
            message = f"Error loading fuel-up data: {exc}"
            empty = make_empty_fuel_up_figure(message)
            return empty, empty, message
