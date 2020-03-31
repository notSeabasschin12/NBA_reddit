"""
Script to be run for research.

Everytime you open up a csv reader object and iterate through it, you cannot iterate
through it again. Thus, everytime that I want to access the spreadsheet data I
must create a new csv reader object.

I used the allennlp module's named entity recognition model to extract mentions
of players from the data that I collected and stored in the program.

Creator: Sebastian Guo
Last modified: March 29 2020
"""
import csv
import commentData
import extraction

with open("/home/sebastianguo/Documents/Research/data/mediumSample.csv", newline='') as csvfile1:
    columnReader = csv.reader(csvfile1)
    columnIndicesDict = extraction.colTitleIndices(columnReader)

with open("/home/sebastianguo/Documents/Research/data/mediumSample.csv", newline='') as csvfile2:
    dataReader = csv.reader(csvfile2)
    commentDataList = extraction.extractColData(dataReader, columnIndicesDict)
print(commentDataList)

# predictor = Predictor.from_path("https://s3-us-west-2.amazonaws.com/allennlp/models/ner-model-2018.12.18.tar.gz")
# print(predictor.predict(sentence="Never crossed your mind that he just isn\x19t good though?"))
