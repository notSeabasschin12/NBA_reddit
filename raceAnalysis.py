"""
Module to look at the effects of race in basketball teams.

Creator: Sebastian Guo
"""
import pandas
import string
import re
import commentData

def coachMentionsGlob(glob, playMenGlobFile, playerNameFile, mgmtList, result, team):
    """
    A function that outputs a csv file separated by thread/global ID. This file
    contains the different coaches, general managers, and owners of a basketball
    team, how many times their mentioned, their race, and whether or not the
    game for the team was won or not.

    Parameter glob: the global ID/thread that the function finds mentions in.
    Precondition: must be an integer greater than zero.

    Parameter playMenGlobFile: A csv file created from function playerMentionsGlob().
    Precondition: Must contain the headers. Must be a csv file reader object.

    Parameter playerNameFile: a reader object that contains information about player
    names and nicknames.
    Precondition: must be a DataFrame object created by the pandas module.

    Parameter mgmtList: a list containing the coaches, GMs, and owners of a team.
    Precondition: must be of type list.

    Parameter result: whether or not the game corresponding to the global ID was won.
    Precondition: must be either "Win", "Lose", or "N/A".

    Parameter team: the basketball team the code is run on.
    Precondition: team is of type string
    """
    _assertionCoachMentionsGlob(glob, playMenGlobFile, playerNameFile, mgmtList, result, team)
    try:
        ment = playMenGlobFile["mentions"]
        position = playerNameFile["Pos"]
        race = playerNameFile["race"]
    except:
        raise commentData.FormatError("The csv files inputted do not have the correct headers.")
    endDict = {"Name":[], "Pos":[], "Race":[], "Mentions":[]}

    for name in mgmtList:
        aggMent = 0
        indexList = playMenGlobFile.index[playMenGlobFile[name] == 1].tolist()
        for row in indexList:
            aggMent += ment[row]
        # Creates a single entry list.
        indexName = playerNameFile.index[playerNameFile["Player"] == name].tolist()
        endDict["Name"].append(name)
        endDict["Pos"].append(position[indexName[0]])
        endDict["Race"].append(race[indexName[0]])
        endDict["Mentions"].append(aggMent)

    endDict["Name"].append(result)
    endDict["Pos"].append("")
    endDict["Race"].append("")
    endDict["Mentions"].append("")
    df = pandas.DataFrame(endDict)
    df.to_csv(r'/home/sebastianguo/Documents/Research/Teams/' + team + '/managementRaceByGame/' + str(glob) + '.csv', index=False)

def winOrLose(globIDFile, seasonResultFile, threadIDList, gameDateList, teamStr, glob, team, d):
    """
    Function to see whether for a global ID or game, the inputted team won or lost.
    Returns a csv file titled gameResult.csv with the data. To figure out the
    result of a game, look at a csv file containing games for a certain team, the
    dates, and the results. An inputted file containing global IDs and the dates
    of the thread post is then compared to the dates of the season games of a team.

    The function looks at both the date of the post and the opponent team. The
    opponent team check is necessary because post game threads are sometimes posted
    a date after the game and if a team plays two games in a row, it could mess up
    results. However, some global ID threads are not post game threads, so not
    every thread title has a basketball team name in it.

    Parameter globIDFile: a csv file containing the Reddit thread titles,
    the corresponding global IDs of those threads, and the dates of the game.
    Precondition: must be a reader object and contain the headers "ID" and "dt".

    Parameter seasonResultFile: a csv file containing the results of a team's season.
    Precondition: must be a reader object and contain the headers "Result", "Opponent",
    and "New Date" (the last header is formatted from the function formatDate()).

    Parameter threadIDList: a list containing every ID in globIDFile to use
    for finding indices of global IDs. The list is inputted as a parameter to prevent
    repition.
    Precondition: must be a list.

    Parameter gameDateList: a list containing the dates of games played in a season.
    Precondition: must be a list.

    Parameter teamStr: a string containing all NBA teams except "team".
    Precondition: must be a string.

    Parameter glob: a global ID that this function finds a game result for.
    Precondition: must be an integer greater than zero.

    Parameter team: the team for which you are trying to find the result of a game.
    Precondition: must be a string.
    """
    _assertionsWinOrLose(globIDFile, seasonResultFile, threadIDList, gameDateList, teamStr, glob, team)
    idRow = threadIDList.index(str(glob))
    threadPostDate = globIDFile["dt"][idRow]
    regEx = re.compile(teamStr)
    regExList = regEx.findall(globIDFile["title"][idRow])
    while True:
        # If there is no mention of a team in the thread title, assume the thread
        # is not a post game discussion
        if len(regExList) == 0:
            break
        else:
            try:
                gameRow = gameDateList.index(threadPostDate)
                if seasonResultFile["Opponent Shortened"][gameRow] not in regExList:
                    threadPostDate = _subtractDate(threadPostDate)
                else:
                    break
            except:
                threadPostDate = _subtractDate(threadPostDate)
    if len(regExList) == 0:
        d["Opponent"].append("")
        return "N/A"
    else:
        d["Opponent"].append(regExList[0])
        gameResult = seasonResultFile["Result"][gameRow]
    if gameResult == "W":
        return "Win"
    elif gameResult == "L":
        return "Lose"

def makeTeamStr(teamFile, team):
    """
    A function to create a regular expression string containing all of the NBA
    basketball teams excluding the one passed in under the team parameter. This
    regex will be used in function winOrLose().

    Parameter teamFile: a file containing all 30 basketball teams in the NBA.
    Precondition: must be a csv reader object containing the header "Team".

    Parameter team: the team that the regex skips.
    Precondition: must be a string.
    """
    assert type(teamFile) == pandas.core.frame.DataFrame, \
        repr(teamFile) + " is not a csv reader object."
    assert type(team) == str, repr(team) + " is not of type string."
    try:
        teams = teamFile["Team"]
    except:
        raise comemntData.FormatError("The csv reader object does not contain header 'team'.")
    regExStr = ""
    for index in range(teamFile.shape[0]):
        if teams[index] != team:
            regExStr += teams[index] + "|"
    return regExStr[:-1]

def findManagement(playerNameFile):
    """
    Given a roster file, find the coaches, GMs, and owners of the team. Return
    a list of these people.

    Parameter playerNameFile: a reader object that contains information about player
    names and nicknames.
    Precondition: must be a DataFrame object created by the pandas module.
    """
    assert type(playerNameFile) == pandas.core.frame.DataFrame, \
        repr(playerNameFile) + " is not a csv reader object."
    try:
        position = playerNameFile["Pos"]
        player = playerNameFile["Player"]
    except:
        commentData.FormatError("The correct column header 'pos' does not exist.")

    mgmtList = []
    importantPeople = ["Coach", "GM", "Owner"]
    for index in range(playerNameFile.shape[0]):
        if position[index] in importantPeople:
            mgmtList.append(player[index])
    return mgmtList

def formatData(seasonResultFile, teamReader, team):
    """
    A file to take season data format the date column. The data from the website
    has dates in the form "Sun 10, 2019" This function turns it into the format MM/DD/YY.

    Parameter seasonResultFile: a file for the team in the parameter. It contains
    information about the games the team it played, the scores, and the result.
    Precondition: must be a reader from the pandas module.

    Parameter teamReader:

    Parameter team: the team that the file seasonResultFile is about.
    Precondition: must be a string.
    """
    assert type(seasonResultFile) == pandas.core.frame.DataFrame, \
        repr(seasonResultFile) + " is not a csv reader object."
    assert type(team) == str, repr(team) + " is not a string."
    date = seasonResultFile["Date"]
    numGames = len(seasonResultFile["G"])
    appendList1 = []
    appendList2 = []
    for number in range(numGames):
        oppTeam = seasonResultFile["Opponent"][number]
        if "Trail Blazers" in oppTeam:
            appendList1.append("Blazers")
        else:
            appendList1.append(oppTeam.split()[-1])
        appendList2.append(_changeDate(date[number]))

    seasonResultFile["Opponent Shortened"] = appendList1
    seasonResultFile["New Date"] = appendList2
    seasonResultFile.to_csv(r'/home/sebastianguo/Documents/Research/Teams/' + team + '/2019-2020_scores.csv', index=False)

def _subtractDate(threadPostDate):
    """
    Subtract the days from the date until a date is found that matches up with
    a game.
    """
    dateList = threadPostDate.split("/")
    month = int(dateList[0])
    day = int(dateList[1])
    year = int(dateList[2])
    if month == 1 and day == 1:
        month = 12
        day = 31
        year -= 1
    elif day == 1:
        day = 31
        month -= 1
    else:
        day -= 1
    return str(month) + "/" + str(day) + "/" + str(year)

def _changeDate(date):
    """
    Helper function to change date format of the function formatData().
    The dates are given in the form "Day of week, Month, Day, Year" and the output
    date is in the form "Day/Month/Year".
    """
    # Have the first entry blank so indexing into monthList lines up with the
    # number of months
    monthList = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    dateList = date.split()
    # THE csv files dates are all formatted the same such that the index of the
    # month starts at five.
    return str(monthList.index(dateList[1])) + "/" + str(dateList[2]) + "/" + str(dateList[3])


def _assertionCoachMentionsGlob(glob, playMenGlobFile, playerNameFile, mgmtList, result, team):
    """
    Function to test assertions for coachMentionsGlob().
    """
    assert type(glob) == int and glob > 0, repr(glob) + " is not an integer greater than zero."
    assert type(playMenGlobFile) == pandas.core.frame.DataFrame, \
        repr(playMenGlobFile) + " is not a csv reader object."
    assert type(playerNameFile) == pandas.core.frame.DataFrame, \
        repr(playerNameFile) + " is not a csv reader object."
    assert type(mgmtList) == list, repr(mgmtList) + " is not a list."
    assert type(result) == str, repr(result) + " is not a string."
    assert result == "Win" or result == "Lose" or result == "N/A"
    assert type(team) == str, repr(team) + " is not a string."

def _assertionsWinOrLose(globIDFile, seasonResultFile, threadIDList, gameDateList, teamStr, glob, team):
    """
    Function to test assertions for winOrLose().
    """
    assert type(globIDFile) == pandas.core.frame.DataFrame, \
        repr(globIDFile) + " is not a csv reader object."
    assert type(seasonResultFile) == pandas.core.frame.DataFrame, \
        repr(seasonResultFile) + " is not a csv reader object."
    try:
        globIDFile["ID"]
        print(1)
        globIDFile["dt"]
        print(2)
        seasonResultFile["Result"]
        print(3)
        seasonResultFile["Opponent"]
        print(4)
        seasonResultFile["Opponent Shortened"]
        print(5)
        seasonResultFile["New Date"]
    except:
        raise commentData.FormatError("The inputted csv files do not have correct headers.")
    assert type(threadIDList) == list and type(gameDateList) == list, "The inputted lists are not lists."
    assert type(teamStr) == str, repr(teamStr) + " is not a string."
    assert type(glob) == int and glob > 0, repr(glob) + " is not an integer more than zero."
    assert type(team) == str, repr(team) + " is not a string."
