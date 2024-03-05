from philo.questioner import Questioner


def main():
    q = Questioner()
    ### Get all philosophies ###
    ###
    print("Getting all philosophies...")
    philosophies = q.get_philosophies(prompt_version_number=1)
    ### Get all actions from all philosophies ###
    ###
    print("Getting actions from all philosophies...")
    collect_actions_from_philosophies = []
    for philosophy_dict in philosophies:
        actions_from_philosophies = q.get_actions_from_philosophies(
            prompt_version_number=0,
            philosophy_dict=philosophy_dict,
        )
        collect_actions_from_philosophies.append(
            {
                "philo": philosophy_dict,
                "actions": actions_from_philosophies,
            }
        )
    ### Collect actions into a list ###
    ###
    print("Collecting actions into a list...")
    collect_all_actions = []
    for action in collect_actions_from_philosophies:
        for action_dict in action["actions"]:
            collect_all_actions.append(action_dict["action"])
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
    ### Get the scores for each action
    ###
    print("Getting scores for each action...")
    # Change to GPT-3.5-turbo to get faster results
    q.set_chatbot(model="gpt-3.5-turbo")
    q.set_action_scores(
        prompt_version_number=0,
        action_list=sorted_actions,
        philosophy_list=philosophies,
        verbose=False,
        pbar=True,
        force_refresh=False,
    )
    q.create_scorecard()


if __name__ == "__main__":
    main()
