"""
Module to check the accuracy of csv files created in module name_matching and
extraction_v2 according to provided hand code.

Creator: Sebastian Guo
"""
import pandas, numpy
import assertions

def compare_files(machine_code_file, ground_truth_file, roster_list, team):
    """
    Compare the machine_code_file created by nameMatching function comment_players
    to a generated file ground_truth_file to look at the accuracy.
    Calculates the precision and recall of the columns of player mentions for each
    comment and the total precision/recall. Then modify the csv file comment_mentions
    by adding rows at the end of the file with total recall/prec and recall/prec
    for each column. If the recall/prec is "null", that means that due to a divide
    by zero error in calculations, the recall/prec was uncalculable.

    To compare the accuracy, the function creates matrices of each file and adds/
    subtracts them. If an entry has a 2, then the mention of the player in the
    comment is a true positive. When subtracting the matrices, a value of -1
    corresponds to a false positive (the ground truth code doesn't have the player
    mention but the machine code does.) A value of +1 is a false negative
    (the ground truth code has a player mention but the machine code does not.)

    Parameter machine_code_file: a csv file containing individual comments and
    marks for whether or not each comment contains a mention of a player
    Precondition: must be a DataFrame object from the pandas module.

    Parameter ground_truth_file: a csv file contaniing individual comments
    Precondition: must be a DataFrame object from the pandas module. The columns
    global_ID, local_ID, and comment must be the same as comment_file and contain
    the same player headers.

    Parameter roster_list: a list of strings with players to compare the csvfile to.
    Precondition: roster_list must be a list with string entries.

    Parameter team: the basketball team the code is run on.
    Precondition: team is of type string
    """
    assertions.assert_compare_machine_hand(machine_code_file, ground_truth_file)
    assertions.assert_str_list(roster_list)
    assertions.assert_team(team)
    length = len(machine_code_file)
    matrix_one = _create_matrix(numpy.empty((0, length), int), machine_code_file, roster_list)
    matrix_two = _create_matrix(numpy.empty((0, length), int), ground_truth_file, roster_list)
    matrix_diff = numpy.subtract(matrix_two, matrix_one)
    matrix_sum = numpy.add(matrix_one, matrix_two)
    appendDict = {"Calculations":["True Positives", "False Positives",
        "False Negatives", "Precision", "Recall", "Num. of comments"], "Total":[]}

    _add_values(appendDict, matrix_sum, matrix_diff, roster_list)
    df = pandas.DataFrame(appendDict)
    df.to_csv(r'/home/sebastianguo/Documents/Research/Teams/' + team +
        '/precision_and_recall.csv', index=False)

def _add_values(dictionary, matrix_sum, matrix_diff, roster_list):
    """
    Takes in a numpy array and modifies it to add either the recall or precision of
    the columns corresponding to mentions of players. The matrix with the values
    -1, 0, 1, and 2 is in column major order.
    """
    agg_true_pos = 0
    agg_fal_pos = 0
    agg_fal_neg = 0
    for index in range(len(roster_list)):
        player = roster_list[index]
        col_true_pos = numpy.count_nonzero(matrix_sum[index] == 2)
        col_fal_pos = numpy.count_nonzero(matrix_diff[index] == -1)
        col_fal_neg = numpy.count_nonzero(matrix_diff[index] == 1)
        dictionary[player] = [col_true_pos, col_fal_pos, col_fal_neg]
        try:
            dictionary[player] += [col_true_pos/(col_true_pos + col_fal_pos)]
        except:
            dictionary[player] += ["null"]
        try:
            dictionary[player] += [col_true_pos/(col_true_pos + col_fal_neg)]
        except:
            dictionary[player] += ["null"]
        agg_true_pos += col_true_pos
        agg_fal_pos += col_fal_pos
        agg_fal_neg += col_fal_neg
        dictionary[player].append("")
    dictionary["Total"] = [agg_true_pos, agg_fal_pos, agg_fal_neg]
    try:
        dictionary["Total"] += [agg_true_pos/(agg_true_pos + agg_fal_pos)]
    except:
        dictionary["Total"] += ["null"]
    try:
        dictionary["Total"] += [agg_true_pos/(agg_true_pos + agg_fal_neg)]
    except:
        dictionary["Total"] += ["null"]
    dictionary["Total"].append("")

def _create_matrix(matrix, comment_file, roster_list):
    """
    Create a two-dimensional matrix to represent whether or not a table of
    comments contain mentions of certain players in them. A "1" means that the
    comment does have a mention and a "0" means the comment doesn't. The matrix
    is in column major order.
    """
    for player in roster_list:
        matrix = numpy.append(matrix, [comment_file[player]], axis=0)
    matrix = numpy.nan_to_num(matrix)
    return matrix
