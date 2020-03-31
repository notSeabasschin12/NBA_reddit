"""
Module containing the class Comment.
Creator: Sebastian Guo
Last modified: March 25 2020
"""


class Comment(object):
    """
    A class to initialize a Comment object.

    The main purpose of this class is to create objects for each comment taken in
    from a spreadsheet of data. It will also assign each comment a unique global
    and local ID, as well as any mentions of player names from the comment.

    # INSTANCE ATTRIBUTES
    # Attribute _global_ID: an identification number for the original post of the comment
    # within the subreddit.
    # Invariant: _global_ID must be an integer.
    #
    # Attribute _local_ID: an identification number for the specific comment within
    # a thread. While the _global_ID attribute refers to a post in the subreddit,
    # the _local_ID differentiates between comments within a single post/thread in
    # the subreddit.
    # Invariant: _local_ID must be an integer.
    #
    # Attribute _comnt: the comment of the Redditor.
    # Invariant: _comnt must be a string.
    #
    # Attribute _named_entities: any names that are mentioned in the comment. If
    # no names are mentioned in the comment, the attribute is set to None.
    # Invariant: _named_entities is a list whose entries are strings. Could also be
    # None.
    #
    # Attribute _matched_entities: any entry in the list named_entities that are
    # players on the team. If no players are in _named_entities, then _matched_entities
    # is set to None.
    # Invariant: _matched_entities is a list whose entries are strings. Could also
    # be None.
    """

    def setGlobal(self, value):
        """
        Set the global ID to the new value.

        Parameter _global_ID: an identification number for the original post of
        the comment within the subreddit.
        Precondition: _global_ID must be an integer.
        """
        assert type(value) == int, repr(value) + " is not of type integer."
        self._global_ID = value

    def getGlobal(self):
        """
        Returns the _global_ID attribute of the object.
        """
        return self._global_ID

    def setLocal(self, value):
        """
        Set the local ID to the new value.

        Parameter _local_ID: an identification number for the specific comment within
        a thread. While the _global_ID attribute refers to a post in the subreddit,
        the _local_ID differentiates between comments within a single post/thread in
        the subreddit.
        Precondition: _local_ID must be an integer.
        """
        assert type(value) == int, repr(value) + " is not of type integer."
        self._local_ID = value

    def getLocal(self):
        """
        Returns the _local_ID attribute of the object.
        """
        return self._local_ID

    def setComment(self, value):
        """
        Set the comment to the new value.

        Parameter value: the comment of the Redditor.
        Precondition: value must be a string.
        """
        assert type(value) == str, repr(value) + " is not of type string."
        self._comnt = value

    def getComment(self):
        """
        Returns the _comnt attribute of the object.
        """
        return self._comnt

    def setNamed(self, value):
        """
        Set the named entities to the new value.

        Parameter value: any names that are mentioned in the comment. If
        no names are mentioned in the comment, the attribute is set to None.
        Precondition: value is a list whose entries are strings.
        """
        assert (type(value) == list) or (value == None), repr(value) + " is not of type list or None."
        if value != None:
            for entry in value:
                assert type(entry) == str, "The term " + repr(entry) + " inside of the list is not a string"
        self._named_entities = value

    def getNamed(self):
        """
        Returns the _named_entities attribute of the object.
        """
        return self._named_entities

    def setMatched(self, value):
        """
        Set the matched entities to the new value.

        Parameter value: any entry in the list named_entities that are
        players on the team. If no players are in _named_entities, then _matched_entities
        is set to None.
        Precondition: value is a list whose entries are strings or None.
        """
        assert (type(value) == list) or (value == None), repr(value) + " is not of type list or None."
        if value != None:
            for entry in value:
                assert type(entry) == str, "The term " + repr(entry) + " inside of the list is not a string"
        self._matched_entities = value

    def getMatched(self):
        """
        Returns the _matched_entities attribute of the object.
        """
        return self._matched_entities

    def __init__(self, glob, local, comment="", named=None, matched=None):
        """
        Initializes a new Comment with instance attributes.

        Parameter _global_ID: an identification number for the original post of
        the comment within the subreddit.
        Precondition: _global_ID must be an integer.

        Parameter _local_ID: an identification number for the specific comment within
        a thread. While the _global_ID attribute refers to a post in the subreddit,
        the _local_ID differentiates between comments within a single post/thread in
        the subreddit.
        Precondition: _local_ID must be an integer.

        Parameter _comnt: the comment of the Redditor.
        Precondition: _comnt must be a string.

        Parameter _named_entities: any names that are mentioned in the comment. If
        no names are mentioned in the comment, the attribute is set to None.
        Precondition: _named_entities is a list whose entries are strings. Could also be
        None.

        Parameter _matched_entities: any entry in the list named_entities that are
        players on the team. If no players are in _named_entities, then _matched_entities
        is set to None.
        Precondition: _matched_entities is a list whose entries are strings. Could also
        be None.
        """
        self.setGlobal(glob)
        self.setLocal(local)
        self.setComment(comment)
        self.setNamed(named)
        self.setMatched(matched)

    def __str__(self):
        """
        Return a string representation of a Comment object.
        """
        return ("Comment with global ID "+str(self._global_ID)+", local ID "
        +str(self._local_ID)+", that contains the names "+str(self._named_entities)
        +" with the player names "+str(self._matched_entities)+".")
