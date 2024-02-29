from philo.questioner import Questioner


def main():
    q = Questioner(fresh_start=True)
    philosophies = q.get_philosophies(prompt_version_number=1)
    collect = []
    for i, philosophy_dict in enumerate(philosophies):
        print(f"{i+1}")
        print(philosophy_dict["name"])
        print(philosophy_dict["description"])
        actions_from_philosophies = q.get_actions_from_philosophies(
            prompt_version_number=1,
            philosophy_dict=philosophy_dict,
        )
        collect.append({"philo": philosophy_dict, "actions": actions_from_philosophies})


if __name__ == "__main__":
    main()
