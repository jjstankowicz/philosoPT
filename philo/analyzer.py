from itertools import product
import tqdm
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
from philo.utils import load_results_dfs
import plotly.graph_objects as go
import plotly.offline as ol
import numpy as np
import pandas as pd


class Analyzer:
    def __init__(self):
        self.df, _ = load_results_dfs()

        self.set_action_data()
        self.set_pca_action_data()

    def set_action_data(self) -> None:
        """Set the action_data attribute with the results of the PCA analysis."""
        self.action_data = self.df.values

    def set_pca_action_data(self) -> None:
        """Set the pca_action_data attribute with the results of the PCA analysis."""
        n_components = 1
        explained_variance = 0.0
        while explained_variance < 0.95:
            n_components += 1
            pca = PCA(n_components=n_components)
            pca.fit(self.df)
            explained_variance = pca.explained_variance_ratio_.sum()
        pca_action_data = pca.transform(self.df)
        self.pca_action_data = pca_action_data

    def set_df_kmeans(
        self,
        number_of_random_seeds: int = 100,
    ) -> None:
        """Set the kmeans_df attribute with the results of the KMeans clustering analysis.

        Args:
            number_of_random_seeds (int, optional): Number of KMeans trials. Defaults to 100.
        """
        number_of_clusters = []
        inertias = []
        silhouette_scores = []
        random_seeds = []
        vector_type = []

        iterator = product(range(2, 20), range(number_of_random_seeds), ["actions", "pca_actions"])
        iterator = list(iterator)

        for k, r, v in tqdm.tqdm(iterator):
            if v == "actions":
                data = self.action_data
            elif v == "pca_actions":
                data = self.pca_action_data
            kmeans = KMeans(n_clusters=k, random_state=r)
            kmeans.fit(data)
            number_of_clusters.append(k)
            inertias.append(kmeans.inertia_)
            predicted_labels = kmeans.predict(data)
            silhouette_scores.append(silhouette_score(data, predicted_labels))
            random_seeds.append(r)
            vector_type.append(v)

        # Min/max scale the inertia and silhouette scores
        inertias = np.array(inertias)
        silhouette_scores = np.array(silhouette_scores)
        inertias = (inertias - min(inertias)) / (max(inertias) - min(inertias))
        silhouette_scores = (silhouette_scores - min(silhouette_scores)) / (
            max(silhouette_scores) - min(silhouette_scores)
        )
        df = pd.DataFrame(
            {
                "inertias": inertias,
                "silhouette_scores": silhouette_scores,
                "random_seeds": random_seeds,
                "number_of_clusters": number_of_clusters,
                "vector_type": vector_type,
            }
        )
        result_df = df.groupby(["number_of_clusters", "vector_type"]).agg(
            inertia_mean=("inertias", "mean"),
            inertia_sem=("inertias", "sem"),
            silhouette_score_mean=("silhouette_scores", "mean"),
            silhouette_score_sem=("silhouette_scores", "sem"),
        )
        self.df_kmeans = result_df

    def set_kmeans_trace_configs(self) -> None:
        """Set the kmeans_trace_configs attribute with the configurations for the KMeans metrics plot."""
        self.kmeans_trace_configs = {
            "Actions Inertia": {
                "dataframe": self.df_kmeans.xs("actions", level="vector_type"),
                "y_col": "inertia_mean",
                "error_y_col": "inertia_sem",
            },
            "Actions Silhouette Score": {
                "dataframe": self.df_kmeans.xs("actions", level="vector_type"),
                "y_col": "silhouette_score_mean",
                "error_y_col": "silhouette_score_sem",
            },
            "PCA Actions Inertia": {
                "dataframe": self.df_kmeans.xs("pca_actions", level="vector_type"),
                "y_col": "inertia_mean",
                "error_y_col": "inertia_sem",
            },
            "PCA Actions Silhouette Score": {
                "dataframe": self.df_kmeans.xs("pca_actions", level="vector_type"),
                "y_col": "silhouette_score_mean",
                "error_y_col": "silhouette_score_sem",
            },
        }

    def set_kmeans_metrics_plot(self) -> None:
        """Set the kmeans_metrics_plot attribute with the Plotly figure for the KMeans metrics plot."""
        self.set_kmeans_trace_configs()

        # Initialize a Plotly figure
        fig = go.Figure()

        # Loop over the configuration and create each trace
        for trace_name, config in self.kmeans_trace_configs.items():
            trace = go.Scatter(
                x=config["dataframe"].index.get_level_values("number_of_clusters"),
                y=config["dataframe"][config["y_col"]],
                error_y=dict(
                    type="data", array=config["dataframe"][config["error_y_col"]], visible=True
                ),
                mode="lines+markers",
                name=trace_name,
            )
            fig.add_trace(trace)

        # Update layout if needed
        fig.update_layout(
            title="Clustering Quality Metrics by Vector Type",
            xaxis_title="Number of Clusters",
            yaxis_title="Metric Values (Min-Max Scaled)",
            legend_title="Traces",
        )

        self.kmeans_metrics_plot = fig

    def save_kmeans_metrics_plot(self) -> None:
        """Save the KMeans metrics plot to an HTML file."""
        ol.plot(self.kmeans_metrics_plot, filename="results/kmeans_metrics.html")
