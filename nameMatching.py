"""
Module to match named entities from csv files to players from the New York
Knicks roster.

Creator: Sebastian Guo
"""
import extraction_v2
import commentData
import pandas
import numpy
import csv

def findPlayerNames(playerNameFile):
    """
    Returns a list of strings of player names from a given csv file. The inputted
    csvfile must contain a column with the header "Player" or else the function
    returns a FormatError.

    Parameter playerNameFile: a reader object that contains information about players.
    Precondition: must be a DataFrame object created by the pandas module. It must
    contain the column "Player".
    """
    assert type(playerNameFile) == pandas.core.frame.DataFrame, \
        repr(playerNameFile) + " is not a csv reader object."
    try:
        players = playerNameFile["Player"]
    except:
        raise commentData.FormatError("The csv file does not contain the 'Player' header.")

    lst = []
    for index in range(playerNameFile.shape[0]):
        lst.append(players[index])
    return lst

def playerMentions(commentDataList, playerNameFile, playerList, team):
    """
    Creates a csv file based off of an inputted list of named entities. The csv file
    contains the total mentions of each named entity (names, places, organizations)
    in the commentDataList created by calling the method extractColData. The
    function extractColData from the extraction module creates a two-dimensional
    list with data about the named entity.

    The function also marks the player on the basketball team that the named entity
    corresponds to. playerNameFile contains data about the names of the basketball
    team and any associated nicknames.

    Parameter commentDataList: A list containing named entities and their types.
    Precondition: Must be a two-dimensional list with inner entities as lists.
    The inner entries can either be a list with four terms (global ID, local ID,
    named entity, category) or a list with two terms (global ID and local ID). If
    the inner list only has two terms, that means that the associated comment has
    no named entities and will not affect the aggregate list of this function.

    Parameter playerNameFile: a reader object that contains information about player
    names and nicknames.
    Precondition: must be a DataFrame object created by the pandas module.

    Parameter playerList: a list of strings with players to compare the csvfile to.
    Precondition: playerList must be a list with string entries.

    Parameter team: the basketball team the code is run on.
    Precondition: team is of type string
    """
    _assertionPlayerMentions(commentDataList, playerNameFile, playerList, team)

    totMent = {"named entity": [], "category": [], "mentions": []}
    for lst in commentDataList:
        if len(lst) == 4 and (lst[2] not in totMent["named entity"]):
            # If named entity not in list, add entity to dictionary
            totMent["named entity"].append(lst[2])
            totMent["category"].append(lst[3])
            totMent["mentions"].append(1)
        elif len(lst) == 4 and (lst[2] in totMent["named entity"]):
            # If named entity in list, increase mentions by one
            index = totMent["named entity"].index(lst[2])
            totMent["mentions"][index] += 1
    length = len(totMent["named entity"])
    for player in playerList:
        totMent[player] = [""] * length
    for index in range(length):
        name = _matchPlayer(playerNameFile, totMent["named entity"][index], _createList(playerNameFile, "Player"),
            _createList(playerNameFile, "first short"), _createList(playerNameFile, "last short"), _createList(playerNameFile, "nicknames"))
        if name != "":
            totMent[name][index] = 1
    df = pandas.DataFrame(totMent)
    df.to_csv(r'/home/sebastianguo/Documents/Research/Teams/' + team + '/aggRosterMentions.csv', index=False)

def playerMentionsGlob(gameFile, playerNameFile, playerList, team):
    """
    Creates a csv file based off an inputted list commentDataList. The outputted
    csv files contains, for a certain thread/game, the total mentions of each named
    entity and the player that corresponds to the named entity in playerList.
    This function is similar to playerMentions(), except it sorts the csv files
    by thread.

    Parameter gameFile: A csv file created from function createDataFrame().
    Precondition: Must contain the headers "global_ID", "local_ID" and "name" and
    "category". Must be a csv file reader object.

    Parameter playerNameFile: a reader object that contains information about player
    names and nicknames.
    Precondition: must be a DataFrame object created by the pandas module.

    Parameter playerList: A list of the players on the team.
    Precondition: Must be a list with entries as strings.

    Parameter team: the basketball team the code is run on.
    Precondition: team is of type string
    """
    _assertionPlayerMentionsGlob(gameFile, playerNameFile, playerList, team)
    try:
        glob = gameFile["global_ID"]
        loc = gameFile["local_ID"]
        name = gameFile["name"]
        cat = gameFile["category"]
    except:
        raise commentData.FormatError("The csv file does not contain the correct headers.")

    totMent = {"named entity": [], "category": [], "mentions": []}
    for index in range(gameFile.shape[0]):
        if not pandas.isnull(name[index]) and name[index] not in totMent["named entity"]:
            totMent["named entity"].append(name[index])
            totMent["category"].append(cat[index])
            totMent["mentions"].append(1)
        elif not pandas.isnull(name[index]) and name[index] in totMent["named entity"]:
            place = totMent["named entity"].index(name[index])
            totMent["mentions"][place] += 1
    length = len(totMent["named entity"])
    for player in playerList:
        totMent[player] = [""] * length
    for number in range(length):
        name = _matchPlayer(playerNameFile, totMent["named entity"][number], _createList(playerNameFile, "Player"), _createList(playerNameFile, "first short"), _createList(playerNameFile, "last short"), _createList(playerNameFile, "nicknames"))
        if name != "":
            totMent[name][number] = 1
    df = pandas.DataFrame(totMent)
    df.to_csv(r'/home/sebastianguo/Documents/Research/Teams/' + team + '/aggRosterMentionsByGame/' + str(glob[0]) + '.csv', index=False)

def commentPlayers(rawDataFile, playerNameFile, playerList, commentDataList, team):
    """
    Create a csv file that contains individual comments and their unique global
    and local identifiers, plus columns that mark whether or not the comment
    has a mention of a player on the New York Knicks.

    The file with the raw scrapped data must be formatted as following:
    If one of the column names does not exist, an exception is returned. If the
    columns have headers but they are not in the first row, return an exception.
    If two columns exist with the same header, the function only looks at the
    column with the smallest index and should still return true provided all three
    headers exist. The global_ID and localI_ID column must have integer types.

    Parameter rawDataFile: the file that contains the raw scrapped data.
    Precondition: must be a reader object from the pandas module. It must contain
    the three column headers global_ID, local_ID and comment.

    Parameter playerNameFile: a reader object that contains information about player
    names and nicknames.
    Precondition: must be a DataFrame object created by the pandas module.

    Parameter playerList: a list of strings with players to compare the csvfile to.
    Precondition: playerList must be a list with string entries.

    Parameter commentDataList: A list containing named entities and their types.
    Precondition: Must be a two-dimensional list with inner entities as lists.
    The inner entries can either be a list with four terms (global ID, local ID,
    named entity, category) or a list with two terms (global ID and local ID).

    Parameter team: the basketball team the code is run on.
    Precondition: team is of type string
    """
    _assertionCommentPlayers(rawDataFile, playerNameFile, playerList, commentDataList, team)
    aggDict = {}
    aggDict["global_ID"] = rawDataFile["global_ID"]
    aggDict["local_ID"] = rawDataFile["local_ID"]
    aggDict["comment"] = rawDataFile["comment"]
    length = len(rawDataFile["global_ID"])
    for player in playerList:
        aggDict[player] = [""] * length

    nameList = _createList(playerNameFile, "Player")
    listFSho = _createList(playerNameFile, "first short")
    listLSho = _createList(playerNameFile, "last short")
    listNick = _createList(playerNameFile, "nicknames")
    for index in range(len(aggDict["global_ID"])):
        aggDict = _addPlayerMentions(aggDict, playerNameFile, index, aggDict["global_ID"][index],
            aggDict["local_ID"][index], commentDataList, nameList, listFSho, listLSho, listNick)
    df = pandas.DataFrame(aggDict)
    df.to_csv(r'/home/sebastianguo/Documents/Research/Teams/' + team + '/commentRosterMentions.csv', index=False)

def commentPlayersGlob(commentFile, playerList, global_ID, team):
    """
    A function to create separate csv files sorted by global ID or different games.
    Each csv file contains information similar to the csv file created by
    commentPlayers with comments and a matrix showing whether the comment contains
    a mention of a player name. The format of commentFile should contain the headers
    "global_ID", "local_ID", "comment", and the players from playerList. The
    function nameMatching.commentPlayers should ensure that these headers exist.

    Paramter commentFile: a file created by commentPlayers.
    Precondition: commentFile is a csv reader object.

    Parameter playerList: a list of strings with players to compare the csvfile to.
    Precondition: playerList must be a list with string entries.

    Parameter global_ID: the global ID which all of the comments outputted by this
    function must have.
    Precondition: global_ID is an integer greater than zero.

    Parameter team: the basketball team the code is run on.
    Precondition: team is of type string
    """
    assert type(commentFile) == pandas.core.frame.DataFrame, \
        repr(commentFile) + " is not a reader object."
    assert type(playerList) == list, repr(playerList) + " is not a list."
    for term in playerList:
        assert type(term) == str, repr(term) + " is not a string."
    assert type(global_ID) == int and global_ID > 0, repr(global_ID) + " is not an int greater than zero."
    assert type(team) == str, repr(team) + " is not a string."

    dfDict = {"global_ID":[], "local_ID":[], "comment":[]}
    glob = commentFile["global_ID"]
    loc = commentFile["local_ID"]
    comm = commentFile["comment"]
    playerMatrix = _createMatrix(numpy.empty((0, len(commentFile)), int), commentFile, playerList)

    indexList = []
    for index in range(commentFile.shape[0]):
        if glob[index] == global_ID:
            dfDict["global_ID"].append(glob[index])
            dfDict["local_ID"].append(loc[index])
            dfDict["comment"].append(comm[index])
            indexList.append(index)
    for columnInd in range(len(playerMatrix)):
        dfDict[playerList[columnInd]] = []
        for rowInd in indexList:
            dfDict[playerList[columnInd]].append(playerMatrix[columnInd][rowInd])
    df = pandas.DataFrame(dfDict)
    df.to_csv(r'/home/sebastianguo/Documents/Research/Teams/' + team + '/commentRosterMentionsByGame/' + str(global_ID) + ".csv", index=False)

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

def _matchPlayer(playerNameFile, namedEntity, nameList, listFSho, listLSho, listNick): #should be a private function
    """
    Returns, if any, the player that the nameEntity refers to in a csvfile.
    containing columns with full names, first and last names, and their
    associated nicknames. If there is no mention of a player that is associated
    with namedEntity, return an empty string.
    """
    try:
        fullNames = playerNameFile["Player"]
        first = playerNameFile["first"]
        last = playerNameFile["last"]
        playerNameFile["nicknames"]
        playerNameFile["first short"]
        playerNameFile["last short"]
    except:
        raise commentData.FormatError("The csv file does not contain the correct headers.")

    player = ""
    for index in range(playerNameFile.shape[0]):
        totalLst = [listFSho[index], listLSho[index], listNick[index]]
        if namedEntity == fullNames[index] or namedEntity == first[index] or namedEntity == last[index]:
            player = nameList[index]
            break
        for entry in totalLst:
            if namedEntity in entry:
                player = nameList[index]
    return player

def _createList(playerNameFile, colName):
    """
    Returns and creates a two-dimensional list according to the column name
    passed in as a parameter. Used for creating a list of nicknames, shortened
    first or last names. The reason a list is being created is for easier indexing
    into rows later on in the function matchPlayer.
    Some players might have multiple nicknames or shortened names.

    Parameter playerNameFile: playerNameFile is the csv file contianing the column colName.
    Precondition: must be a reader object from the pandas module.
    Paramter colName: the name of the column in nameFile to create the list for.
    Precondition: must be a string
    """
    assert type(playerNameFile) == pandas.core.frame.DataFrame, \
        repr(playerNameFile) + " is not a reader object."
    assert type(colName) == str, repr(colName) + " is not a string."

    items = playerNameFile[colName]
    returnList = []
    for index in range(playerNameFile.shape[0]):
        # If a box is empty in the csv file, the type of that box is float
        if pandas.isnull(items[index]):
            returnList.append("")
        elif "," in items[index]:
            lstNames = items[index].split(",")
            # Add a list into returnList if a player has multiple names
            returnList.append(lstNames)
        else:
            returnList += items[index].split(",")
    return returnList

def _addPlayerMentions(dfDictionary, playerNameFile, index, glob, loc, commentDataList, nameList, listFSho, listLSho, listNick):
    """
    Add to the dfdictionary any player mentions.
    """
    for entity in commentDataList:
        name = ''
        if len(entity) == 4 and entity[0] == glob and entity[1] == loc:
            name = _matchPlayer(playerNameFile, entity[2], nameList, listFSho, listLSho, listNick)
        if name != '':
            for key in dfDictionary:
                dfDictionary[name][index] = "1"
    return dfDictionary

def _assertionPlayerMentions(commentDataList, playerNameFile, playerList, team):
    """
    Function to test assertions for function playerMentions.
    """
    assert type(commentDataList) == list, repr(commentDataList) + " is not a list."
    for term in commentDataList:
        assert type(term) == list, repr(term) + " is not a list."
        assert len(term) == 2 or len(term) == 4, repr(term) + " is not of correct length."
    assert type(playerNameFile) == pandas.core.frame.DataFrame, \
        repr(playerNameFile) + " is not a csv reader object."
    assert type(playerList) == list, repr(playerList) + " is not a list."
    for term in playerList:
        assert type(term) == str, repr(term) + " is not a string."
    assert type(team) == str, repr(team) + " is not a string."

def _assertionCommentPlayers(rawDataFile, playerNameFile, playerList, commentDataList, team):
    """
    Function to test assertions for function commentPlayers.
    """
    assert type(rawDataFile) == pandas.core.frame.DataFrame, \
        repr(rawDataFile) + " is not a csv reader object."
    if not extraction_v2.checkColIndices(rawDataFile):
        raise commentData.FormatError("The csv file is either incorrectly formatted or a column header is missing.")
    if (rawDataFile["global_ID"].dtypes != int or rawDataFile["local_ID"].dtypes != int):
        raise TypeError("The types of the columns are incorrect.")
    assert type(playerNameFile) == pandas.core.frame.DataFrame, \
        repr(playerNameFile) + " is not a csv reader object."
    assert type(playerList) == list, repr(playerList) + " is not a list."
    for term in playerList:
        assert type(term) == str, repr(term) + " is not a string."
    assert type(commentDataList) == list, repr(commentDataList) + " is not a list."
    for term in commentDataList:
        assert type(term) == list, repr(term) + " is not a list."
        assert len(term) == 2 or len(term) == 4, repr(term) + " is not of correct length."
    assert type(team) == str, repr(team) + " is not a string."

def _assertionPlayerMentionsGlob(gameFile, playerNameFile, playerList, team):
    """
    Function to test assertions for function playerMentionsGlob.
    """
    assert type(gameFile) == pandas.core.frame.DataFrame, \
        repr(totalFile) + " is not a csv reader object."
    assert type(playerNameFile) == pandas.core.frame.DataFrame, \
        repr(playerNameFile) + " is not a csv reader object."
    assert type(playerList) == list, repr(playerList) + " is not of type list."
    for term in playerList:
        assert type(term) == str, repr(term) + " is not a string."
    assert type(team) == str, repr(team) + " is not a string."
