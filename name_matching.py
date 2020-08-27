"""
Module to match named entities from csv files to players from the New York
Knicks roster.

Creator: Sebastian Guo
"""
import extraction_v2, assertions
import pandas, numpy, csv

def find_roster_names(roster_file):
    """
    Returns a list of strings of player names from a given csv file. The inputted
    csvfile must contain a column with the header "Player" or else the function
    returns a FormatError.

    Parameter roster_file: a reader object that contains information about players.
    Precondition: must be a DataFrame object created by the pandas module. It must
    contain the column "Player".
    """
    assertions.assert_roster_file_format(roster_file)
    players = roster_file["Player"]
    lst = []
    for index in range(roster_file.shape[0]):
        lst.append(players[index])
    return lst

def roster_mentions(cmt_data_list, roster_file, roster_list, team):
    """
    Creates a csv file based off of an inputted list of named entities. The csv file
    contains the total mentions of each named entity (names, places, organizations)
    in the cmt_data_list created by calling the method extractColData. The
    function extract_col_data from the extraction module creates a two-dimensional
    list with data about the named entity.

    The function also marks the player on the basketball team that the named entity
    corresponds to. roster_file contains data about the names of the basketball
    team and any associated nicknames.

    Parameter cmt_data_list: A list containing named entities and their types.
    Precondition: Must be a two-dimensional list with inner entities as lists.
    The inner entries can either be a list with four terms (global ID, local ID,
    named entity, category) or a list with two terms (global ID and local ID). If
    the inner list only has two terms, that means that the associated comment has
    no named entities and will not affect the aggregate list of this function.

    Parameter roster_file: a reader object that contains information about player
    names and nicknames.
    Precondition: must be a DataFrame object created by the pandas module.

    Parameter roster_list: a list of strings with players to compare the csvfile to.
    Precondition: roster_list must be a list with string entries.

    Parameter team: the basketball team the code is run on.
    Precondition: team is of type string
    """
    _assertion_roster_mentions(cmt_data_list, roster_file, roster_list, team)
    tot_ment = {"named entity": [], "category": [], "mentions": []}
    for lst in cmt_data_list:
        if len(lst) == 4 and (lst[2] not in tot_ment["named entity"]):
            # If named entity not in list, add entity to dictionary
            tot_ment["named entity"].append(lst[2])
            tot_ment["category"].append(lst[3])
            tot_ment["mentions"].append(1)
        elif len(lst) == 4 and (lst[2] in tot_ment["named entity"]):
            # If named entity in list, increase mentions by one
            index = tot_ment["named entity"].index(lst[2])
            tot_ment["mentions"][index] += 1
    length = len(tot_ment["named entity"])
    for player in roster_list:
        tot_ment[player] = [""] * length
    for index in range(length): # Match named entities to players
        name = _match_roster(roster_file, tot_ment["named entity"][index])
        if name != "":
            tot_ment[name][index] = 1
    df = pandas.DataFrame(tot_ment)
    df.to_csv(r'/home/sebastianguo/Documents/Research/Teams/' + team +
        '/agg_roster_mentions.csv', index=False)

def roster_mentions_glob(global_ID, rost_ment_file, roster_file, roster_list, team):
    """
    Creates a csv file based off an inputted list cmt_data_list. The outputted
    csv files contains, for a certain thread/game, the total mentions of each named
    entity and the player that corresponds to the named entity in roster_list.
    This function is similar to roster_mentions(), except it sorts the csv files
    by thread.

    Parameter global_ID: the global ID that this function extracts data from.
    Precondition: must be an integer greater than zero.

    Parameter rost_ment_file: a csv file created by create_data_frame(). It
    contains individual mentions of people on a basketball roster for a global ID.
    Precondition: must be a DataFrame object with the correct headers.

    Parameter roster_file: a reader object that contains information about player
    names and nicknames.
    Precondition: must be a DataFrame object created by the pandas module.

    Parameter roster_list: A list of the players on the team.
    Precondition: Must be a list with entries as strings.

    Parameter team: the basketball team the code is run on.
    Precondition: team is of type string
    """
    _assertion_roster_mentions_glob(global_ID, rost_ment_file, roster_file, roster_list, team)

    name = rost_ment_file["name"]
    cat = rost_ment_file["category"]

    tot_ment = {"named entity": [], "category": [], "mentions": []}
    for index in range(rost_ment_file.shape[0]):
        # Does the same as roster_mentions(), except makes sure global ID is the same.
        if not pandas.isnull(name[index]) and name[index] not in tot_ment["named entity"]:
            tot_ment["named entity"].append(name[index])
            tot_ment["category"].append(cat[index])
            tot_ment["mentions"].append(1)
        elif not pandas.isnull(name[index]) and name[index] in tot_ment["named entity"]:
            place = tot_ment["named entity"].index(name[index])
            tot_ment["mentions"][place] += 1

    length = len(tot_ment["named entity"])
    for player in roster_list:
        tot_ment[player] = [""] * length
    for number in range(length): # Match named entities to players
        name = _match_roster(roster_file, tot_ment["named entity"][number])
        if name != "":
            tot_ment[name][number] = 1
    df = pandas.DataFrame(tot_ment)
    df.to_csv(r'/home/sebastianguo/Documents/Research/Teams/' + team +
        '/agg_roster_mentions_by_game/' + str(global_ID) + '.csv', index=False)

def comment_roster(raw_data_file, roster_file, roster_list, cmt_data_list, team):
    """
    Create a csv file that contains individual comments and their unique global
    and local identifiers, plus columns that mark whether or not the comment
    has a mention of a player on the New York Knicks.

    The file with the raw scrapped data must be formatted as following:
    If one of the column names does not exist, an exception is returned. If the
    columns have headers but they are not in the first row, return an exception.
    If two columns exist with the same header, the function only looks at the
    column with the smallest index and should still return true provided all three
    headers exist. The global_ID and local_ID column must have integer types.

    Parameter raw_data_file: the file that contains the raw scrapped data.
    Precondition: must be a reader object from the pandas module. It must contain
    the three column headers global_ID, local_ID and comment.

    Parameter roster_file: a reader object that contains information about player
    names and nicknames.
    Precondition: must be a DataFrame object created by the pandas module.

    Parameter roster_list: a list of strings with players to compare the csvfile to.
    Precondition: roster_list must be a list with string entries.

    Parameter cmt_data_list: A list containing named entities and their types.
    Precondition: Must be a two-dimensional list with inner entities as lists.
    The inner entries can either be a list with four terms (global ID, local ID,
    named entity, category) or a list with two terms (global ID and local ID).

    Parameter team: the basketball team the code is run on.
    Precondition: team is of type string
    """
    _assertion_comment_roster(raw_data_file, roster_file, roster_list, cmt_data_list, team)
    agg_dict = {}
    agg_dict["global_ID"] = raw_data_file["global_ID"]
    agg_dict["local_ID"] = raw_data_file["local_ID"]
    agg_dict["comment"] = raw_data_file["comment"]
    length = len(raw_data_file["global_ID"])
    for player in roster_list:
        agg_dict[player] = [""] * length

    for index in range(len(agg_dict["global_ID"])): # Find named entities for a comment.
        agg_dict = _add_roster_mentions(agg_dict, roster_file, index,
            agg_dict["global_ID"][index], agg_dict["local_ID"][index], cmt_data_list)
    df = pandas.DataFrame(agg_dict)
    df.to_csv(r'/home/sebastianguo/Documents/Research/Teams/' + team +
        '/cmt_lvl_roster_mentions.csv', index=False)

def comment_roster_glob(cmt_lvl_ment_file, roster_list, global_ID, team):
    """
    A function to create separate csv files sorted by global ID or different games.
    Each csv file contains information similar to the csv file created by
    commentPlayers with comments and a matrix showing whether the comment contains
    a mention of a player name. The format of cmt_lvl_ment_file should contain the headers
    "global_ID", "local_ID", "comment", and the players from roster_list. The
    function nameMatching.commentPlayers should ensure that these headers exist.

    Paramter cmt_lvl_ment_file: a file created by comment_roster().
    Precondition: cmt_lvl_ment_file is a csv reader object.

    Parameter roster_list: a list of strings with players to compare the csvfile to.
    Precondition: roster_list must be a list with string entries.

    Parameter global_ID: the global ID which all of the comments outputted by this
    function must have.
    Precondition: global_ID is an integer greater than zero.

    Parameter team: the basketball team the code is run on.
    Precondition: team is of type string
    """
    _assertion_comment_roster_glob(cmt_lvl_ment_file, roster_list, global_ID, team)
    agg_dict = {"global_ID":[], "local_ID":[], "comment":[]}
    glob = cmt_lvl_ment_file["global_ID"]
    loc = cmt_lvl_ment_file["local_ID"]
    comm = cmt_lvl_ment_file["comment"]
    player_matrix = _create_matrix(numpy.empty((0, len(cmt_lvl_ment_file)), int), cmt_lvl_ment_file, roster_list)

    index_list = []
    for index in range(cmt_lvl_ment_file.shape[0]):
        if glob[index] == global_ID:
            agg_dict["global_ID"].append(glob[index])
            agg_dict["local_ID"].append(loc[index])
            agg_dict["comment"].append(comm[index])
            index_list.append(index)
    for column_ind in range(len(player_matrix)):
        agg_dict[roster_list[column_ind]] = []
        for row_ind in index_list:
            agg_dict[roster_list[column_ind]].append(player_matrix[column_ind][row_ind])
    df = pandas.DataFrame(agg_dict)
    df.to_csv(r'/home/sebastianguo/Documents/Research/Teams/' + team +
        '/cmt_lvl_roster_mentions_by_game/' + str(global_ID) + ".csv", index=False)

def _create_matrix(matrix, cmt_lvl_ment_file, roster_list):
    """
    Create a two-dimensional matrix to represent whether or not a table of
    comments contain mentions of certain players in them. A "1" means that the
    comment does have a mention and a "0" means the comment doesn't. The matrix
    is in column major order.
    """
    for player in roster_list:
        matrix = numpy.append(matrix, [cmt_lvl_ment_file[player]], axis=0)
    return matrix

def _match_roster(roster_file, named_entity):
    """
    Returns, if any, the player that the nameEntity refers to in a csvfile.
    containing columns with full names, first and last names, and their
    associated nicknames. If there is no mention of a player that is associated
    with named_entity, return an empty string.
    """
    try:
        full_names = roster_file["Player"]
        first = roster_file["First"]
        last = roster_file["Last"]
        f_short = roster_file["First Short"]
        l_short = roster_file["Last Short"]
        nicknames = roster_file["Nicknames"]
    except:
        raise commentData.FormatError("The csv file does not contain the correct headers.")

    player = ""
    for index in range(roster_file.shape[0]):
        name_list = []
        if not pandas.isnull(f_short[index]):
            name_list += f_short[index].split(",")
        if not pandas.isnull(l_short[index]):
            name_list += l_short[index].split(",")
        if not pandas.isnull(nicknames[index]):
            name_list += nicknames[index].split(",")
        for term in name_list:
            if named_entity == term:
                player = full_names[index]
                break
        if not pandas.isnull(first[index]) and named_entity == first[index]:
            player = full_names[index]
            break
        elif not pandas.isnull(last[index]) and named_entity == last[index]:
            player = full_names[index]
            break
        elif named_entity == full_names[index]:
            player = full_names[index]
            break
    return player

def _add_roster_mentions(agg_dict, roster_file, index, global_ID, local_ID, cmt_data_list):
    """
    Add to the agg_dict any player mentions.
    """
    for entity in cmt_data_list:
        name = ''
        if len(entity) == 4 and entity[0] == global_ID and entity[1] == local_ID:
            name = _match_roster(roster_file, entity[2])
        if name != '':
            for key in agg_dict:
                agg_dict[name][index] = "1"
    return agg_dict

def _assertion_roster_mentions(cmt_data_list, roster_file, roster_list, team):
    """
    Function to test assertions for function roster_mentions().
    """
    assertions.assert_cmt_data_list(cmt_data_list)
    assertions.assert_roster_file_format(roster_file)
    assertions.assert_str_list(roster_list)
    assertions.assert_team(team)

def _assertion_comment_roster(raw_data_file, roster_file, roster_list,
    cmt_data_list, team):
    """
    Function to test assertions for function comment_roster().
    """
    assertions.assert_raw_data_file_format(raw_data_file)
    assertions.assert_roster_file_format(roster_file)
    assertions.assert_str_list(roster_list)
    assertions.assert_cmt_data_list(cmt_data_list)
    assertions.assert_team(team)

def _assertion_roster_mentions_glob(global_ID, rost_ment_file, roster_file,
    roster_list, team):
    """
    Function to test assertions for function roster_mentions_glob().
    """
    assertions.assert_global_ID(global_ID)
    assertions.assert_roster_ment_by_game_file_format(rost_ment_file)
    assertions.assert_roster_file_format(roster_file)
    assertions.assert_str_list(roster_list)
    assertions.assert_team(team)

def _assertion_comment_roster_glob(cmt_lvl_ment_file, roster_list, global_ID, team):
    """
    Function to test assertions for function coach_mentions_glob()
    """
    assertions.assert_cmt_lvl_ment_file_format(cmt_lvl_ment_file, roster_list)
    assertions.assert_str_list(roster_list)
    assertions.assert_global_ID(global_ID)
    assertions.assert_team(team)
