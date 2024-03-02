from philo.questioner import Questioner
from collections import Counter

VERBOSE = False


def main():
    q = Questioner()
    philosophies = q.get_philosophies(prompt_version_number=1)
    collect_actions_from_phiolosophies = []
    for philosophy_dict in philosophies:
        if VERBOSE:
            print(f'---{philosophy_dict["name"]}---')
            print(philosophy_dict["description"])
        actions_from_philosophies = q.get_actions_from_philosophies(
            prompt_version_number=0,
            philosophy_dict=philosophy_dict,
        )
        collect_actions_from_phiolosophies.append(
            {
                "philo": philosophy_dict,
                "actions": actions_from_philosophies,
            }
        )
    collect_all_actions = []
    for action in collect_actions_from_phiolosophies:
        if VERBOSE:
            print(f'---{action["philo"]["name"]}---')
            print(action["philo"]["description"])
            print("")
        for action_dict in action["actions"]:
            if VERBOSE:
                print(action_dict["morality"])
                print(action_dict["action"])
                print(action_dict["reason"])
                print("")
            collect_all_actions.append(action_dict["action"])
    if VERBOSE:
        for a in collect_all_actions:
            print(a)
    action_clusters = q.get_action_clusters(
        prompt_version_number=0,
        action_list=collect_all_actions,
        force_refresh=True,
    )
    for cluster, actions in action_clusters.items():
        print(f"---{cluster}---")
        for action in actions:
            print(" ", action)
        print("")
    import pdb

    pdb.set_trace()


if __name__ == "__main__":
    main()
