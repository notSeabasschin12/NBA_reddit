"""
Script file to be run. It first extracts named entities from a file with scrapped Reddit
comment data and places them according to the global ID. It then takes all of the
named entities mentioned in the scrapped file and narrows down the list to those
mentioning players from the New York Knicks basketball team.

I used regular expressions and the re Python module to extract mentions
of named entities from the data that I collected and stored in the program. I
used the pandas module which provided methods to input and manipulate data from
csv files and then export new data into csv files.

Creator: Sebastian Guo
"""
import pandas
import nameMatching
import extraction
import extraction_v2
import handCodeCompare

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
    commentDataList = extraction_v2.extractColData(reader, reader2)
    globalIDList = extraction_v2.getGlobalID(reader)
    playerList = nameMatching.findPlayerNames(reader2)

    # Creates a csv file named total.csv that takes the commentDataList and finds
    # the total times each named entity is mentioned.
    nameMatching.aggregate(commentDataList)
    with open("/home/sebastianguo/Documents/Research/data/total.csv", newline='') as csvfile3:
        reader3 = pandas.read_csv(csvfile3)
    # Creates a csv file named mentions.csv that builds upon the csv file
    # outputted by the function aggregate() but has columns that mark whether or
    # not the named entity corresponds to a player from the output list of
    # findPlayerNames.
    nameMatching.playerMentions(reader2, reader3, playerList)

    # Creates a csv file with all of the separate comments and with columns marking
    # whether or not a certain comment contains a mention of a player
    nameMatching.commentPlayers(reader, reader2, playerList, commentDataList)
    with open("/home/sebastianguo/Documents/Research/data/commentMentions.csv", newline='') as csvfile4:
        reader4 = pandas.read_csv(csvfile4)
    with open("/home/sebastianguo/Documents/Research/data/handCodeSample.csv", newline='') as csvfile5:
        reader5 = pandas.read_csv(csvfile5)

    # Creates csv files for each Reddit thread/game with the named entities mentioned.
    # Creates csv files for each Reddit thread/game with comments tagged if they
    # contain a player mention.
    # The names of the csvfiles are the global IDs for the threads.
    for term in globalIDList:
        extraction_v2.createDataFrame(term, commentDataList)
        nameMatching.commentPlayersGlob(reader4, playerList, term)

    # Modifies reader5 (which contains handCodeData comment by comment) to include
    # for each player column the true positives, false positives, true negatives,
    # precision, and recall found by comparing the ground truth, or hand code data
    # and the code ran by the machine (the code I wrote). These data points are
    # meant to test how well the machine code found and marked named entities
    # within separate comments.
    handCodeCompare.compareFiles(reader4, reader5, playerList)

if __name__ == '__main__':
    main()
