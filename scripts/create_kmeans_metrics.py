from philo.analyzer import Analyzer


def main():
    analyzer = Analyzer()
    analyzer.set_df_kmeans()
    analyzer.set_kmeans_metrics_plot()
    analyzer.save_kmeans_metrics_plot()


if __name__ == "__main__":
    main()
