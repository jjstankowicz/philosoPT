from philo.analyzer import Analyzer


def main():
    analyzer = Analyzer()
    analyzer.set_df_kmeans()
    analyzer.set_metrics_plot_kmeans()
    analyzer.save_metrics_plot_kmeans()


if __name__ == "__main__":
    main()
