from philo.questioner import Questioner


def main():
    q = Questioner()
    philosophies = q.get_philosophies(version_number=0)
    print(philosophies)


if __name__ == "__main__":
    main()
