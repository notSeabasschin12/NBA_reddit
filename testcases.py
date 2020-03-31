"""
A script for testing my code.
Creator: Sebastian Guo
Last modified: March 29 2020
"""

import commentData
import extraction
import csv
import unittest


class TestCases(unittest.TestCase):
    """
    Class for testing my code. I used the unittest module provided by Python.
    To utilize the unittest module, I created a class that subclassed from the
    TestCase class which allowed me to create a new test class. For each unit test
    I created a new function and used assertion methods from the unittest module.
    """
    def testComment(self):
        """
        Unit test for class Commment.
        """
        comm1 = commentData.Comment(1, 1, "Random comment with names John and Joe", ["John", "Joe"], ["John"])
        comm2 = commentData.Comment(2, 2, "Random comment with no names", None, None)

        # Test to see if attributes are initialized correctly
        # Setters are tested through initializing a comment object.
        self.assertEqual(1, comm1.getLocal())
        self.assertEqual(1, comm1.getGlobal())
        self.assertEqual("Random comment with names John and Joe", comm1.getComment())
        self.assertEqual(["John", "Joe"], comm1.getNamed())
        self.assertEqual(["John"], comm1.getMatched())
        self.assertEqual(None, comm2.getNamed())
        self.assertEqual(None, comm2.getMatched())

        # Test if the assert statements work
        self.assertRaises(AssertionError, commentData.Comment, "a", 1, "Comm", [], [])
        self.assertRaises(AssertionError, commentData.Comment, 1, "a", "Comm", [], [])
        self.assertRaises(AssertionError, commentData.Comment, 1, 1, 1, [], [])
        self.assertRaises(AssertionError, commentData.Comment, 1, 1, "Comm", "you", [])
        self.assertRaises(AssertionError, commentData.Comment, 1, 1, "Comm", [1, 2], [])
        self.assertRaises(AssertionError, commentData.Comment, 1, 1, "Comm", [], "a")
        self.assertRaises(AssertionError, commentData.Comment, 1, 1, "Comm", [], [1, 2])

    def testColTitleIndices(self):
        """
        Unit test for the function colTitleIndices.
        """
        # Test for a spreadsheet with column names in first row
        with open("/home/sebastianguo/Documents/Research/data/tester1.csv", newline='') as csvfile1:
            tester1 = csv.reader(csvfile1)
            self.assertEqual({"global_ID": 1, "local_ID": 2, "comment": 13}, extraction.colTitleIndices(tester1))
        # Test for a spreadsheet with column names in first row, but in mixed order
        with open("/home/sebastianguo/Documents/Research/data/tester2.csv", newline='') as csvfile2:
            tester2 = csv.reader(csvfile2)
            self.assertEqual({"local_ID": 5, "global_ID": 8, "comment": 12}, extraction.colTitleIndices(tester2))
        # Test for a spreadsheet with column names NOT in first row
        with open("/home/sebastianguo/Documents/Research/data/tester3.csv", newline='') as csvfile3:
            tester3 = csv.reader(csvfile3)
            self.assertEqual(None, extraction.colTitleIndices(tester3))
        # Test for a spreadsheet without all three necessary column headers
        with open("/home/sebastianguo/Documents/Research/data/tester4.csv", newline='') as csvfile4:
            tester4 = csv.reader(csvfile4)
            self.assertEqual(None, extraction.colTitleIndices(tester4))
        # Test for a spreadsheet with repeating of three necessary column headers
        with open("/home/sebastianguo/Documents/Research/data/tester5.csv", newline='') as csvfile5:
            tester5 = csv.reader(csvfile5)
            self.assertEqual({"global_ID": 1, "local_ID": 2, "comment": 12}, extraction.colTitleIndices(tester5))

        # Test assert statement of function colTitleIndices
        self.assertRaises(AssertionError, extraction.colTitleIndices, "not a reader object")

    def testExtractColData(self):
        """
        Unit test for the function extractColData.
        """
        # Test dictionary that is in order with reader object
        with open("/home/sebastianguo/Documents/Research/data/tester1.csv", newline='') as csvfile1:
            tester1 = csv.reader(csvfile1)
            dataList1 = extraction.extractColData(tester1, {"global_ID": 1, "local_ID": 2, "comment": 13})
            self.assertEqual([[16802, 302, "My stream failed so I couldn't watch all the game, looks it was warning me of the eventual blowout."]], dataList1)
        # Test dictionary that is not in correct order with reader object
        with open("/home/sebastianguo/Documents/Research/data/tester2.csv", newline='') as csvfile2:
            tester2 = csv.reader(csvfile2)
            dataList2 = extraction.extractColData(tester2, {"local_ID": 5, "global_ID": 8, "comment": 12})
            self.assertEqual([[16802, 302, "My stream failed so I couldn't watch all the game, looks it was warning me of the eventual blowout."]], dataList2)
        # Test reader object which is not formatted correctly (column header not in first line, not all headers, multiple headers)
        with open("/home/sebastianguo/Documents/Research/data/tester3.csv", newline='') as csvfile3:
            tester3 = csv.reader(csvfile3)
            dataList3 = extraction.extractColData(tester3, {"global_ID": 1, "local_ID": 2, "comment": 13})
            self.assertEqual(None, dataList3)
        with open("/home/sebastianguo/Documents/Research/data/tester4.csv", newline='') as csvfile4:
            tester4 = csv.reader(csvfile4)
            dataList4 = extraction.extractColData(tester4, {"global_ID": 1, "local_ID": 2, "comment": 13})
            self.assertEqual(None, dataList4)
        # Test reader object that is formatted correctly but either the global_ID, local_ID, or comment is not the correct type.
        with open("/home/sebastianguo/Documents/Research/data/tester6.csv", newline='') as csvfile5:
            tester5 = csv.reader(csvfile5)
            dataList5 = extraction.extractColData(tester5, {"global_ID": 1, "local_ID": 2, "comment": 13})
            self.assertEqual(None, dataList5)

        # Test assert statements of function extractColData
        self.assertRaises(AssertionError, extraction.extractColData, "", {"global_ID": 1, "local_ID": 2, "comment": 13})
        with open("/home/sebastianguo/Documents/Research/data/tester1.csv", newline='') as csvfile1:
            self.assertRaises(AssertionError, extraction.extractColData, csvfile1, "not a dictionary")
        with open("/home/sebastianguo/Documents/Research/data/tester1.csv", newline='') as csvfile2:
            self.assertRaises(AssertionError, extraction.extractColData, csvfile2, {})
        with open("/home/sebastianguo/Documents/Research/data/tester1.csv", newline='') as csvfile3:
            self.assertRaises(AssertionError, extraction.extractColData, csvfile3, {"global_ID":1, "local_ID":2, "comment":3})
        with open("/home/sebastianguo/Documents/Research/data/tester1.csv", newline='') as csvfile4:
            self.assertRaises(AssertionError, extraction.extractColData, csvfile4, {"A":1, "B":2, "C":3})

if __name__ == "__main__":
    unittest.main()
