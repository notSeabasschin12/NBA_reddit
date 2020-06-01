"""
Script to be run. It first extracts named entities from a file with scrapped Reddit
comment data. It then takes all of the named entities mentioned in the scrapped
file and narrows down the list to those mentioning players from the New York
Knicks basketball team.

I used the allennlp module's named entity recognition model to extract mentions
of named entities from the data that I collected and stored in the program. I
used the pandas module which provided methods to input and manipulate data from
csv files and then export new data into csv files.

Creator: Sebastian Guo
Last modified: May 29 2020
"""
import extraction
import nameMatching
import allennlp
import pandas
from allennlp.predictors.predictor import Predictor
import allennlp_models.ner.crf_tagger

with open("/home/sebastianguo/Documents/Research/data/tester1.csv", newline='') as csvfile1:
    reader = pandas.read_csv(csvfile1)
    commentDataList = extraction.extractColData(reader)
    print(commentDataList)
    nameMatching.aggregate(commentDataList)
    # globalIDList = extraction.getGlobalID(reader)
    # for term in globalIDList:
    #     extraction.createDataFrame(term, commentDataList)
