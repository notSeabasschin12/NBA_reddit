# NBA_reddit
The purpose of this project is to analyze data from Reddit post-game NBA threads to see how accurate comments are in giving priase to those basketball players who deserve it. When Redditors discuss recent basketball games, they often reference certain players in their comments and provide their own opinions on whether that player performed well or poorly. However, the amount of credit that a Redditor provides to a basketball player might not reflect their actual performance in the game. One way to see whether or not the Redditor's praise or criticism of a player is reasonable is examining the statistics of the game. Through combining the player's statistics and the Redditor's comments, we will try to provide insight into whether or not a Redditor's analysis of a basketball game provides an accurate interpretation of the player's actual performance. 

Csv files containing raw Reddit data, rosters, and game scores are not included in repository. Outputted csv files containing information about mentions of basketball player names extracted from Reddit comments are not included as well.

Files:
extraction_v2.py: contains functions to take in Reddit comment data and output csv files with mentions of players on a given basketball team.
name_matching.py: similarly to extraction_v2.py, contains files to output csv files with information about player mentions in Reddit comments.
mgmt_matching.py: extracts mentions of managers from Reddit comment data. Also provides functions that take in a Reddit global ID thread and figure out whether or not that post-game thread corresponds to a win or loss.
mgmt_analysis.py: calculates the number of times coaches are mentioned after wins/losses. Also calculates the average sentiment of comments in which coaches for a specific basketball team are mentioned.
hand_code_compare.py: compares the accuracy of my machine generated file to a hand created ground truth file. The file being tested is a collection of Reddit comments and a matrix to show whether or not a player is mentioned in these comments.
sentiment_analysis.py: trains a Naive-Bayes classifier to analyze the sentiment of comments.
assertions.py: contains various functions to assert formatting of inputted csv files and other inputted parameters.


 
