"""
Module to match named entities from csv files to players from the New York
Knicks roster.

Creator: Sebastian Guo
Last modified: June 5 2020
"""
import extraction
import commentData
import pandas

def aggregate(commentDataList):
    """
    Creates a csv file based off of an inputted list of named entities. The csv file
    contains the total mentions of each named entity (names, places, organizations)
    in the commentDataList created  by calling the method extractColData. The
    function extractColData from the extraction module creates a two-dimensional
    list with data about the named entity.

    Parameter commentDataList: A list containing named entities and their types.
    Precondition: Must be a two-dimensional list with inner entities as lists.
    The inner entries can either be a list with four terms (global ID, local ID,
    named entity, category) or a list with two terms (global ID and local ID). If
    the inner list only has two terms, that means that the associated comment has
    no named entities and will not affect the aggregate list of this function.
    """
    assert type(commentDataList) == list, repr(commentDataList) + " is not a list."
    for term in commentDataList:
        assert type(term) == list, repr(term) + " is not a list."
        assert len(term) == 2 or len(term) == 4, repr(term) + " is not of correct length."

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
    df = pandas.DataFrame(totMent)
    df.to_csv(r'/home/sebastianguo/Documents/Research/data/total.csv', index=False)


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

def playerMentions(playerNameFile, playerList):
    """
    Creates a csv file that contains whether or not a named entity from the inputted
    csvfile refers to a player on the New York Knicks Basketball team. The
    inputted csvfile is one that is created from the method aggregate in the
    module nameMatching and contains the total mentions of a named entity. While
    the file created has the same three columns as the inputted csvfile, this
    function still creates a different csv file. Csvfile2 contains data about
    the names of the New York Knicks basketball team and any associated nicknames.

    If the csvfile does not contain the three necessary columns, return
    a FormatError.

    Parameter playerNameFile: a reader object that contains information about player
    names and nicknames.
    Precondition: must be a DataFrame object created by the pandas module.

    Parameter playerList: a list of strings with players to compare the csvfile to.
    Precondition: playerList must be a list with string entries.
    """
    assert type(playerNameFile) == pandas.core.frame.DataFrame, \
        repr(playerNameFile) + " is not a csv reader object."
    assert type(playerList) == list, repr(playerList) + " is not a list."
    for term in playerList:
        assert type(term) == str, repr(term) + " is not a string."
    with open("/home/sebastianguo/Documents/Research/data/total.csv", newline='') as csvfile:
        totalFile = pandas.read_csv(csvfile)
    try:
        names = totalFile["named entity"]
        cat = totalFile["category"]
        ment = totalFile["mentions"]
    except:
        raise commentData.FormatError("The csv file does not contain the correct headers.")

    endDict = {}
    endDict["named entity"] = names
    endDict["category"] = cat
    endDict["mentions"] = ment
    length = len(names)
    rowsStuff = []
    for player in playerList:
        endDict[player] = [""] * length
    for index in range(totalFile.shape[0]):
        name = _matchPlayer(playerNameFile, names[index])
        if name != "":
            endDict[name][index] = 1
            rowsStuff.append(index)


    df = pandas.DataFrame(endDict)
    for rowNum in rowsStuff:
        target_row = rowNum
        idx = [target_row] + [i for i in range(len(df)) if i != target_row]
        df = df.iloc[idx]
    df.to_csv(r'/home/sebastianguo/Documents/Research/data/mentions.csv', index=False)


def _matchPlayer(playerNameFile, namedEntity): #should be a private function
    """
    Returns, if any, the player that the nameEntity refers to in a csvfile.
    containing columns with full names, first and last names, and their
    associated nicknames. If there is no mention of a player that is associated
    with namedEntity, return an empty string.
    """
    try:
        fullNames = playerNameFile["Player"]
        nicknames = playerNameFile["nicknames"]
        first = playerNameFile["first"]
        last = playerNameFile["last"]
        firstShort = playerNameFile["first short"]
        lastShort = playerNameFile["last short"]
    except:
        raise commentData.FormatError("The csv file does not contain the correct headers.")

    nicknameList = createList(playerNameFile, "nicknames")
    fShortList = createList(playerNameFile, "first short")
    lShortList = createList(playerNameFile, "last short")

    player = ""
    for index in range(playerNameFile.shape[0]):
        totalLst = [nicknameList[index], fShortList[index], lShortList[index]]
        if first[index] == namedEntity.upper() or last[index] == namedEntity.upper():
            # check if full first or last name matches up. upper() ensures that
            # the function matches named entities regardless of letter case.
            player = fullNames[index]
        for entry in totalLst:
            if type(entry) == list:
                if namedEntity in entry:
                    player = fullNames[index]
            else:
                if entry == namedEntity:
                    player = fullNames[index]
    return player

def createList(playerNameFile, colName):
    """
    Returns and creates a two-dimensional list according to the column name
    passed in as a parameter. Used for creating a list of nicknames, shortened
    first or last names. The reason a list is being created is for easier indexing
    into rows later on in the function matchPlayer.

    Some players might have multiple nicknames or shortened names. When iterating
    through the csv file, the reader object returns a string similar to
    "name 1, name 2" if the player has multiple names. If a player does have
    multiple names, then the subsequent columns indicies will be shifted down one.
    So creating a list of the names where an inner list is created for a player
    with multiple nicknames prevents index errors.

    A similar thing can happen with names with multiple words (the multiple words
    might be seen as separate names and be assigned separate indices).

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
        if type(items[index]) == float:
            returnList.append("")
        elif "," in items[index]:
            lstNames = items[index].split(",")
            # Add a list into nicknameList if a player has multiple nicknames
            returnList.append(lstNames)
        else:
            lstNames = items[index].split(",")
            returnList += lstNames
    return returnList
