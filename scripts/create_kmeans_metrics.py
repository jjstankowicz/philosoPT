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


def create_result_df(
    action_data: np.ndarray,
    pca_action_data: np.ndarray,
    number_of_random_seeds: int = 100,
) -> pd.DataFrame:
    number_of_clusters = []
    inertias = []
    silhouette_scores = []
    random_seeds = []
    vector_type = []

    iterator = product(range(2, 20), range(number_of_random_seeds), ["actions", "pca_actions"])
    iterator = list(iterator)

    for k, r, v in tqdm.tqdm(iterator):
        if v == "actions":
            data = action_data
        elif v == "pca_actions":
            data = pca_action_data
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
    return result_df


def get_pca_action_data(df: pd.DataFrame) -> np.ndarray:
    n_components = 1
    explained_variance = 0.0
    while explained_variance < 0.95:
        n_components += 1
        pca = PCA(n_components=n_components)
        pca.fit(df)
        explained_variance = pca.explained_variance_ratio_.sum()
    pca_action_data = pca.transform(df)
    return pca_action_data


def create_metrics_plot(df: pd.DataFrame) -> go.Figure:
    trace_configs = {
        "Actions Inertia": {
            "dataframe": df.xs("actions", level="vector_type"),
            "y_col": "inertia_mean",
            "error_y_col": "inertia_sem",
        },
        "Actions Silhouette Score": {
            "dataframe": df.xs("actions", level="vector_type"),
            "y_col": "silhouette_score_mean",
            "error_y_col": "silhouette_score_sem",
        },
        "PCA Actions Inertia": {
            "dataframe": df.xs("pca_actions", level="vector_type"),
            "y_col": "inertia_mean",
            "error_y_col": "inertia_sem",
        },
        "PCA Actions Silhouette Score": {
            "dataframe": df.xs("pca_actions", level="vector_type"),
            "y_col": "silhouette_score_mean",
            "error_y_col": "silhouette_score_sem",
        },
    }

    # Initialize a Plotly figure
    fig = go.Figure()

    # Loop over the configuration and create each trace
    for trace_name, config in trace_configs.items():
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

    return fig


def main():
    df, _ = load_results_dfs()

    action_data = df.values
    pca_action_data = get_pca_action_data(df)

    result_df = create_result_df(action_data, pca_action_data)

    import pdb

    pdb.set_trace()

    fig = create_metrics_plot(result_df)

    # Show plot
    ol.plot(fig, filename="results/kmeans_metrics.html")


if __name__ == "__main__":
    main()
