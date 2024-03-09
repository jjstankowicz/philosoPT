from philo.questioner import Questioner


def main():
    q = Questioner()
    ### Get all philosophies ###
    ###
    print("Getting all philosophies...")
    q.set_philosophies(prompt_version_number=1)
    ### Get all actions from all philosophies ###
    ###
    print("Getting actions from all philosophies...")
    q.set_all_actions_from_philosophies()
    ### Collect actions into a list ###
    ###
    print("Collecting actions into a list...")
    q.set_all_actions()
    ### Cluster the actions
    ###
    # print("Clustering actions...")
    q.set_clusters_to_actions(
        prompt_version_number=0,
        verbose=True,
        pbar=True,
        # force_refresh=True,
    )
    q.set_sorted_actions()
    ### Get the scores for each action
    ###
    print("Getting scores for each action...")
    # Change to GPT-3.5-turbo to get faster results
    q.set_chatbot(model="gpt-3.5-turbo")
    q.set_action_scores(
        prompt_version_number=0,
        verbose=False,
        pbar=True,
        force_refresh=False,
    )
    q.create_scorecard()


if __name__ == "__main__":
    main()
