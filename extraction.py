"""
Module to extract names of players from an Excel spreadsheet.
Used the pandas module to input and read the spreadsheet containing Reddit
comment data.

Creator: Sebastian Guo
Last modified: June 5 2020
"""
from allennlp.predictors.predictor import Predictor
import allennlp_models.ner.crf_tagger
import pandas
import commentData
import nameMatching
import string

def createDataFrame(globalID, twoDList):
    """
    Returns a csv file after making a DataFrame object with four columns: global_ID,
    local_ID, name, and the category. Using the global ID attribute, all of the
    rows in the DataFrame should have the same global ID.

    Parameter globalID: the global ID corresponding to a Reddit thread. For this
    specific global ID, extract the data from the 2DList.
    Precondition: must be an integer greater than zero.

    Parameter twoDList: a two-dimensional list that has as one of these three entries:
    1) a list of the form [global ID, local ID, name, category]
    2) ["0-2 char"] - if the comment corresponding to a global/local ID is less
    than two characters.
    3) [global ID] - if the comment corresponding to a global/local ID has no named
    entities.
    """
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
    assert type(rawDataFile) == pandas.core.frame.DataFrame, \
        repr(rawDataFile) + " is not a csv reader object."
    assert type(playerNameFile) == pandas.core.frame.DataFrame, \
        repr(playerNameFile) + " is not a csv reader object."

    if not _checkColIndices(rawDataFile):
        raise commentData.FormatError("The csv file is either incorrectly formatted or a column header is missing.")
    if (rawDataFile["global_ID"].dtypes != int or rawDataFile["local_ID"].dtypes != int):
        raise TypeError("The types of the columns are incorrect.")
    try:
        playerNameFile["nicknames"]
    except:
        raise Exception("The nickname file does not have the column 'nickname'.")

    globID = rawDataFile["global_ID"]
    locID = rawDataFile["local_ID"]
    comm = rawDataFile["comment"]
    twoDList = []
    # every comment is unique in its glob/loc ID. Maintain list of past IDs to
    # prevent having duplicate comments. Within a single comment, however, it is
    # fine to have multiples of a single named entity (in fact, we want that).
    duplicates = []
    for index in range(rawDataFile.shape[0]):
        if [globID[index], locID[index]] not in duplicates:
            try:
                # uppercase = string.capwords(comm[index])
                _extractEntities(twoDList, globID[index], locID[index], comm[index])
                _findNickname(twoDList, globID[index], locID[index], comm[index], playerNameFile)
            except:
                raise Exception("Failed to create 2D list of named entities.")
        duplicates.append([globID[index], locID[index]])
        print(index)
    return twoDList

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


def _checkColIndices(rawDataFile):
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

def _extractEntities(lst, glob, loc, comment):
    """
    Returns a 2D list with 1D lists as named entities/categories(person, place, etc.).
    Uses the AllenNLP module to find the named entities. If the comment contains
    no named entities, return [global ID, local ID]. If the length of the string
    is too small for the AllenNLP to work, return [global ID, local ID].

    Parameter comment: a comment from a Reddit thread.
    Precondition: comment must be a string.
    """
    try:
        predictor = Predictor.from_path("https://storage.googleapis.com/allennlp-public-models/ner-model-2020.02.10.tar.gz")
        # the allenNLP algorithm returns a dictionary. For my purpose, I only need
        # two of the key-value pairs: the words and the tags/types of the words.
        rawDictionary = predictor.predict(sentence=comment)
        allWords = rawDictionary["words"]
        tags = rawDictionary["tags"]
        counter = 0
        flag = False
        for word in tags:
            if word != "O":
                lst.append([glob, loc, allWords[counter],word])
                flag = True
            counter += 1 # prevents assigning a wrong word if two words have the same tag
        if not flag:
            # If there is a comment more than 2 characters but has no named entities
            lst.append([glob, loc])
    except:
        # If the comment is less than or equal to 2 characters, than treat as
        # if the comment has no named entities
        lst.append([glob, loc])
    return lst

def _findNickname(lst, glob, loc, comment, nicknameFile):
    """
    Checks and adds to list any mentions of named entities as nicknames.
    """
    nicknames = nameMatching.createList(nicknameFile, "nicknames")
    for name in nicknames:
        if type(name) == list:
            for term in name:
                if term in comment and " " in term:
                    lst.append([glob, loc, term, "U-PER"])
        elif type(name) != list:
            if name in comment and " " in name:
                lst.append([glob, loc, name, "U-PER"])
