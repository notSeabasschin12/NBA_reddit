"""
Module to match named entities from csv files to players from the New York
Knicks roster.

Creator: Sebastian Guo
Last modified: June 1 2020
"""
import extraction
import pandas
import os

def aggregate(commentDataList):
    """
    Creates a csv file based off of an inputted list of named entities. The
    function extractColData from the extraction module creates a two-dimensional
    list with data about the named entity. The csv file created in this function
    will be a spreadsheet with the number of times a named entity is mentioned in
    the whole of the scrapped Reddit data comments.

    Parameter commentDataList: A list containing named entities and their types.
    Precondition: Must be a two-dimensional list with inner entities as lists.
    The inner entries can either be a list with four terms (global ID, local ID,
    named entity, type) or a list with two terms (global ID and local ID). If
    the inner list only has two terms, that means that the associated comment has
    no named entities and will not affect the aggregate list of this function.
    """
    totMent = {"named entity": [], "type": [], "mentions": []}
    for lst in commentDataList:
        if len(lst) == 4 and (lst[2] not in totMent["named entity"]):
            # If named entity not in list, add entity to dictionary
            totMent["named entity"].append(lst[2])
            totMent["type"].append(lst[3])
            totMent["mentions"].append(1)
        elif len(lst) == 4 and (lst[2] in totMent["named entity"]):
            # If named entity in list, increase mentions by one
            index = totMent["named entity"].index(lst[2])
            totMent["mentions"][index] += 1
    df = pandas.DataFrame(totMent)
    df.to_csv(r'/home/sebastianguo/Documents/Research/csv-files/total.csv', index=False)
