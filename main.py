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
import raceAnalysis

def main(team):
    """
    Main function to run for research. Its purpose is detailed in the file comment.
    """
    with open("/home/sebastianguo/Documents/Research/Teams/" + team + "/smallSample.csv", newline='') as csvfile1:
        sampleReader = pandas.read_csv(csvfile1)
    with open("/home/sebastianguo/Documents/Research/Teams/" + team + "/roster.csv", newline='') as csvfile2:
        rosterReader = pandas.read_csv(csvfile2)

    # Creates a 2D list with list entries that are either named entities according
    # to their global/local IDs or markers to designate a comment without a
    # named entity.
    commentDataList = extraction_v2.extractColData(sampleReader, rosterReader)
    globalIDList = extraction_v2.getGlobalID(sampleReader)
    rosterList = nameMatching.findPlayerNames(rosterReader)
    managementList = raceAnalysis.findManagement(rosterReader)
    # Creates a csv file named mentions.csv that takes the commentDataList and finds
    # the total times each named entity is mentioned and has columns that mark
    # the player that corresponds to the named entity in the output list of
    # findPlayerNames.
    nameMatching.playerMentions(commentDataList, rosterReader, rosterList, team)
    # Creates a csv file with all of the separate comments and with columns marking
    # whether or not a certain comment contains a mention of a player
    nameMatching.commentPlayers(sampleReader, rosterReader, rosterList, commentDataList, team)

    # with open("/home/sebastianguo/Documents/Research/teams.csv", newline='') as teamFile:
    #     teamReader = pandas.read_csv(teamFile)
    # # _formatSeasonResults(teamReader, team)
    #
    # _runByGlobID(globalIDList, rosterList, managementList, commentDataList, team, rosterReader, teamReader)
    with open("/home/sebastianguo/Documents/Research/Teams/" + team + "/commentRosterMentions.csv", newline='') as csvfile4:
         commentReader = pandas.read_csv(csvfile4)
    _calculatePrecRec(rosterList, team, commentReader)

def _runByGlobID(globalIDList, rosterList, mgmtList, commentDataList, team, rosterReader, teamReader):
    """
    Function that runs the functions that work by global ID. The function is split
    into two parts: one that works to extract player mentions by global ID and comment.
    The other looks at the effects of race in commentor's perception of players and their
    contribution to a win or loss.

    1) createDataFrame() creates a list of of every named entity in a global ID thread.
    The names of the csv files are the global ID. playerMentionsGlob() aggregates
    the different named entities and marks the player the named entity
    corresponds to. commentPlayersGlob() lists the different comments for a global
    ID and whether or not certain players are mentioned in the comment.
    2) winOrLose() determines whether or not the game for a global ID is a win or
    loss. coachMentionsGlob() creates separate csv files for global ID with
    management mentions, their race, and the outcome of the game.
    """
    with open("/home/sebastianguo/Documents/Research/game_thread_urls_2020_enhanced.csv", newline='') as csvfile5:
        globIDReader = pandas.read_csv(csvfile5)
    with open("/home/sebastianguo/Documents/Research/Teams/" + team + "/2019-2020_scores.csv", newline='') as csvfile6:
        scoreReader = pandas.read_csv(csvfile6)
    threadIDList = globIDReader["ID"].tolist()
    gameDateList = scoreReader["New Date"].tolist()

    dictionary = {"ID":[], "Opponent":[], "Result":[]}
    teamStr = raceAnalysis.makeTeamStr(teamReader, team)
    for term in globalIDList:
        # # Part 1: separates mentions.csv and commentMentions.csv by global ID.
        # extraction_v2.createDataFrame(term, commentDataList, team)
        #
        # with open("/home/sebastianguo/Documents/Research/Teams/" + team + "/listOfRosterMentionsByGame/" + str(term) + ".csv", newline='') as gameFile:
        #     gameReader = pandas.read_csv(gameFile)
        # nameMatching.playerMentionsGlob(gameReader, rosterReader, rosterList, team)
        #
        # with open("/home/sebastianguo/Documents/Research/Teams/" + team + "/commentRosterMentions.csv", newline='') as csvfile4:
        #     commentReader = pandas.read_csv(csvfile4)
        # nameMatching.commentPlayersGlob(commentReader, rosterList, term, team)
        #
        # # Part 2: looks at management, game results, and race.
        # with open("/home/sebastianguo/Documents/Research/Teams/" + team + "/aggRosterMentionsByGame/" + str(term) + ".csv", newline='') as gameFile2:
        #     gameReader2 = pandas.read_csv(gameFile2)

        result = raceAnalysis.winOrLose(globIDReader, scoreReader, threadIDList, gameDateList, teamStr, term, team, dictionary)
        dictionary["ID"].append(term)
        dictionary["Result"].append(result)
        # raceAnalysis.coachMentionsGlob(term, gameReader2, rosterReader, mgmtList, result, team)
    df = pandas.DataFrame(dictionary)
    df.to_csv(r'/home/sebastianguo/Documents/Research/Teams/' + team + '/win.csv', index=False)

def _calculatePrecRec(rosterList, team, commentReader):
    """
    Function that creates a csv file title precisionAndRecall.csv to find the amount
    of true positives, false positive, and false negatives when comparing the machine
    code run commentMentions.csv to a manually created hand code file. Then, calculate
    precision and recall to determine accuracy of the machine code.
    """
    with open("/home/sebastianguo/Documents/Research/Teams/" + team + "/handCodeSample.csv", newline='') as csvfile4:
        handCodeReader = pandas.read_csv(csvfile4)
    handCodeCompare.compareFiles(commentReader, handCodeReader, rosterList, team)

def _formatSeasonResults(teamReader, team):
    """
    A function to reformat the csv file containing a basketball players season
    results. The csv file/basketball results are found from the website
    "basketball-reference.com"
    """
    with open("/home/sebastianguo/Documents/Research/Scores/2019-2020_" + team + ".csv", newline='') as csvfile3:
        resultReader = pandas.read_csv(csvfile3)
    raceAnalysis.formatData(resultReader, teamReader, team)

if __name__ == '__main__':
    main("Hawks")
