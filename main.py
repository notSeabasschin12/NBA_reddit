"""
Script file to be run. It first extracts named entities from a file with scrapped
Reddit comment data and places them according to the global ID. It then takes all
of the named entities mentioned in the scrapped file and narrows down the list
to those mentioning players from the New York Knicks basketball team.

I used regular expressions and the re Python module to extract mentions
of named entities from the data that I collected and stored in the program. I
used the pandas module which provided methods to input and manipulate data from
csv files and then export new data into csv files.

Creator: Sebastian Guo
"""
import pandas
import name_matching, mgmt_matching
import extraction_v2
import hand_code_compare
import sentiment_analysis, mgmt_analysis

def main(team, classifier):
    """
    Main function to run for research. Its purpose is detailed in the file comment.
    """
    print("Team: " + team)
    with open("/home/sebastianguo/Documents/Research/Teams/" + team +
        "/csv_data/regseason_postgame_2020_" + team + "_.csv", newline='') as raw_file:
        raw_data_reader = pandas.read_csv(raw_file)
    with open("/home/sebastianguo/Documents/Research/Teams/" + team +
        "/csv_data/roster.csv", newline='') as roster_file:
        roster_reader = pandas.read_csv(roster_file)
    with open("/home/sebastianguo/Documents/Research/misc_data/teams.csv",
        newline='') as team_file:
        team_reader = pandas.read_csv(team_file)
    with open("/home/sebastianguo/Documents/Research/Teams/" + team +
        "/csv_data/word_removal.csv", newline='') as word_file:
        word_file_reader = pandas.read_csv(word_file)
    # _format_season_results(team_reader, team)
    # Creates a 2D list with list entries that are either named entities according
    # to their global/local IDs or markers to designate a comment without a
    # named entity.
    # cmt_data_list = extraction_v2.extract_col_data(raw_data_reader, roster_reader,
    #     word_file_reader, team)
    # print("Finished running extract_col_data().")
    glob_ID_list = extraction_v2.get_global_ID(raw_data_reader)
    roster_list = name_matching.find_roster_names(roster_reader)
    mgmt_list = mgmt_matching.find_management(roster_reader)
    # # Creates a csv file named mentions.csv that takes the cmt_data_list and finds
    # # the total times each named entity is mentioned and has columns that mark
    # # the player that corresponds to the named entity in the output list of
    # # find_player_names.
    # name_matching.roster_mentions(cmt_data_list, roster_reader, roster_list, team)
    # print("Finished running roster_mentions().")
    # # Creates a csv file with all of the separate comments and with columns marking
    # # whether or not a certain comment contains a mention of a player
    # name_matching.comment_roster(raw_data_reader, roster_reader, roster_list,
    #     cmt_data_list, team)
    # print("Finished running comment_roster().")
    #
    # with open("/home/sebastianguo/Documents/Research/Teams/" + team +
    #     "/cmt_lvl_roster_mentions.csv", newline='') as cmt_lvl_ment_file:
    #      cmt_lvl_ment_reader = pandas.read_csv(cmt_lvl_ment_file)
    # _extraction_by_global_ID(glob_ID_list, roster_list, cmt_data_list, mgmt_list,
        # team, roster_reader, team_reader, cmt_lvl_ment_reader, classifier)

    mgmt_analysis.calc_mgmt_stats(glob_ID_list, mgmt_list, roster_reader, team)
    # _calculate_prec_rec(roster_list, team, cmt_lvl_ment_reader)

def _format_season_results(team_reader, team):
    """
    A function to reformat the csv file containing a basketball players season
    results. The csv file/basketball results are found from the website
    "basketball-reference.com"
    """
    with open("/home/sebastianguo/Documents/Research/Teams/" + team +
        "/csv_data/2019-2020_scores.csv", newline='') as raw_result_reader:
        raw_result_reader = pandas.read_csv(raw_result_reader)
    mgmt_matching.format_data(raw_result_reader, team_reader, team)

def _extraction_by_global_ID(glob_ID_list, roster_list, cmt_data_list, mgmt_list,
    team, roster_reader, team_reader, cmt_lvl_ment_reader, classifier):
    """
    Function that runs the functions that work by global ID. The function is split
    into two parts: one that works to extract player mentions by global ID and comment.
    The other extracts data for management and finds whether or not a game was won
    for a certain global ID. This data will be used for looking at the effect of
    race in determining a management's role in a game's result.

    1) create_data_frame() creates a list of of every named entity in a global ID
    thread. The names of the csv files are the global ID. playerMentionsGlob()
    aggregates the different named entities and marks the player the named entity
    corresponds to. comment_players_glob() lists the different comments for a
    global ID and whether or not certain players are mentioned in the comment.
    2) win_or_lose() determines whether or not the game for a global ID is a win or
    loss. coach_mentions_glob() creates separate csv files for global ID with
    management mentions, their race, and the outcome of the game.
    """
    with open("/home/sebastianguo/Documents/Research/misc_data/" +
        "game_thread_urls_2020_enhanced.csv", newline='') as glob_ID_file:
        glob_ID_reader = pandas.read_csv(glob_ID_file)
    with open("/home/sebastianguo/Documents/Research/Teams/" + team +
        "/csv_data/2019-2020_scores.csv", newline='') as result_file:
        result_reader = pandas.read_csv(result_file)
    team_str = mgmt_matching.make_team_str(team_reader, team)
    for term in glob_ID_list:
        # Part 1: separates mentions.csv and commentMentions.csv by global ID.
        extraction_v2.create_data_frame(term, cmt_data_list, team)
        # File from create_data_frame()
        with open("/home/sebastianguo/Documents/Research/Teams/" + team +
            "/roster_mentions_by_game/" + str(term) + ".csv", newline='') as ment_file:
            rost_ment_reader = pandas.read_csv(ment_file)
        name_matching.roster_mentions_glob(term, rost_ment_reader, roster_reader,
            roster_list, team)
        name_matching.comment_roster_glob(cmt_lvl_ment_reader, roster_list, term, team)

        # File from roster_mentions_glob()
        with open("/home/sebastianguo/Documents/Research/Teams/" + team +
        "/agg_roster_mentions_by_game/" + str(term) + ".csv", newline='') as agg_reader:
            agg_rost_ment_reader = pandas.read_csv(agg_reader)
        # File from comment_roster_glob()
        with open("/home/sebastianguo/Documents/Research/Teams/" + team +
            "/cmt_lvl_roster_mentions_by_game/" + str(term) + ".csv", newline='') as cmt_reader:
            cmt_lvl_ment_by_game_reader = pandas.read_csv(cmt_reader)

        # Part 2: looks at management, game results, and race.
        result = mgmt_matching.win_or_lose(glob_ID_reader, result_reader, team_str,
            term, team)
        sent_dict = sentiment_analysis.manager_cmt_sentiment(classifier,
            cmt_lvl_ment_by_game_reader, term, roster_list, mgmt_list, team)
        mgmt_matching.coach_mentions_glob(term, agg_rost_ment_reader, roster_reader,
            mgmt_list, sent_dict, result, team)
    print("Finished running extraction_by_global_ID().")

def _analyze_management(glob_ID_list, mgmt_list, roster_reader, team):
    """
    Function that finds statistics and looks at how people blame management for
    a team's performance in a game.
    """
    mgmt_analysis.calc_mgmt_sentiment(glob_ID_list, mgmt_list, roster_reader, team)


def _calculate_prec_rec(roster_list, team, cmt_lvl_ment_reader):
    """
    Function that creates a csv file title precisionAndRecall.csv to find the amount
    of true positives, false positive, and false negatives when comparing the machine
    code run commentMentions.csv to a manually created hand code file. Then, calculate
    precision and recall to determine accuracy of the machine code.
    """
    with open("/home/sebastianguo/Documents/Research/Teams/" + team +
        "/csv_data/hand_code_sample.csv", newline='') as hand_code_file:
        hand_code_reader = pandas.read_csv(hand_code_file)
    hand_code_compare.compare_files(cmt_lvl_ment_reader, hand_code_reader,
        roster_list, team)

if __name__ == '__main__':
    team_list = ["76ers"]
    print("Training classifier.")
    classifier = sentiment_analysis.train_classifier()
    print("Finished training classifier.")
    for team_name in team_list:
        main(team_name, classifier)
    print("Finished running main().")
