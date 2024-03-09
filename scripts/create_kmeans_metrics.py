from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from philo.utils import load_results_dfs
import plotly.graph_objects as go
import plotly.offline as ol
import numpy as np
import pandas as pd


def main():
    df, dfh = load_results_dfs()
    number_of_clusters = []
    inertias = []
    silhouette_scores = []
    random_seeds = []
    for k in range(2, 20):
        for r in range(100):
            kmeans = KMeans(n_clusters=k, random_state=r)
            kmeans.fit(df)
            number_of_clusters.append(k)
            inertias.append(kmeans.inertia_)
            predicted_labels = kmeans.predict(df)
            silhouette_scores.append(silhouette_score(df, predicted_labels))
            random_seeds.append(r)
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
        }
    )
    result_df = df.groupby("number_of_clusters").agg(
        inertia_mean=("inertias", "mean"),
        inertia_sem=("inertias", "sem"),
        silhouette_score_mean=("silhouette_scores", "mean"),
        silhouette_score_sem=("silhouette_scores", "sem"),
    )

    # Assuming `df` is your DataFrame with the table you provided

    # Create traces
    trace1 = go.Scatter(
        x=result_df.index,
        y=result_df["inertia_mean"],
        name="Inertia Mean",
        mode="lines+markers",
        error_y=dict(
            type="data",  # or 'percent' for percentage based error
            array=result_df["inertia_sem"],
            visible=True,
        ),
    )

    trace2 = go.Scatter(
        x=result_df.index,
        y=result_df["silhouette_score_mean"],
        name="Silhouette Score Mean",
        mode="lines+markers",
        error_y=dict(
            type="data",  # or 'percent' for percentage based error
            array=result_df["silhouette_score_sem"],
            visible=True,
        ),
    )

    # Create the figure and add traces
    fig = go.Figure()
    fig.add_trace(trace1)
    fig.add_trace(trace2)

    # Update layout
    fig.update_layout(
        title="Cluster Quality Metrics with Error Bars",
        xaxis_title="Number of Clusters",
        yaxis_title="Min/maxed Metric Value",
        legend_title="Metric",
    )

    # Show plot
    ol.plot(fig, filename="results/kmeans_metrics.html")


if __name__ == "__main__":
    main()
