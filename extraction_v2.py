"""
Module that extracts data from scrapped csv files WITHOUT using the allenNLP.
"""
import pandas
import re
import string
import commentData
import nameMatching

def createDataFrame(globalID, twoDList):
    """
    Returns a csv file after making a DataFrame object with four columns: global_ID,
    local_ID, name, and the category. Using the global ID attribute, all of the
    rows in the DataFrame should have the same global ID.

    Parameter globalID: the global ID corresponding to a Reddit thread. For this
    specific global ID, extract the data from the 2DList.
    Precondition: must be an integer greater than zero.

    Parameter twoDList: a two-dimensional list that has as one of these two entries:
    1) a list of the form [global ID, local ID, name, category]
    3) [global ID, local ID] - if the comment corresponding to a global/local ID has no named
    entities.
    """
    assert type(globalID) == int and globalID > 0, repr(globalID) + " is not an int greater than zero."
    assert type(twoDList) == list, repr(twoDList) + " is not a 2D list."
    for term in twoDList:
        assert type(term) == list and (len(term) == 2 or len(term) == 4), \
            repr(term) + " is not a list or does not contain the correct terms."
    dict = {"global_ID":[], "local_ID":[], "name":[], "category":[]}
    for lst in twoDList:
        # if the comment has less than 2 characters or has no named entities, add
        # an the global and local ID, but no named entity or category.
        if (len(lst) == 2 and globalID == lst[0]):
            dict["global_ID"].append(globalID)
            dict["local_ID"].append(lst[1])
            dict["name"].append("")
            dict["category"].append("")
        elif (len(lst) == 4 and globalID == lst[0]):
            dict["global_ID"].append(globalID)
            dict["local_ID"].append(lst[1])
            dict["name"].append(lst[2])
            dict["category"].append(lst[3])
    df = pandas.DataFrame(dict)
    df.to_csv(r'/home/sebastianguo/Documents/Research/csv-files/' + str(globalID) + ".csv", index=False)

def extractColData(rawDataFile, playerNameFile):
    """
    Returns a two dimensional list. Each inner list corresponds to a named entity,
    its category (person, place, nickname) with its associated global and local ID. All
    global_IDs and local_IDs must be integers. Comments can be of any category, but
    will be cast into strings. The function also checks if the comments have
    nicknames as named entities.

    If the raw data file does not have columns global_ID, local_ID, and comment, raise an
    FormatError. If the raw data file has headers but they are not in the first row,
    raise a FormatError as well.

    If the types of the columns are incorrect, raise a TypeError. To check
    the types, the pandas module has a method dtypes. For a column with multiple
    types, calling the dtypes method returns object.

    Assume that for every global_ID and local_ID, there is an associated comment
    in that row. This means that the the number of elements in each of the
    three columns is the same. If the function fails to extract the data in any
    way, raise an exception.

    The order of the three columns in rawDataFile does not matter. The function will
    rearrange the 2D list order to make the keys go "global_ID", "local_ID", and
    "named entity/category".

    Parameter rawDataFile: the reader object with the csvfile that you want
    to extract the data from.
    Precondition: must be a DataFrame object created from the pandas module

    Parameter playerNameFile: the reader object containing nicknames to check for in
    the comments.

    Precondition: must be a DataFrame object created from the pandas module
    """
    _assertionExtractColData(rawDataFile, playerNameFile)
    globID = rawDataFile["global_ID"]
    locID = rawDataFile["local_ID"]
    comm = rawDataFile["comment"]
    twoDList = []
    # every comment is unique in its glob/loc ID. Maintain list of past IDs to
    # prevent having duplicate comments.
    duplicates = []

    # call createList here to prevent redundacy
    shortF = _createList(playerNameFile, "first short")
    lastF = _createList(playerNameFile, "last short")
    nameStr = _makeNameStr(playerNameFile["Player"], playerNameFile["first"], playerNameFile["last"])
    nicknameStr = _makeNicknameStr(_createList(playerNameFile, "nicknames"))
    total = 0
    for index in range(rawDataFile.shape[0]):
        if [globID[index], locID[index]] not in duplicates:
            try:
                _extractEntities(twoDList, globID[index], locID[index], comm[index],
                    nameStr, nicknameStr, shortF, lastF, total)
            except:
                raise Exception("Failed to create 2D list of named entities.")
        duplicates.append([globID[index], locID[index]])
        # print(index)
    return twoDList

def _extractEntities(lst, glob, loc, comment, nameStr, nicknameStr, shortFList, shortLList, total):
    """
    Returns a 2D list with 1D lists as named entities/categories(person, place, etc.).
    If the comment contains no named entities, return [global ID, local ID]. Function
    ignores case (frank vs. Frank) and stores possesive nouns with apostrophes
    removed (Frank's/Franks become Frank and frank also becomes Frank in the 2D list).

    playerNameFile is the file with the basketball players full names, and shortened
    ones.
    """
    _findName(lst, glob, loc, comment, nameStr, total)
    _findShortName(lst, glob, loc, comment, shortFList, shortLList)
    _findNickname(lst, glob, loc, comment, nicknameStr, total)
    # Add something to the 2D list to signal that the comment has no named entities.
    if len(lst) == 0:
        lst.append([glob, loc])
    elif lst[-1][0] != glob and lst[-1][1] != loc:
        lst.append([glob, loc])
    return lst

def _findName(lst, glob, loc, comment, nameStr, total): #instead of looping through each row in players, make one big, same, regex for each comment (don't make so many regex objects then). Also, this string passed into regex is same for each comment, so can only make that once.
    """
    Finds any names (full, first, and last) in the comment and adds to lst.
    """
    regExObj = re.compile(nameStr, re.IGNORECASE)
    regExList = regExObj.findall(comment)
    total += len(regExList)
    for entity in regExList:
        lst.append([glob, loc, string.capwords(entity), "U-PER"])
    return lst

def _findShortName(lst, glob, loc, comment, shortFList, shortLList):
    """
    Finds any shortened versions of the players names in a comment using regular
    expressions. While finding nicknames and full names uses regular expressions,
    shortened names are a little bit more tricky. For example, if you are looking
    for a nickname like "Rich" in the string "Richard", it'll still return a hit
    even though we are only looking for "Rich".
    """
    # for name in shortFList: # If this works, move for loop up to prevent redundacy and try same thing with _findName
    noPunc = re.sub(r'[^\w\s]','',comment).lower()
    commSplit = noPunc.split()
    for term1 in shortFList:
        countShort = commSplit.count(term1.lower()) + commSplit.count(term1.lower() + "s")
        while (countShort != 0):
            lst.append([glob, loc, term1, "U-PER"])
            countShort -= 1
    for term2 in shortLList:
        countLong = commSplit.count(term2.lower()) + commSplit.count(term2.lower() + "s")
        while (countLong != 0):
            lst.append([glob, loc, term2, "U-PER"])
            countLong -= 1
    return lst

def _findNickname(lst, glob, loc, comment, nicknameStr, total):
    """
    Checks and adds to list any mentions of named entities as nicknames. The
    function ignores case and adds a nickname with the first letters of the word
    capitalized even if the word within the comment has incorrect case.
    """
    regExObj = re.compile(nicknameStr, re.IGNORECASE)
    regExList = regExObj.findall(comment)
    total += len(regExList)
    for term in regExList:
        lst.append([glob, loc, string.capwords(term), "U-PER"])
    return lst

def _makeNameStr(fullName, firstName, lastName):
    """
    Make a string to input for the regular expression.
    """
    strRegEx = ''
    for termFull in fullName:
        strRegEx += termFull + "|"
    for termFirst in firstName:
        strRegEx += termFirst + "|"
    for termLast in lastName:
        strRegEx += termLast + "|"
    return strRegEx[:-1]

def _makeNicknameStr(nicknameList):
    """
    Make a regular expression string for nicknames.
    """
    strRegEx = ''
    for term in nicknameList:
        strRegEx += term + "|"
    return strRegEx[:-1]

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
        if type(items[index]) != float:
            lstNames = items[index].split(",")
            returnList += lstNames
    return returnList

def checkColIndices(rawDataFile):
    """
    Returns true is the file contains the column names global_ID, local_ID, and
    comment. If one of the column names does not exist, the function returns false.
    If the columns have headers but they are not in the first row, return false
    (to ensure proper formatting of the csv file). If two columns exist with the
    same header, the function only looks at the column with the smallest index
    and should still return true provided all three headers exist.

    Parameter rawDataFile: the reader with the file that you want
    to extract the data of the column numbers from.
    Precondition: must be a DataFrame object from the pandas python module.
    """
    assert type(rawDataFile) == pandas.core.frame.DataFrame, \
        repr(rawDataFile) + " is not a csv reader object."

    colNumDict = {}
    columns = rawDataFile.columns
    try:
        colNumDict["global_ID"] = columns.get_loc("global_ID")
        colNumDict["local_ID"] = columns.get_loc("local_ID")
        colNumDict["comment"] = columns.get_loc("comment")
    except:
        pass
    if len(colNumDict) == 3:
        return True
    else:
        return False

def getGlobalID(rawDataFile):
    """
    Returns a list of the global IDs in the scrapped data file. The global ID of a comment
    distinguishes it from comments in different threads (so two comments in the
    same thread have the same global ID).

    If the terms in the column don't have the correct type, raise a TypeError.

    Parameter rawDataFile: the reader object with the csvfile that you want
    to extract the global IDs from.
    Precondition: must be a DataFrame object created from the pandas module.
    """
    assert type(rawDataFile) == pandas.core.frame.DataFrame, \
        repr(rawDataFile) + " is not a csv reader object."

    try:
        col = rawDataFile["global_ID"]
    except:
        raise Exception("The csv file does not contain a global_ID header.")
    if (rawDataFile["global_ID"].dtypes != int):
        raise TypeError("The type of the column global_ID are not all integers.")
    globalIDList = []
    # add non-duplicate IDs to the globalIDList
    for item in col:
        if item not in globalIDList:
            globalIDList.append(item)
    return globalIDList

def _assertionExtractColData(rawDataFile, playerNameFile):
    """
    Assertions for function extractColData.
    """
    assert type(rawDataFile) == pandas.core.frame.DataFrame, \
        repr(rawDataFile) + " is not a csv reader object."
    assert type(playerNameFile) == pandas.core.frame.DataFrame, \
        repr(playerNameFile) + " is not a csv reader object."
    if not checkColIndices(rawDataFile):
        raise commentData.FormatError("The csv file is either incorrectly formatted or a column header is missing.")
    if (rawDataFile["global_ID"].dtypes != int or rawDataFile["local_ID"].dtypes != int):
        raise TypeError("The types of the columns are incorrect.")
    try:
        playerNameFile["nicknames"]
    except:
        raise Exception("The nickname file does not have the column 'nickname'.")
