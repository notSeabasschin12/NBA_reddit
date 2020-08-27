"""
Module to analyze management of a basketball team and whether or not race is a
factor in how people blame/credit someone for a team's performance.

Creator: Sebastian Guo
"""
import assertions
import pandas
import numpy

def calc_mgmt_stats(global_ID_list, mgmt_list, roster_file, team):
    """
    A function to calculate statistical averages for comment sentiment and
    management mentions. It takes in a csv file created by function
    coach_mentions_glob() which contains data about comment sentiment for
    comments mentioning management. The function then finds the average net
    sentiment per game won/loss per race and average positive/negative comments
    per won/loss game per race. To make the stats comparable, the averages are
    divided by the number of AA or CA coaches.

    In a separate file, the function looks at the probability a coach is mentioned
    after a won/loss. To do so, it finds the average times a coach is mentioned
    separated into wins and losses, and other factors that could be correlated
    like race, salary, or experience.

    Average net sentiment per game won/loss for a race = (net sentiment per race
    for all won/loss games / # of won/loss games) / # of coaches for a race.
    Average mentions per game won/loss for a coach = total mentions of that coach
    in all won/loss games / won/loss games
    If average pos/neg comments of a race per game is zero, then assume that the
    team has no managers of that race.

    Parameter global_ID_list: a list of global IDs that make up a scrapped file
    of Reddit comment data.
    Precondition: must be a list with integer entries.

    Parameter mgmt_list: a list of managers for a basketball team.
    Precondition: must be a list with string entries.

    Parameter roster_file: a csv file containing player/coach names and nicknames.
    Precondition: must be a DataFrame with the correct headers.

    Parameter team: the team that the function works on.
    Precondition: must be a string.
    """
    _assertion_calc_mgmt_stats(global_ID_list, mgmt_list, roster_file, team)
    end_dict = {"Statistic Per Game Won or Lost (Per Coach)":["Manager Average Net Sentiment Per Game",
        "AA", "CA", "Manager Average Positive Comments Per Game","AA", "CA",
        "Manager Average Negative Comments Per Game", "AA", "CA"], "Win":[],"Loss":[]}
    # Store all stats in a dictionary to be passed into a helper function.
    stat_dict = {"win_aa_pos_cmt":0, "win_aa_neg_cmt":0, "win_ca_pos_cmt":0,
        "win_ca_neg_cmt":0, "loss_aa_pos_cmt":0, "loss_aa_neg_cmt":0,
        "loss_ca_pos_cmt":0, "loss_ca_neg_cmt":0, "win_aa_net_sent":0,
        "win_ca_net_sent":0, "loss_aa_net_sent":0, "loss_ca_net_sent":0}
    info_dict = {"won_games":0, "lost_games":0, "aa_coach":0, "ca_coach":0}
    ment_dict = {"Coach":[], "Race":[], "Annual Salary":[], "Seasons Spent":[],
        "Mentions Per Win":[], "Mentions Per Loss":[]}
    _find_num_coaches(roster_file, info_dict, mgmt_list)
    _add_ment_dict(ment_dict, info_dict, roster_file, mgmt_list)
    for term in global_ID_list:
        # File from coach_mentions_glob().
        with open("/home/sebastianguo/Documents/Research/Teams/" + team +
            "/mgmt_and_race_by_game/" + str(term) + ".csv", newline='') as game_reader:
            mgmt_race_reader = pandas.read_csv(game_reader)
        assertions.assert_mgmt_and_race_file_format(mgmt_race_reader, mgmt_list)
        stat_dict, ment_dict, info_dict = _add_to_dicts(mgmt_list, mgmt_race_reader,
            stat_dict, ment_dict, info_dict, term)
    _average_final_stats(stat_dict, info_dict, mgmt_list)
    _add_end_dict(end_dict, stat_dict, info_dict)

    df = pandas.DataFrame(end_dict)
    df2 = pandas.DataFrame(ment_dict)
    df2["Mentions Per Win"] = (df2["Mentions Per Win"] /
        info_dict["won_games"]).round(decimals = 4)
    df2["Mentions Per Loss"] = (df2["Mentions Per Loss"] /
        info_dict["lost_games"]).round(decimals = 4)
    df2["Mentions Ratio (Per Win/Per Loss)"] = (df2["Mentions Per Win"] /
        df2["Mentions Per Loss"]).round(decimals = 4)

    df.to_csv(r'/home/sebastianguo/Documents/Research/Teams/' + team +
        '/mgmt_sentiment.csv', index=False)
    df2.to_csv(r'/home/sebastianguo/Documents/Research/Teams/' + team +
        '/mgmt_mentions.csv', index=False)

def _find_num_coaches(roster_file, info_dict, mgmt_list):
    """ Finds total number of African American and Caucasian Coaches. """
    for term in mgmt_list:
        ind_lst = roster_file.index[roster_file["Player"] == term].tolist()
        try:
            if roster_file["Race"][ind_lst[0]] == "AA":
                info_dict["aa_coach"] += 1
            elif roster_file["Race"][ind_lst[0]] == "CA":
                info_dict["ca_coach"] += 1
        except:
            raise Exception("Couldn't find a race index for a management person.")
    return info_dict

def _add_ment_dict(ment_dict, info_dict, roster_file, mgmt_list):
    """ Adds coaches and other attributes to the ment_dict. """
    person = roster_file["Player"]
    race = roster_file["Race"]
    salary = roster_file["Annual Salary"]
    seasons = roster_file["Seasons Spent"]
    for manager in mgmt_list:
        row_ind = roster_file.index[person == manager].tolist()
        ment_dict["Coach"].append(manager)
        ment_dict["Race"].append(race[row_ind[0]])
        ment_dict["Annual Salary"].append(salary[row_ind[0]])
        ment_dict["Seasons Spent"].append(seasons[row_ind[0]])
        ment_dict["Mentions Per Win"].append(0)
        ment_dict["Mentions Per Loss"].append(0)
    return ment_dict

def _add_to_dicts(mgmt_list, mgmt_race_reader, stat_dict, ment_dict, info_dict, term):
    """
    A helper function to add up net sentiment and total mentions for a data frame
    created by function coach_mentions_glob(). After looping through every data
    frame, stat_dict should contain aggregate statistics for net sentiment, total
    mentions, and positive/negative comments.
    """
    pos_cmt = mgmt_race_reader["Positive comments"]
    neg_cmt = mgmt_race_reader["Negative comments"]
    net_sent = mgmt_race_reader["Net sentiment"]
    mentions = mgmt_race_reader["Mentions"]
    result = mgmt_race_reader["Name"][len(mgmt_list)]
    if result == "Win": info_dict["won_games"] += 1
    elif result == "Lose": info_dict["lost_games"] += 1
    for row_ind in range(len(mgmt_list)):
        ethnicity = mgmt_race_reader["Race"][row_ind]
        row_net_sent = net_sent[row_ind]
        row_pos_cmts = pos_cmt[row_ind]
        row_neg_cmts = neg_cmt[row_ind]
        row_ment = mentions[row_ind]
        if result == "Win":
            ment_dict["Mentions Per Win"][row_ind] += row_ment
            if ethnicity == "AA":
                stat_dict["win_aa_net_sent"] += row_net_sent
                stat_dict["win_aa_pos_cmt"] += row_pos_cmts
                stat_dict["win_aa_neg_cmt"] += row_neg_cmts
            elif ethnicity == "CA":
                stat_dict["win_ca_pos_cmt"] += row_pos_cmts
                stat_dict["win_ca_neg_cmt"] += row_neg_cmts
                stat_dict["win_ca_net_sent"] += row_net_sent
        elif result == "Lose":
            ment_dict["Mentions Per Loss"][row_ind] += row_ment
            if ethnicity == "AA":
                stat_dict["loss_aa_pos_cmt"] += row_pos_cmts
                stat_dict["loss_aa_neg_cmt"] += row_neg_cmts
                stat_dict["loss_aa_net_sent"] += row_net_sent
            elif ethnicity == "CA":
                stat_dict["loss_ca_pos_cmt"] += row_pos_cmts
                stat_dict["loss_ca_neg_cmt"] += row_neg_cmts
                stat_dict["loss_ca_net_sent"] += row_net_sent
    return stat_dict, ment_dict, info_dict

def _average_final_stats(stat_dict, info_dict, mgmt_list):
    """
    A helper function to find averages for net sentiment and mentions per game.
    It divides all of the statistics on net sentiment and mentions for race and
    game results by the number of won or lost games for a file of global IDs.
    """
    games_won = info_dict["won_games"]
    games_lost = info_dict["lost_games"]
    stat_dict["win_aa_net_sent"] /= games_won
    stat_dict["loss_aa_net_sent"] /= games_lost
    stat_dict["win_aa_pos_cmt"] /= games_won
    stat_dict["win_aa_neg_cmt"] /= games_won
    stat_dict["loss_aa_pos_cmt"] /= games_lost
    stat_dict["loss_aa_neg_cmt"] /= games_lost
    stat_dict["win_ca_net_sent"] /= games_won
    stat_dict["loss_ca_net_sent"] /= games_lost
    stat_dict["win_ca_pos_cmt"] /= games_won
    stat_dict["win_ca_neg_cmt"] /= games_won
    stat_dict["loss_ca_pos_cmt"] /= games_lost
    stat_dict["loss_ca_neg_cmt"] /= games_lost
    num_aa = info_dict["aa_coach"] if info_dict["aa_coach"] != 0 else 1
    num_ca = info_dict["ca_coach"] if info_dict["ca_coach"] != 0 else 1
    for key in stat_dict:
        if "aa" in key:
            stat_dict[key] /= num_aa
        elif "ca" in key:
            stat_dict[key] /= num_ca
        stat_dict[key] = round(stat_dict[key], 4)
    return stat_dict

def _add_end_dict(end_dict, stat_dict, info_dict):
    """
    A helper function to add the aggregate averaged stats in stat_dict to end_dict.
    end_dict is the dictionary that will be turned into a pandas DataFrame object.
    """
    end_dict["Win"] += ["", stat_dict["win_aa_net_sent"], stat_dict["win_ca_net_sent"],
        "", stat_dict["win_aa_pos_cmt"], stat_dict["win_ca_pos_cmt"], "",
        stat_dict["win_aa_neg_cmt"], stat_dict["win_ca_neg_cmt"], ""]
    end_dict["Loss"] += ["",stat_dict["loss_aa_net_sent"], stat_dict["loss_ca_net_sent"],
        "", stat_dict["loss_aa_pos_cmt"], stat_dict["loss_ca_pos_cmt"], "",
        stat_dict["loss_aa_neg_cmt"], stat_dict["loss_ca_neg_cmt"], ""]
    end_dict["Statistic Per Game Won or Lost (Per Coach)"].append("Win/Loss Ratio: " +
        str(info_dict["won_games"]) + "/" + str(info_dict["lost_games"]))
    return end_dict

def compile_mgmt_stats(team_list):
    """
    Takes the csv files created by calc_mgmt_stats and compiles them into one
    aggregate file to look at all of the teams.
    """
    end_dict = {"Statistic Overall For All Teams":["Manager Average Net Sentiment Per Game",
        "AA", "CA", "Manager Average Positive Comments Per Game","AA", "CA",
        "Manager Average Negative Comments Per Game", "AA", "CA",
        "Manager Average Mentions Per Game", "AA", "CA"], "Win":["",0,0,"",0,0,"",0,0,"",0,0],
        "Loss":["",0,0,"",0,0,"",0,0,"",0,0]}
    num_teams = len(team_list)
    for team_name in team_list:
        # File from calc_mgmt_stats().
        with open("/home/sebastianguo/Documents/Research/Teams/" + team_name +
            "/mgmt_sentiment.csv", newline='') as mgmt_stat_reader:
            mgmt_stat_reader = pandas.read_csv(mgmt_stat_reader)
        assertions.assert_mgmt_stat_file_format(mgmt_stat_reader)
        win_row = mgmt_stat_reader["Win"]
        loss_row = mgmt_stat_reader["Loss"]
        # Loop through "Win" and "Loss" rows, formatting is asserted by prev func.
        for row in range(mgmt_stat_reader.shape[0]):
            if not pandas.isnull(win_row[row]):
                end_dict["Win"][row] += win_row[row]
                end_dict["Loss"][row] += loss_row[row]
                if team_list[num_teams-1] == team_name:
                    end_dict["Win"][row] = round(end_dict["Win"][row]/num_teams, 4)
                    end_dict["Loss"][row] = round(end_dict["Loss"][row]/num_teams, 4)
    df = pandas.DataFrame(end_dict)
    df.to_csv(r'/home/sebastianguo/Documents/Research/misc_data/all_teams_mgmt_stats.csv',
        index=False)

def _assertion_calc_mgmt_stats(global_ID_list, mgmt_list, roster_file, team):
    """ Function to assert assertions for calc_mgmt_stats(). """
    assertions.assert_int_list(global_ID_list)
    assertions.assert_str_list(mgmt_list)
    assertions.assert_roster_file_format(roster_file)
    assertions.assert_team(team)
