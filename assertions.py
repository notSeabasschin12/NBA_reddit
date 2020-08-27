"""
Module containing the classes and functions meant to raise errors as well as
assertion statements for commonly used function parameters and other checking functions.

Creator: Sebastian Guo
"""
import pandas, numpy
from nltk import NaiveBayesClassifier

class FormatError(Exception):
    """
    A class with an exception to be thrown when an inputted csv file is not
    formatted correctly.
    """
    pass

def assert_global_ID(global_ID):
    """ Assert: global_ID is of type integer and is greater than zero. """
    assert type(global_ID) == int, repr(global_ID) + " is not of type integer."
    assert global_ID > 0, repr(global_ID) + " is not greater than zero."

def assert_cmt_data_list(cmt_data_list):
    """
    Assert: cmt_data_list is of type list and contains as entries lists that have
    either two or four terms.
    """
    assert type(cmt_data_list) == list, "The inputted attribute is not of type list."
    for term in cmt_data_list:
        assert type(term) == list, "The one-dimensional entries in cmt_data_list are not lists."
        assert len(term) == 2 or len(term) == 4, "The inner lists are not of correct length."

def assert_str_list(input_list):
    """ Assert: a inputted attribute is of type list and has string entries. """
    assert type(input_list) == list, repr(input_list) + " is not a list."
    for term in input_list:
        assert type(term) == str, repr(term) + " is not a string."

def assert_int_list(input_list):
    """ Assert: a inputted attribute is of type list and has integer entries. """
    assert type(input_list) == list, repr(input_list) + " is not a list."
    for term in input_list:
        assert type(term) == int, repr(term) + " is not an integer."

def assert_result(result):
    """ Assert: type is string and is either "Win", "Lose", or "N/A". """
    assert type(result) == str, repr(result) + " is not of type string."
    assert result in ["Win", "Lose", "N/A"], \
        repr(result) + " is not one of three correct strings."

def assert_team(team):
    """ Assert: team is of type string. """
    assert type(team) == str, repr(team) + " is not a string."

def assert_type_df(df_reader):
    """ Assert: df_reader is a pandas DataFrame object. """
    assert type(df_reader) == pandas.DataFrame, repr(df_reader) + " is not a DataFrame object."

def assert_raw_data_file_format(raw_data_file):
    """
    Asserts the file contains the column names global_ID, local_ID, and
    comment. If one of the column names does not exist, the function returns false.
    If two columns exist with the same header, the function only looks at the
    column with the smallest index and should still return true provided all
    three headers exist. It also asserts that the types of columns global and local
    ID are integers.

    Parameter raw_data_file: the reader with the file that you want
    to extract the data of the column numbers from.
    Precondition: must be a DataFrame object from the pandas python module.
    """
    assert_type_df(raw_data_file)
    try:
        raw_data_file["global_ID"]
        raw_data_file["local_ID"]
        raw_data_file["comment"]
    except:
        raise AssertionError("The column headers for the file do not exist or are incorrectly formatted.")
    assert raw_data_file["global_ID"].dtypes == int and raw_data_file["local_ID"].dtypes == int, \
        "The columns global and local ID do not contain integers."

def assert_roster_file_format(roster_file):
    """ Asserts the file contains the correct column names. """
    assert_type_df(roster_file)
    try:
        roster_file["Player"]
        roster_file["Nicknames"]
        roster_file["First"]
        roster_file["Last"]
        roster_file["First Short"]
        roster_file["Last Short"]
        roster_file["Pos"]
        roster_file["Race"]
    except:
        raise AssertionError("The column headers for roster_file are incorrect.")

def assert_word_removal_file_format(word_removal_file, team):
    """ Asserts the file contains the column with parameter team as a header. """
    try:
        for row in range(word_removal_file.shape[0]):
            assert type(word_removal_file[team][row]) == str
    except:
        raise AssertionError("The columns do not have the correct types.")


def assert_roster_ment_by_game_file_format(game_file):
    """ Assert that game_file is a DataFrame and contains the correct columns. """
    assert_type_df(game_file)
    try:
        game_file["global_ID"]
        game_file["local_ID"]
        game_file["name"]
        game_file["category"]
    except:
        raise AssertionError("The column headers for game_file are incorrect.")

def assert_agg_roster_ment_file_format(game_file, roster_file):
    """
    Assert that game_file, a csv file created by function roster_mentions_glob()
    has the correct columns and is a DataFrame.
    """
    assert_type_df(game_file)
    try:
        game_file["named entity"]
        game_file["category"]
        game_file["mentions"]
        for player in roster_file["Player"]:
            game_file[player]
    except:
        raise AssertionError("The game_file does not contain the correct headers.")

def assert_cmt_lvl_ment_file_format(cmt_lvl_ment_file, roster_list):
    """ Assert file is a DataFrame and contains the correct headers. """
    assert_raw_data_file_format(cmt_lvl_ment_file)
    try:
        cmt_lvl_ment_file["global_ID"]
        cmt_lvl_ment_file["local_ID"]
        cmt_lvl_ment_file["comment"]
        for player in roster_list:
            cmt_lvl_ment_file[player]
    except:
        raise AssertionError("The headers of the file are incorrectly formatted.")

def assert_game_thread_info_file_format(game_thread_info_file):
    """ Assert that file has correct headers and is a DataFrame. """
    assert_type_df(game_thread_info_file)
    try:
        game_thread_info_file["dt"]
        game_thread_info_file["ID"]
        game_thread_info_file["title"]
    except:
        raise AssertionError("The file does not contain the correct headers.")

def assert_season_result_file_format(season_result_file):
    """ Assert the file is a DataFrame and has the correct headers. """
    assert_type_df(season_result_file)
    try:
        season_result_file["Result"]
        season_result_file["Opponent Shortened"]
        season_result_file["New Date"]
    except:
        raise AssertionError("The file does not contain the correct headers.")

def assert_raw_result_file_format(raw_result_file):
    """ Assert the file is a DataFrame and has the correct headers. """
    assert_type_df(raw_result_file)
    try:
        raw_result_file["Date"]
        raw_result_file["G"]
        raw_result_file["Opponent"]
    except:
        raise AssertionError("The file does not contain the correct headers.")

def assert_team_file_format(team_file):
    """ Assert the file is a DataFrame and has the correct team header."""
    assert_type_df(team_file)
    try:
        team_file["Team"]
    except:
        raise AssertionError("The file does not contain the correct headers.")

def assert_mgmt_and_race_file_format(mgmt_and_race_file, mgmt_list):
    """ Assert the file is a DataFrame object and has the correct headers. """
    assert_type_df(mgmt_and_race_file)
    try:
        players = mgmt_and_race_file["Name"]
        for row_ind in range(len(mgmt_list)):
            players[row_ind]
        mgmt_and_race_file["Race"]
        mgmt_and_race_file["Positive comments"]
        mgmt_and_race_file["Negative comments"]
        mgmt_and_race_file["Net sentiment"]
    except:
        raise AssertionError("The file does not contain the correct headers.")

def assert_mgmt_stat_file_format(mgmt_stat_file):
    """
    Assert the file is a DataFrame object and has the correct headers. It also
    ensures the columns are formatted correctly
    """
    assert_type_df(mgmt_stat_file)
    try:
        headers = mgmt_stat_file["Statistic Per Game Won or Lost (Per Coach)"]
        mgmt_stat_file["Win"]
        mgmt_stat_file["Loss"]
        assert headers[0] == "Manager Average Net Sentiment Per Game"
        assert headers[3] == "Manager Average Positive Comments Per Game"
        assert headers[6] == "Manager Average Negative Comments Per Game"
        assert headers[9] == "Manager Average Mentions Per Game"
        for row in range(mgmt_stat_file.shape[0]):
            if row in [0, 3, 6, 9]: # Correspond to empty rows in file
                assert pandas.isnull(mgmt_stat_file["Win"][row])
                assert pandas.isnull(mgmt_stat_file["Loss"][row])
            else:
                assert type(mgmt_stat_file["Win"][row]) == numpy.float64
                assert type(mgmt_stat_file["Loss"][row]) == numpy.float64
    except:
        raise AssertionError("The file does not contain correct headers.")

def assert_compare_machine_hand(machine_code_file, ground_truth_file):
    """
    Asserts the file machine_code and hand_code have the same column headers and
    the same global, local ID, and comment columns.
    """
    assert_type_df(machine_code_file)
    assert_type_df(ground_truth_file)

    assert machine_code_file["global_ID"].equals(ground_truth_file["global_ID"]), \
        "machine_code_file and ground_truth_file column 'global_ID' are not the same."
    assert machine_code_file["local_ID"].equals(ground_truth_file["local_ID"]), \
        "machine_code_file and ground_truth_file column 'local_ID' are not the same."
    assert machine_code_file["comment"].equals(ground_truth_file["comment"]), \
        "machine_code_file and ground_truth_file column 'comment' are not the same."
    assert machine_code_file.columns.tolist() == ground_truth_file.columns.tolist(), \
        "The headers of the two files do not match up."

def assert_classifier(classifier):
    """ Assert classifier is a Naive Bayes Classifier object. """
    assert type(classifier) == NaiveBayesClassifier, \
        "The classifier is not a Naive Bayes Classifier object."
