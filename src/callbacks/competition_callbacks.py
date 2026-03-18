from dash import Input, Output, callback_context, no_update
import pandas as pd
import polars as pl
from pathlib import Path
from src.figures.competition_figures import plot_clusters, plot_motorway_cluster_pies, plot_price_difference_line, plot_price_difference_boxplot

PROJECT_ROOT = Path(__file__).resolve().parents[2]

def register_competition_callbacks(app):
    
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