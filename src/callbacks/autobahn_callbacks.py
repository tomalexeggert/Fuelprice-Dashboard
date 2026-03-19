from dash import Input, Output, ctx, State, callback_context, no_update
import pandas as pd
import polars as pl
from pathlib import Path
from src.figures.autobahn_figures import (show_border_price_difference, show_median_price_heatmap_per_region, plot_autobahn_premium_barchart,
                                          plot_border_stations, plot_wilcoxon_results_loolipop, plot_yearly_autobahn_premium_line,load_autobahn_results,
                                          load_wilcoxon_results, load_overall_border_mann_whitney_results, load_yearly_border_mann_whitney_results, load_border_brand_structure,
                                          display_weather_codes_per_region, load_extreme_weather_regression)
from src.figures.competition_figures import plot_clusters, plot_motorway_cluster_pies, plot_price_difference_line, plot_price_difference_boxplot

PROJECT_ROOT = Path(__file__).resolve().parents[2]

def register_autobahn_callbacks(app):
    @app.callback(
        Output("autobahn-mean-coef", "children"),
        Output("autobahn-mean-ci", "children"),
        Output("autobahn-significance", "children"),
        Output("autobahn-mean-trend", "figure"),
        Input("premium-btn-diesel", "n_clicks"),
        Input("premium-btn-e5", "n_clicks"),
        Input("premium-btn-e10", "n_clicks"),
    )
    def update_autobahn_mean_results(diesel, e5, e10):        
        results_df = load_autobahn_results()

        button_id = ctx.triggered_id

        if button_id == "premium-btn-diesel":
            selected_fuel = "diesel"
        elif button_id == "premium-btn-e5":
            selected_fuel = "e5"
        else:
            selected_fuel = "e10"

        #filter for selected fuel type and mean statistic.
        dff = results_df[
            (results_df["fuel_type"] == selected_fuel) &
            (results_df["statistic"] == "mean")
        ].copy()

        #calculate summary values for the cards.
        mean_coef = dff["autobahn_coef"].mean()
        mean_ci_low = dff["ci_low"].mean()
        mean_ci_high = dff["ci_high"].mean()

        #calculate significance over the available years.
        significant_years = (dff["p_value"] < 0.05).sum()
        total_years = dff["p_value"].notna().sum()


        #create yearly autobahn premium plot.
        fig = plot_yearly_autobahn_premium_line(
            fuel_type=selected_fuel,
            statistic="mean"
        )

        return (
            f"{mean_coef:.3f} €/liter",
            f"[{mean_ci_low:.3f}, {mean_ci_high:.3f}]",
            f"{significant_years}/{total_years}",
            fig
        )
    
    @app.callback(
        Output("premium-btn-diesel", "color"),
        Output("premium-btn-e5", "color"),
        Output("premium-btn-e10", "color"),
        Input("premium-btn-diesel", "n_clicks"),
        Input("premium-btn-e5", "n_clicks"),
        Input("premium-btn-e10", "n_clicks"),
    )

    def highlight_active_button_autobahn(n_diesel, n_e5, n_e10):
        ctx = callback_context

        if not ctx.triggered:
            active = "e10"
        else:
            button_id = ctx.triggered[0]["prop_id"].split(".")[0]
            active = button_id.replace("premium-btn-", "")
        return (
            "info" if active == "diesel" else "primary",
            "info" if active == "e5" else "primary",
            "info" if active == "e10" else "primary",
            )
    
    @app.callback(
        Output("wilcoxon-median-effect", "children"),
        Output("wilcoxon-p-value", "children"),
        Output("wilcoxon-significance", "children"),
        Output("wilcoxon-direction", "children"),
        Output("wilcoxon-lollipop-plot", "figure"),
        Input("dummy-trigger", "children")
    )
    def update_wilcoxon_results(_):
        wilcoxon_df = load_wilcoxon_results()

        median_effect = wilcoxon_df["median_difference"].median()
        median_p_value = float(wilcoxon_df["p_value"].median())
        significant_years = int((wilcoxon_df["p_value"] < 0.05).sum())
        positive_years = int((wilcoxon_df["median_difference"] > 0).sum())
        total_years = int(wilcoxon_df["year"].nunique())

        fig = plot_wilcoxon_results_loolipop()

        return (
            f"{median_effect:.4f} €/liter",
            f"{median_p_value:.4g}",
            f"{significant_years}/{total_years}",
            f"{positive_years}/{total_years}",
            fig
        )
    
    @app.callback(
        Output("overall-median-diff", "children"),
        Output("overall-significance", "children"),
        Output("overall-direction", "children"),
        Output("overall-brand-share", "children"),
        Input("dummy-trigger", "children")
    )
    def update_overall_results(_):
        overall_df = load_overall_border_mann_whitney_results()   
        brand_df = load_border_brand_structure()

        median_diff = overall_df["Price_difference"].median()
        significant_countries = int((overall_df["p_value"] < 0.05).sum())
        positive_countries = int((overall_df["Price_difference"] > 0).sum())
        total_countries = int(overall_df["Country"].nunique())

        border_brand = brand_df.loc[brand_df["border_region"] == "Border (0-8km)", "brand" ].iloc[0]
        surrounding_brand = brand_df.loc[brand_df["border_region"] == "Surrounding (8-25km)", "brand"].iloc[0]



        return (
            f"{median_diff:.3f} €/liter",
            f"{significant_countries}/{total_countries}",
            f"{positive_countries}/{total_countries}",
            f"{border_brand:.2f}% / {surrounding_brand:.2f}%"
        )
    
    @app.callback(
        Output("border-price-difference-plot", "figure"),
        Output("country-price-diff", "children"),
        Output("country-p-value", "children"),
        Output("country-significant", "children"),
        Output("country-stations", "children"),
        Input("border-country-dropdown", "value"),
    )
    def update_country_border_view(country):
        fig = show_border_price_difference(country)

        results_df = load_yearly_border_mann_whitney_results()
        row = results_df[results_df["Country"] == country]

        if row.empty:
            return fig, "-", "-", "-", "-"

        row = row.iloc[0]

        significant = row["Significant (5%)"]
        if isinstance(significant, str):
            significant = significant.strip().lower() == "true"

        return (
            fig,
            f"{row['Price_difference']:.3f} €/liter",
            f"{row['p_value']:.4g}",
            "Yes" if significant else "No",
            f"{int(row['N_border'])} / {int(row['N_surrounding'])}",
        )
    
    @app.callback(
        Output("yearly-weather-codes-plot", "figure"),
        Input("weather-year-dropdown", "value")
    )
    def update_weather_codes_view(year):
        fig = display_weather_codes_per_region(year)

        return fig
    
    @app.callback(
        Output("weather-regression-headline", "children"),
        Output("weather-regression-headline", "color"),
        Output("weather-effect-estimate", "children"),
        Output("weather-p-value", "children"),
        Output("weather-confidence-interval", "children"),
        Output("weather-observations", "children"),
        Output("weather-r2", "children"),
        Input("dummy-trigger", "children")
    )
    def update_weather_regression_summary(_):
        result = load_extreme_weather_regression()

        coef = result["coefficient"]
        p_value = result["p_value"]
        lower_ci = result["lower_ci"]
        upper_ci = result["upper_ci"]
        observations = result["observations"]
        r_squared = result["r_squared"]

        headline = "We couldn't find any significanct effect of extreme weather events on the fuel prices."
        color = "Secondary"

        return (
            headline,
            color,
            f"{coef:.6f}",
            f"{p_value:.4f}",
            f"[{lower_ci:.6f}, {upper_ci:.6f}]",
            f"{observations:,}",
            f"{r_squared:.4f}",
        )
    
    @app.callback(
        Output("collapse-effect", "is_open"),
        Input("toggle-effect", "n_clicks"),
        State("collapse-effect", "is_open"),
    )
    def toggle_effect(n, is_open):
        if n:
            return not is_open
        return is_open


    @app.callback(
        Output("collapse-pvalue", "is_open"),
        Input("toggle-pvalue", "n_clicks"),
        State("collapse-pvalue", "is_open"),
    )
    def toggle_pvalue(n, is_open):
        if n:
            return not is_open
        return is_open


    @app.callback(
        Output("collapse-ci", "is_open"),
        Input("toggle-ci", "n_clicks"),
        State("collapse-ci", "is_open"),
    )
    def toggle_ci(n, is_open):
        if n:
            return not is_open
        return is_open


    @app.callback(
        Output("collapse-obs", "is_open"),
        Input("toggle-obs", "n_clicks"),
        State("collapse-obs", "is_open"),
    )
    def toggle_obs(n, is_open):
        if n:
            return not is_open
        return is_open


    @app.callback(
        Output("collapse-r2-weather", "is_open"),
        Input("toggle-r2-weather", "n_clicks"),
        State("collapse-r2-weather", "is_open"),
    )
    def toggle_r2_weather(n, is_open):
        if n:
            return not is_open
        return is_open
    
    # --- 1. Cluster Maps (Initiales Laden) ---
    @app.callback(
        Output("cluster_1_map", "figure"),
        Output("cluster_2_map", "figure"),
        Input("cluster_1_map", "id")
    )
    def load_cluster_maps(_):
        path_1 = PROJECT_ROOT / "data" / "competition" / "stations_clusters_1.csv"
        path_2 = PROJECT_ROOT / "data" / "competition" / "stations_clusters_2.csv"

        # Nur eine Definition! Direkt mit Polars laden.
        cluster_1_data = pl.read_csv(path_1)
        cluster_2_data = pl.read_csv(path_2)

        fig_cluster_1 = plot_clusters(cluster_1_data, cluster_1_data["cluster"])
        fig_cluster_2 = plot_clusters(cluster_2_data, cluster_2_data["cluster"])

        return fig_cluster_1, fig_cluster_2


    # --- 2. Autobahn Anteil (Pie Chart) ---
    @app.callback(
        Output("cluster_autobahn_share_pie", "figure"),
        Input("cluster_autobahn_share_pie", "id"),
    )
    def load_cluster_autobahn_share_pie(_):
        path_1 = PROJECT_ROOT / "data" / "competition" / "stations_clusters_1.csv"
        path_2 = PROJECT_ROOT / "data" / "competition" / "stations_clusters_2.csv"
        path_3 = PROJECT_ROOT / "data" / "competition" / "autobahn_stations.csv"

        cluster_data_1 = pl.read_csv(path_1)
        cluster_data_2 = pl.read_csv(path_2)
        autobahn_data = pl.read_csv(path_3)

        return plot_motorway_cluster_pies(cluster_data_1, cluster_data_2, autobahn_data)
    
    
    # --- 3. Preis-Analyse (Line Charts reagieren auf Kraftstoff-Buttons) ---
    @app.callback(
        Output("price_diff_cluster_1_line", "figure"),
        Output("price_diff_cluster_2_line", "figure"),
        Output("price_diff_cluster_1_boxplot", "figure"),
        Output("price_diff_cluster_2_boxplot", "figure"),
        Input("fuel-btn-diesel-competition", "n_clicks"),
        Input("fuel-btn-e5-competition", "n_clicks"),
        Input("fuel-btn-e10-competition", "n_clicks"),
    )
    def update_price_analysis(n_diesel, n_e5, n_e10):
        ctx = callback_context
        if not ctx.triggered:
            fuel_type = "diesel" 
        else:
            button_id = ctx.triggered[0]["prop_id"].split(".")[0]
            fuel_type = button_id.replace("fuel-btn-", "").replace("-competition", "")

        path_diff_1 = PROJECT_ROOT / "data" / "competition" / f"cluster_1_diff_{fuel_type}.csv"
        path_diff_2 = PROJECT_ROOT / "data" / "competition" / f"cluster_2_diff_{fuel_type}.csv"

        try:
            df_diff_1 = pd.read_csv(path_diff_1)
            fig_line_1 = plot_price_difference_line(df_diff_1, "Cluster 1", fuel_type)
            fig_boxplot_1 = plot_price_difference_boxplot(df_diff_1, "Cluster 1", fuel_type)

            df_diff_2 = pd.read_csv(path_diff_2)
            fig_line_2 = plot_price_difference_line(df_diff_2, "Cluster 2", fuel_type)
            fig_boxplot_2 = plot_price_difference_boxplot(df_diff_2, "Cluster 2", fuel_type)

            return fig_line_1, fig_line_2, fig_boxplot_1, fig_boxplot_2

        except Exception as e:
            # Das hier zeigt dir im Terminal GENAU, welche Zeile knallt
            import traceback
            traceback.print_exc() 
            print(f"Fehler Details: {e}")
            return no_update, no_update, no_update, no_update
        
    @app.callback(
    Output("fuel-btn-diesel-competition", "color"),
    Output("fuel-btn-e5-competition", "color"),
    Output("fuel-btn-e10-competition", "color"),
    Input("fuel-btn-diesel-competition", "n_clicks"),
    Input("fuel-btn-e5-competition", "n_clicks"),
    Input("fuel-btn-e10-competition", "n_clicks"),
    )

    def highlight_active_button(n_diesel, n_e5, n_e10):
        ctx = callback_context

        if not ctx.triggered:
            active = "diesel"
        else:
            button_id = ctx.triggered[0]["prop_id"].split(".")[0]
            active = button_id.replace("fuel-btn-", "").replace("-competition", "")

        return (
            "info" if active == "diesel" else "primary",
            "info" if active == "e5" else "primary",
            "info" if active == "e10" else "primary",
        )