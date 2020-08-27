"""
Module to extract data from scrapped Reddit comments about mentions of management.
This module also finds whether or not a global ID thread corresponds to a won or
lost game for the team. This extracted mention data will be used with the result
of the games to analyze whether or not mentions of a manager's role in a game's
result are correlated to their race.

Creator: Sebastian Guo
"""
import pandas, string, re
import assertions

def coach_mentions_glob(global_ID, agg_rost_ment_file, roster_file, mgmt_list,
    sent_dict, result, team):
    """
    A function that outputs a csv file separated by thread/global ID. This file
    contains the different coaches, general managers, and owners of a basketball
    team, how many times their mentioned, their race, and whether or not the
    game for the team was won or not. It also includes calculations regarding the
    positivity and negativity of comments that mention the management team.
    Sentiment ratio is pos comm/neg comm. If sentiment ratio = 1, overall sentiment
    is neutral. A ratio less than 1 is overall negative and more than 1 is overall
    positive.

    Parameter global_ID: the global ID/thread that the function finds mentions in.
    Precondition: must be an integer greater than zero.

    Parameter agg_rost_ment_file: a csv file created from roster_mentions_glob()
    which contains the aggregate mentions of roster people for a global ID.
    Precondition: must be a DataFrame object created by the pandas module. It
    must contain the correct headers.

    Parameter roster_file: a reader object that contains information about player
    names and nicknames.
    Precondition: must be a DataFrame object created by the pandas module. It must
    also contain the correct headers.

    Parameter mgmt_list: a list containing the coaches, GMs, and owners of a team.
    Precondition: must be of type list and contain strings.

    Parmaeter sent_dict: a dictionary with managers as keys and comment sentiment
    as values.
    Precondition: must be a dictionary with string keys and list values.

    Parameter result: whether or not the game corresponding to the global ID was won.
    Precondition: must be either "Win", "Lose", or "N/A".

    Parameter team: the basketball team the code is run on.
    Precondition: team is of type string
    """
    _assertion_coach_mentions_glob(global_ID, agg_rost_ment_file, roster_file,
        mgmt_list, sent_dict, result, team)
    ment = agg_rost_ment_file["mentions"]
    position = roster_file["Pos"]
    race = roster_file["Race"]

    end_dict = {"Name":[], "Pos":[], "Race":[], "Mentions":[],
        "Positive comments":[], "Negative comments":[], "Net sentiment":[]}
    for name in mgmt_list:
        agg_ment = 0
        index_list = agg_rost_ment_file.index[agg_rost_ment_file[name] == 1].tolist()
        for row in index_list:
            agg_ment += ment[row]
        # Creates a single entry list.
        index_name = roster_file.index[roster_file["Player"] == name].tolist()
        end_dict["Name"].append(name)
        end_dict["Pos"].append(position[index_name[0]])
        end_dict["Race"].append(race[index_name[0]])
        end_dict["Mentions"].append(agg_ment)
        pos_cmts = sent_dict[name][0]
        neg_cmts = sent_dict[name][1]
        end_dict["Positive comments"].append(pos_cmts)
        end_dict["Negative comments"].append(neg_cmts)
        end_dict["Net sentiment"].append(pos_cmts-neg_cmts)

    for key in end_dict:
        end_dict[key].append("") if key != "Name" else end_dict[key].append(result)
    df = pandas.DataFrame(end_dict)
    df.to_csv(r'/home/sebastianguo/Documents/Research/Teams/' + team +
        '/mgmt_and_race_by_game/' + str(global_ID) + '.csv', index=False)

def win_or_lose(game_thread_info_file, result_file, team_str, global_ID, team):
    """
    Function to see whether for a global ID or game, the inputted team won or lost.
    Returns a csv file titled game_result.csv with the data. To figure out the
    result of a game, look at a csv file containing games for a certain team, the
    dates, and the results. An inputted file containing global IDs and the dates
    of the thread post is then compared to the dates of the season games of a team.

    The function looks at both the date of the post and the opponent team. The
    opponent team check is necessary because post game threads are sometimes posted
    a date after the game and if a team plays two games in a row, it could mess up
    results. However, some global ID threads are not post game threads, so not
    every thread title has a basketball team name in it.

    Parameter game_thread_info_file: a csv file containing the Reddit thread
    titles, the corresponding global IDs of those threads, and the dates of the game.
    Precondition: must be a reader object and contain the headers "ID", "dt",
    and "title".

    Parameter result_file: a csv file containing the results of a team's season.
    Precondition: must be a reader object and contain the headers "Result", "Opponent",
    and "New Date" (the last header is formatted from the function format_date()).

    Parameter team_str: a string containing all NBA teams except "team".
    Precondition: must be a string.

    Parameter global_ID: a global ID that this function finds a game result for.
    Precondition: must be an integer greater than zero.

    Parameter team: the team for which you are trying to find the result of a game.
    Precondition: must be a string.
    """
    _assertion_win_or_lose(game_thread_info_file, result_file, team_str,
        global_ID, team)
    new_date = result_file["New Date"]
    opp_short = result_file["Opponent Shortened"]
    # Finds the row index for the global ID, store as one entry list
    id_row = game_thread_info_file.index[game_thread_info_file["ID"] == global_ID].tolist()
    thread_post_date = game_thread_info_file["dt"][id_row[0]]
    reg_ex = re.compile(team_str)
    reg_ex_list = reg_ex.findall(game_thread_info_file["title"][id_row[0]])
    while True:
        game_row = result_file.index[new_date == thread_post_date].tolist()
        # If there is no mention of a team in the thread title, assume the thread
        # is not a post game discussion
        if len(reg_ex_list) == 0:
            break
        try:
            game_ind = game_row[0] # If no row with the thread post date, subtract date.
            if opp_short[game_ind] not in reg_ex_list:
                thread_post_date = _subtract_date(thread_post_date)
            else:
                break
        except: # No game date matches with reddit thread post date
            thread_post_date = _subtract_date(thread_post_date)
    if len(reg_ex_list) == 0:
        return "N/A"
    else:
        game_result = result_file["Result"][game_ind]
    if game_result == "W":
        return "Win"
    elif game_result == "L":
        return "Lose"

def make_team_str(team_file, team):
    """
    A function to create a regular expression string containing all of the NBA
    basketball teams excluding the one passed in under the team parameter. This
    regex will be used in function win_or_lose().

    Parameter team_file: a file containing all 30 basketball teams in the NBA.
    Precondition: must be a csv reader object containing the header "Team".

    Parameter team: the team that the regex skips.
    Precondition: must be a string.
    """
    assertions.assert_team_file_format(team_file)
    assertions.assert_team(team)
    teams = team_file["Team"]
    reg_ex_str = ""
    for index in range(team_file.shape[0]):
        if teams[index] != team:
            reg_ex_str += teams[index] + "|"
    return reg_ex_str[:-1]

def find_management(roster_file):
    """
    Given a roster file, find the coaches, GMs, and owners of the team. Return
    a list of these people.

    Parameter roster_file: a reader object that contains information about player
    names and nicknames.
    Precondition: must be a DataFrame object created by the pandas module and
    contain the necessary headers.
    """
    assertions.assert_roster_file_format(roster_file)
    position = roster_file["Pos"]
    player = roster_file["Player"]

    mgmt_list = []
    important_people = ["Coach", "GM", "Owner", "President"]
    for index in range(roster_file.shape[0]):
        if position[index] in important_people:
            mgmt_list.append(player[index])
    return mgmt_list

def format_data(raw_result_file, team_file, team):
    """
    A file to take season data format the date column. The data from the website
    has dates in the form "Sun 10, 2019" This function turns it into the format
    MM/DD/YY.

    Parameter raw_result_file: a file for the team in the parameter. It contains
    information about the games the team it played, the scores, and the result.
    Precondition: must be a reader from the pandas module.

    Parameter team_file: a reader object that contains the names of the teams in
    the NBA.
    Precondition: must be a DataFrame reader object and contain the header 'team'.

    Parameter team: the team that the file raw_result_file is about.
    Precondition: must be a string.
    """
    assertions.assert_raw_result_file_format(raw_result_file)
    assertions.assert_team_file_format(team_file)
    assertions.assert_team(team)
    date = raw_result_file["Date"]
    num_games = len(raw_result_file["G"])
    append_list1 = []
    append_list2 = []
    for number in range(num_games):
        append_list1.append(raw_result_file["Opponent"][number].split()[-1])
        append_list2.append(_change_date(date[number]))

    raw_result_file["Opponent Shortened"] = append_list1
    raw_result_file["New Date"] = append_list2
    raw_result_file.to_csv(r'/home/sebastianguo/Documents/Research/Teams/' +
        team + '/csv_data/2019-2020_scores.csv', index=False)

def _subtract_date(thread_post_date):
    """
    Subtract the days from the date until a date is found that matches up with
    a game.
    """
    date_list = thread_post_date.split("/")
    month = int(date_list[0])
    day = int(date_list[1])
    year = int(date_list[2])
    if month == 1 and day == 1:
        month = 12
        day = 31
        year -= 1
    elif day == 1:
        day = 31
        month -= 1
    else:
        day -= 1
    return str(month) + "/" + str(day) + "/" + str(year)

def _change_date(date):
    """
    Helper function to change date format of the function format_data().
    The dates are given in the form "Day of week, Month, Day, Year" and the output
    date is in the form "Day/Month/Year".
    """
    # Have the first entry blank so indexing into month_list lines up with the
    # number of months
    month_list = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug",
        "Sep", "Oct", "Nov", "Dec"]
    date_list = date.split()
    # THE csv files dates are all formatted the same such that the index of the
    # month starts at five.
    return (str(month_list.index(date_list[1])) + "/" + str(date_list[2]) +
        "/" + str(date_list[3]))

def _assertion_coach_mentions_glob(global_ID, agg_rost_ment_file, roster_file,
    mgmt_list, sent_dict, result, team):
    """ Function to test assertions for coach_mentions_glob(). """
    assertions.assert_global_ID(global_ID)
    assertions.assert_agg_roster_ment_file_format(agg_rost_ment_file, roster_file)
    assertions.assert_roster_file_format(roster_file)
    assertions.assert_str_list(mgmt_list)
    assertions.assert_result(result)
    assertions.assert_team(team)

def _assertion_win_or_lose(game_thread_info_file, result_file, team_str,
    global_ID, team):
    """ Function to test assertions for win_or_lose(). """
    assertions.assert_game_thread_info_file_format(game_thread_info_file)
    assertions.assert_season_result_file_format(result_file)
    assertions.assert_team(team_str)
    assertions.assert_global_ID(global_ID)
    assertions.assert_team(team)
