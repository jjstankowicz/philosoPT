from philo.analyzer import Analyzer


def main():
    analyzer = Analyzer()
    analyzer.set_df_philosophy()
    analyzer.set_distance_heatmap_philosophy()
    analyzer.save_distance_heatmap_philosophy()


if __name__ == "__main__":
    main()
