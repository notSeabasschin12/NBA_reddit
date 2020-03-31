"""
Module to extract names of players from an Excel spreadsheet.
I used the csv module to input and read the spreadsheet containing Reddit comment data.
Creator: Sebastian Guo
Last modified: March 30 2020
"""

import csv
import commentData
from allennlp.predictors.predictor import Predictor


def colTitleIndices(readerObj):
    """
    Assigns to an empty dictionary the key-value pairs that correspond to the
    column names global_ID, local_ID, and comment and their associated column numbers.
    Returns the dictionary. The order of the dictionary key-value pairs does not
    matter.

    If one of the column names does not exist, the function returns None. Also if
    the column names are not in the first row of the spreadsheet that is associated
    with the readerObj, the function also returns None. These assumptions make sure
    that the spreadsheet with the data is inputted/formatted correctly
    (necessary column names exist and column names are in the irst row).

    If the first row has two instances of one of the column names, the first one
    is used.

    The function also takes in as an input, a reader object which allows a csv
    file to be read line by line.

    Note about assert statement: Technically, since _colTitleIndices is a private
    method, it is not necessary to enforce preconditions. However, just to be safe,
    I asserted that readerObj is a csv reader object.Since you create a reader object
    by calling the csv.reader() method (which doesn't seem to be a constructor but
    only returns a reader object), I couldn't use isinstance() with the readerObj
    and the class Reader. Therefore, to assert that readerObj is a csv reader object,
    I create an empty csv file called enforcer.csv. Through this, I was able to
    assert that readerObj was an object of the csv reader class was by comparing
    it to another csv file's type (which we know is a csv reader object).

    Parameter readerObj: the csv reader object with the csvfile that you want
    to extract the data of the column numbers from.
    Precondition: must be a csv reader object.
    """
    assert isinstance(readerObj, type(csv.reader("/home/sebastianguo/Documents/Research/data/enforcer.csv"))), repr(readerObj) + " is not a csv reader object."
    colNumDict = {}
    rowNum = 0
    for row in readerObj:
        columnNum = 0 # want to rest columnNum after each row
        rowNum += 1
        for term in row:
            columnNum += 1
            if term == "global_ID" and rowNum == 1 and "global_ID" not in colNumDict:
                colNumDict["global_ID"] = columnNum
            elif term == "local_ID" and rowNum == 1 and "local_ID" not in colNumDict:
                colNumDict["local_ID"] = columnNum
            elif term == "comment" and rowNum == 1 and "comment" not in colNumDict:
                colNumDict["comment"] = columnNum
    return colNumDict if (len(colNumDict.items()) == 3) else  None

def extractColData(readerObj, indexDict):
    """
    Returns a two dimensional list. Each inner list corresponds to one comment/row
    in the csv file corresponding to the inputted csv reader object. For each inner
    list of the returned two dimensional list, it will contain three terms: the global_ID,
    local_ID, and comment that is connected to a user comment. All three of these
    values should be assigned values and never be empty. All global_IDs and local_IDs
    must be integers and the comments must be strings.

    The readerObj should be the same csv file from which the indexDict was found.
    Since the precondition for readerObj specifies that it has to only be a csv
    object but nothing more, the function checks that the csv reasader object is
    formatted correctly with the three necessary headers in the first row and
    nowhere else. If readerObj is not formatted correctly or the column terms
    are incorrect, return None.

    According to the precondition, the order of the three keys in indexDict do
    not matter. The function will rearrange the 2D list order to make the
    keys go "global_ID", "local_ID", and "comment". Doing this allows for every
    inner list in the outputted two dimensional list contain the same ordering.

    Parameter readerObj: the csv reader object with the csvfile that you want
    to extract the data from.
    Precondition: must be a csv reader object (asserting this is the same as the
    function colTitleIndices).

    Parameter indexDict: the dictionary that contains the keys "global_ID",
    "local_ID", and "comment". The values associated with these keys are the column
    numbers of the spreadsheet headers.
    Precondition: must be of type dictionary and must contain the three key names
    mentioned above (order doesn't matter, will be corrected in the function).
    """
    assert isinstance(readerObj, type(csv.reader("/home/sebastianguo/Documents/Research/data/enforcer.csv"))), repr(readerObj) + " is not a csv reader object."
    assert type(indexDict) == dict, repr(indexDict) + " is not of type dictionary."
    assert len(indexDict) == 3, repr(indexDict) + " is not length three."
    assert "global_ID" in indexDict and "local_ID" in indexDict and "comment" in indexDict, repr(indexDict) + " does not contain the correct keys"
    twoDList = []
    rowNum = 0
    for row in readerObj:
        rowNum += 1
        if rowNum != 1 and ("global_ID" in row or "local_ID" in row or "comment" in row):
            return None
        elif rowNum == 1 and ("global_ID" not in row or "local_ID" not in row or "comment" not in row):
            return None
        try:
            if rowNum != 1:
                twoDList.append([int(row[indexDict["global_ID"]-1]), int(row[indexDict["local_ID"]-1]), str(row[indexDict["comment"]-1])])
        except:
            return None
    return twoDList

def storeAsObjects(twoDList):
    """
    Function that returns a one-dimensional list with each term corresponding to
    a pointer to a Comment object. While the function extractColData returns a
    two-dimensional list, this function makes the way to store the data found from
    extractColData with the lists of named entities in the comments. Although it
    is possible to add the names of the players to the 2D list, that would be
    difficult to read so putting all of the data for a single comment into an
    object allows for ease of access.

    The name of each pointer is a string

    The inputted twoDList is the return output of the function extractColData.

    Parameter twoDList: a two dimensional list. Each one dimensional list within it
    has three terms: global_ID, local_ID, and a comment.
    Precondition: twoDList must be a two-dimensional list. Ever term inside of the
    2D list must also be a list. Each of these list terms must contain three
    values. The first two must be integers and the third/last one must be a string.
    """
    asssert type(twoDList) == list, repr(twoDList) + " is not of type list."
    for term in twoDList:
        assert type(term) == list, "The terms inside of twoDList are not all lists."
        assert len(term) == 3, "The length of term " + repr(term) + " is not three."
        assert type(term[0]) == int and type(term[1]) == int and type(term[2]) == str, "The types of the 1D lists are invalid."
    for oneDList in twoDList:
        
