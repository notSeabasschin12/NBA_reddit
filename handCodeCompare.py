"""
Module to check the accuracy of csv files created in module nameMatching and extraction_v2
according to provided hand code.

Creator: Sebastian Guo
"""
import pandas
import numpy


def compareFiles(machineCodeFile, groundTruthFile, playerList, team):
    """
    Compare the machineCodeFile created by nameMatching function commentPlayers
    to a generated file groundTruthFile to look at the accuracy of commentFile.
    Calculates the precision and recall of the columns of player mentions for each
    comment and the total precision/recall. Then modify the csv file commentMentions
    by adding rows at the end of the file with total recall/prec and recall/prec
    for each column. If the recall/prec is "null", that means that due to a divide
    by zero error in calculations, the recall/prec was uncalculable.

    To compare the accuracy, the function creates matrices of each file and adds/
    subtracts them. If an entry has a 2, then the mention of the player in the
    comment is a true positive. When subtracting the matrices, a value of -1
    corresponds to a false positive (the ground truth code doesn't have the player mention
    but the machine code does.) A value of +1 is a false negative (the ground truth
    code has a player mention but the machine code does not.)

    Parameter machineCodeFile: a csv file containing individual comments and marks
    for whether or not each comment contains a mention of a player
    Precondition: must be a DataFrame object from the pandas module.

    Parameter groundTruthFile: a csv file contaniing individual comments
    Precondition: must be a DataFrame object from the pandas module. The columns
    global_ID, local_ID, and comment must be the same as commentFile.

    Parameter playerList: a list of strings with players to compare the csvfile to.
    Precondition: playerList must be a list with string entries.

    Parameter team: the basketball team the code is run on.
    Precondition: team is of type string
    """
    _assertionCompareFiles(machineCodeFile, groundTruthFile, playerList, team)
    matrixOne = _createMatrix(numpy.empty((0, len(machineCodeFile)), int), machineCodeFile, playerList)
    matrixTwo = _createMatrix(numpy.empty((0, len(machineCodeFile)), int), groundTruthFile, playerList)
    matrixDiff = numpy.subtract(matrixTwo, matrixOne)
    matrixSum = numpy.add(matrixOne, matrixTwo)

    appendDict = {"global_ID":["True Positives", "False Positives", "False Negatives", "Precision", "Recall"],
        "local_ID":[""] * 5, "rand_ID":[""] * 5, "comment":[]}

    _addValues(appendDict, matrixSum, matrixDiff, playerList)
    df = pandas.DataFrame(appendDict)
    df2 = groundTruthFile.append(df, ignore_index=True)
    df2.to_csv(r'/home/sebastianguo/Documents/Research/Teams/' + team + '/precisionAndRecall.csv', index=False)

def _addValues(dictionary, matrixSum, matrixDiff, playerList):
    """
    Takes in a rowArray and modifies it to add either the recall or precision of
    the columns corresponding to mentions of players. The matrix with the values
    -1, 0, 1, and 2 is in column major order.
    """
    aggTruePos = 0
    aggFalPos = 0
    aggFalNeg = 0
    for index in range(len(playerList)):
        player = playerList[index]
        colTruePos = numpy.count_nonzero(matrixSum[index] == 2)
        colFalPos = numpy.count_nonzero(matrixDiff[index] == -1)
        colFalNeg = numpy.count_nonzero(matrixDiff[index] == 1)
        dictionary[player] = [colTruePos, colFalPos, colFalNeg]
        try:
            dictionary[player] += [colTruePos/(colTruePos + colFalPos)]
        except:
            dictionary[player] += ["null"]
        try:
            dictionary[player] += [colTruePos/(colTruePos + colFalNeg)]
        except:
            dictionary[player] += ["null"]
        aggTruePos += colTruePos
        aggFalPos += colFalPos
        aggFalNeg += colFalNeg
    dictionary["comment"] = [aggTruePos, aggFalPos, aggFalNeg]
    try:
        dictionary["comment"] += [aggTruePos/(aggTruePos + aggFalPos)]
    except:
        dictionary["comment"] += ["null"]
    try:
        dictionary["comment"] += [aggTruePos/(aggTruePos + aggFalNeg)]
    except:
        dictionary["comment"] += ["null"]

def _createMatrix(matrix, commentFile, playerList):
    """
    Create a two-dimensional matrix to represent whether or not a table of
    comments contain mentions of certain players in them. A "1" means that the
    comment does have a mention and a "0" means the comment doesn't. The matrix
    is in column major order.
    """
    for player in playerList:
        matrix = numpy.append(matrix, [commentFile[player]], axis=0)
    matrix = numpy.nan_to_num(matrix)
    return matrix

def _assertionCompareFiles(machineCodeFile, groundTruthFile, playerList, team):
    """
    Function to maintain assertions for function compareFiles.
    """
    assert type(machineCodeFile) == pandas.core.frame.DataFrame, \
        repr(machineCodeFile) + " is not a reader object."
    assert type(groundTruthFile) == pandas.core.frame.DataFrame, \
        repr(groundTruthFile) + " is not a reader object."
    assert machineCodeFile["global_ID"].equals(groundTruthFile["global_ID"]), \
        "commentFile and groundTruthFile column 'global_ID' are not the same."
    # assert machineCodeFile["local_ID"].equals(groundTruthFile["local_ID"]), \
    #     "commentFile and groundTruthFile column 'local_ID' are not the same."
    assert machineCodeFile["comment"].equals(groundTruthFile["comment"]), \
        "commentFile and groundTruthFile column 'comment' are not the same."
    assert type(playerList) == list, repr(playerList) + " is not a list."
    for term in playerList:
        assert type(term) == str, repr(term) + " is not a string."
    assert type(team) == str, repr(team) + " is not a string."
