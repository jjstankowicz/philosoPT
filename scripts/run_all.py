from philo.questioner import Questioner
from collections import Counter

VERBOSE = False


def main():
    q = Questioner()
    ### Get all philosophies ###
    ###
    print("Getting all philosophies...")
    philosophies = q.get_philosophies(prompt_version_number=1)
    ### Get all actions from all philosophies ###
    ###
    print("Getting actions from all philosophies...")
    collect_actions_from_phiolosophies = []
    for philosophy_dict in philosophies:
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
    ### Collect actions into a list ###
    ###
    print("Collecting actions into a list...")
    collect_all_actions = []
    for action in collect_actions_from_phiolosophies:
        for action_dict in action["actions"]:
            collect_all_actions.append(action_dict["action"])
    if VERBOSE:
        for a in collect_all_actions:
            print(a)
    ### Cluster the actions
    ###
    # print("Clustering actions...")
    clusters_to_actions_dict = q.get_clusters_to_actions(
        prompt_version_number=0,
        action_list=collect_all_actions,
        verbose=True,
        pbar=True,
        # force_refresh=True,
    )
    sorted_actions = []
    for value_dict in clusters_to_actions_dict.values():
        for d in value_dict:
            sorted_actions.append(d["action"])
    import pdb

    pdb.set_trace()


if __name__ == "__main__":
    main()
