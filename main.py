"""
Script file to be run. It first extracts named entities from a file with scrapped Reddit
comment data and places them according to the global ID. It then takes all of the
named entities mentioned in the scrapped file and narrows down the list to those
mentioning players from the New York Knicks basketball team.

I used the allennlp module's named entity recognition model to extract mentions
of named entities from the data that I collected and stored in the program. I
used the pandas module which provided methods to input and manipulate data from
csv files and then export new data into csv files.

Creator: Sebastian Guo
Last modified: June 8 2020
"""
import extraction
import nameMatching
import allennlp
import pandas
from allennlp.predictors.predictor import Predictor
import allennlp_models.ner.crf_tagger

def main():
    """
    Main function to run for research. Its purpose is detialed in the file comment.
    """
    with open("/home/sebastianguo/Documents/Research/data/smallSample.csv", newline='') as csvfile1:
        reader = pandas.read_csv(csvfile1)
    with open("/home/sebastianguo/Documents/Research/data/knick_players.csv", newline='') as csvfile2:
        reader2 = pandas.read_csv(csvfile2)


    # Creates a 2D list with list entries that are either named entities according
    # to their global/local IDs or markers to designate a comment without a
    # named entity.
    commentDataList = extraction.extractColData(reader, reader2)
    # globalIDList = extraction.getGlobalID(reader)
    # # Creates csv files for each Reddit thread with all named entities mentioned.
    # # The names of the csvfiles are the global IDs for the threads.
    # for term in globalIDList:
    #     extraction.createDataFrame(term, commentDataList)

    # # Creates a csv file named total.csv that takes the commentDataList and finds
    # # the total times each named entity is mentioned.
    # nameMatching.aggregate(commentDataList)
    #
    # # Creates a csv file named mentions.csv that builds upon the csv file
    # # outputted by the function aggregate() but has columns that mark whether or
    # # not the named entity corresponds to a player from the output list of
    # # findPlayerNames.
    # nameMatching.playerMentions(reader2, nameMatching.findPlayerNames(reader2))

if __name__ == '__main__':
    main()
