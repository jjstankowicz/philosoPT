from itertools import product
import tqdm
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
from scipy.spatial import distance_matrix
from philo.utils import load_results_dfs
import plotly.graph_objects as go
import plotly.offline as ol
import plotly.figure_factory as ff


class Analyzer:
    def __init__(self):
        self.df, _ = load_results_dfs()

        self.set_data_action()
        self.set_data_action_pca()

    def set_data_action(self) -> None:
        """Set the action_data attribute with the results of the PCA analysis."""
        self.action_data = self.df.values

    def set_data_action_pca(self) -> None:
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

    def set_trace_configs_kmeans(self) -> None:
        """Set the kmeans_trace_configs attribute with the configurations for the KMeans metrics plot."""
        self.trace_configs_kmeans = {
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

    def set_metrics_plot_kmeans(self) -> None:
        """Set the kmeans_metrics_plot attribute with the Plotly figure for the KMeans metrics plot."""
        self.set_trace_configs_kmeans()

        # Initialize a Plotly figure
        fig = go.Figure()

        # Loop over the configuration and create each trace
        for trace_name, config in self.trace_configs_kmeans.items():
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

        self.metrics_plot_kmeans = fig

    def save_metrics_plot_kmeans(self) -> None:
        """Save the KMeans metrics plot to an HTML file."""
        ol.plot(self.metrics_plot_kmeans, filename="results/metrics_kmeans.html")

    def set_df_philosophy(self) -> None:
        """Set the philosophy_df attribute a dataframe of distances."""
        data = self.action_data
        # Compute the distance matrix between the philosophy data
        m_dist = distance_matrix(data, data)
        # Min-max scale the distance matrix
        m_dist = (m_dist - m_dist.min()) / (m_dist.max() - m_dist.min())
        self.df_philosophy = pd.DataFrame(m_dist, index=self.df.index, columns=self.df.index)

    def set_distance_heatmap_philosophy(self):
        # Extract labels and convert the DataFrame to a numpy array
        labels = self.df_philosophy.columns.tolist()
        data_array = self.df_philosophy.values

        # Initialize figure with bottom dendrogram
        fig = ff.create_dendrogram(data_array, orientation="bottom", labels=labels)
        for i in range(len(fig["data"])):
            fig["data"][i]["yaxis"] = "y2"

        # Create Side Dendrogram
        dendro_side = ff.create_dendrogram(data_array, orientation="right", labels=labels)
        for i in range(len(dendro_side["data"])):
            dendro_side["data"][i]["xaxis"] = "x2"

        # Add Side Dendrogram Data to Figure
        for data in dendro_side["data"]:
            fig.add_trace(data)

        # Determine the new order based on the dendrogram
        dendro_leaves_labels = dendro_side["layout"]["yaxis"]["ticktext"]
        dendro_leaves_indices = [labels.index(i) for i in dendro_leaves_labels]

        # Reorder the data based on the dendrogram
        data_reordered = data_array[np.ix_(dendro_leaves_indices, dendro_leaves_indices)]

        # Match the ticktext to the tickvals to create a mapping
        dendro_ticks = dict(
            zip(
                dendro_side["layout"]["yaxis"]["ticktext"],
                dendro_side["layout"]["yaxis"]["tickvals"],
            )
        )

        # Map the labels to their corresponding tickvals
        heatmap_x = [dendro_ticks[x] for x in dendro_leaves_labels]
        heatmap_y = [dendro_ticks[y] for y in dendro_leaves_labels]

        # Create an outer product of the keys of the dendro_ticks dictionary
        ordered_philosophy_labels = list(dendro_ticks.keys())
        hover_text = [
            [
                f"Row: {ordered_philosophy_labels[i]}<br>Column: {ordered_philosophy_labels[j]}<br>Value: {data_reordered[i][j]}"
                for j in range(len(dendro_leaves_labels))
            ]
            for i in range(len(dendro_leaves_labels))
        ]

        heatmap = [
            go.Heatmap(
                x=heatmap_x,  # numerical positions from dendrogram tickvals
                y=heatmap_y,  # numerical positions from dendrogram tickvals
                z=data_reordered,
                colorscale="Blues",
                customdata=np.tile(
                    dendro_leaves_labels, (len(dendro_leaves_labels), 1)
                ),  # Repeat the labels for each row
                hoverinfo="text",
                hovertext=hover_text,
            )
        ]

        # Add Heatmap Data to Figure
        for data in heatmap:
            fig.add_trace(data)

        fig.update_layout(
            # Adjust axis properties
            xaxis=dict(showgrid=False, ticks="", side="bottom", domain=[0.15, 1]),
            yaxis=dict(showgrid=False, showticklabels=False, ticks="", domain=[0, 0.85]),
            xaxis2=dict(showgrid=False, showticklabels=False, domain=[0, 0.15]),
            yaxis2=dict(showgrid=False, showticklabels=False, domain=[0.825, 0.975]),
            # Set the background color for the plot
            plot_bgcolor="white",
            # Set dimensions
            width=800,
            height=800,
            # Don't show the legend
            showlegend=False,
            # Set hovermode to closest
            hovermode="closest",
            # Add title
            title="Distance Heatmap of Philosophy Data<br>0 is close<br>1 is far",
        )

        # Assign the figure to a class attribute
        self.distance_heatmap_philosophy = fig

    def save_distance_heatmap_philosophy(self) -> None:
        """Save the distance heatmap to an HTML file."""
        ol.plot(
            self.distance_heatmap_philosophy, filename="results/distance_heatmap_philosophy.html"
        )
