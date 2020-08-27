"""
Module that extracts data from scrapped csv files without using the allenNLP.

Creator: Sebastian Guo
"""
import pandas, re, string
import assertions
import name_matching

def create_data_frame(global_ID, cmt_data_list, team):
    """
    Returns a csv file after making a DataFrame object with four columns: global_ID,
    local_ID, name, and the category. Using the global ID attribute, all of the
    rows in the DataFrame should have the same global ID.

    Parameter globalID: the global ID corresponding to a Reddit thread. For this
    specific global ID, extract the data from the 2DList.
    Precondition: must be an integer greater than zero.

    Parameter cmt_data_list: a two-dimensional list that has as one of these two
    entries:
    1) a list of the form [global ID, local ID, name, category]
    2) [global ID, local ID] - if the comment corresponding to a global/local ID
    has no named entities.

    Parameter team: the basketball team the code is running on.
    Precondition: team is a string
    """
    assertions.assert_global_ID(global_ID)
    assertions.assert_cmt_data_list(cmt_data_list)
    assertions.assert_team(team)
    dictionary = {"global_ID":[], "local_ID":[], "name":[], "category":[]}
    for lst in cmt_data_list:
        # if the comment has less than 2 characters or has no named entities, add
        # an the global and local ID, but no named entity or category.
        if (len(lst) == 2 and global_ID == lst[0]):
            dictionary["global_ID"].append(global_ID)
            dictionary["local_ID"].append(lst[1])
            dictionary["name"].append("")
            dictionary["category"].append("")
        elif (len(lst) == 4 and global_ID == lst[0]):
            dictionary["global_ID"].append(global_ID)
            dictionary["local_ID"].append(lst[1])
            dictionary["name"].append(lst[2])
            dictionary["category"].append(lst[3])
    df = pandas.DataFrame(dictionary)
    df.to_csv(r'/home/sebastianguo/Documents/Research/Teams/' + team +
        '/roster_mentions_by_game/' + str(global_ID) + ".csv", index=False)

def extract_col_data(raw_data_file, roster_file, word_file_reader, team):
    """
    Returns a two dimensional list. Each inner list corresponds to a named entity,
    its category (person, place, nickname) with its associated global and local
    ID. All global_IDs and local_IDs must be integers. Comments can be of any
    category, but will be cast into strings. The function also checks if the
    comments have nicknames as named entities.

    Assume that for every global_ID and local_ID, there is an associated comment
    in that row. This means that the the number of elements in each of the
    three columns is the same. If the function fails to extract the data in any
    way, raise an exception.

    The order of the three columns in raw_data_file does not matter. The function
    will rearrange the 2D list order to make the keys go "global_ID", "local_ID",
    and "named entity/category".

    Since regexes are used to find full names, nicknames, first/last names, words
    that contain these names as substrings are removed from the comments before
    extraction. For shortened first/last names, a different method other than
    regex is used so substrings are not relevant for those.

    Parameter raw_data_file: the reader object with the csvfile that you want
    to extract the data from.
    Precondition: must be a DataFrame object created from the pandas module with
    headers global ID, local ID and comment. The terms in the global and local ID
    columns must be integers.

    Parameter roster_file: the reader object containing nicknames to check for in
    the comments.
    Precondition: must be a DataFrame object created from the pandas module and
    contain the correct headers.
    """
    assertions.assert_raw_data_file_format(raw_data_file)
    assertions.assert_roster_file_format(roster_file)
    assertions.assert_team(team)
    assertions.assert_word_removal_file_format(word_file_reader, team)
    glob_ID = raw_data_file["global_ID"]
    loc_ID = raw_data_file["local_ID"]
    comm = raw_data_file["comment"]
    cmt_data_list = []
    # For column "Player", "Nicknames", "First", and "Last", include potential
    # substrings in this list that could mistake as names.
    stop_words = word_file_reader[team].tolist()
    # every comment is unique in its glob/loc ID. Maintain list of past IDs to
    # prevent having duplicate comments.
    duplicates = []
    # call create_list here to prevent redundacy
    short_f = _create_list(roster_file, "First Short")
    short_l = _create_list(roster_file, "Last Short")
    name_str = _make_name_str(roster_file["Player"],
        roster_file["First"], roster_file["Last"])
    nickname_str = _make_nickname_str(_create_list(roster_file, "Nicknames"))
    for index in range(raw_data_file.shape[0]):
        if [glob_ID[index], loc_ID[index]] not in duplicates and not pandas.isnull(comm[index]):
            new_comm = comm[index]
            try:
                for word in stop_words:
                    new_comm = new_comm.replace(word, "")
                    new_comm = new_comm.replace(string.capwords(word), "")
                _extract_entities(cmt_data_list, glob_ID[index], loc_ID[index],
                    new_comm, name_str, nickname_str, short_f, short_l)
            except:
                raise Exception("Failed to create 2D list of named entities.")
        duplicates.append([glob_ID[index], loc_ID[index]])
    return cmt_data_list

def _extract_entities(cmt_data_list, global_ID, local_ID, comment, name_str,
    nickname_str, short_flist, short_llist):
    """
    Returns a 2D list with 1D lists as named entities/categories(person, place, etc.).
    If the comment contains no named entities, return [global ID, local ID].
    Function ignores case (frank vs. Frank) and stores possesive nouns with apostrophes
    removed (Frank's/Franks become Frank and frank also becomes Frank in the 2D list).

    roster_file is the file with the basketball roster full names, and shortened
    ones.
    """
    add_blank = len(cmt_data_list)
    _find_name(cmt_data_list, global_ID, local_ID, comment, name_str)
    _find_short_name(cmt_data_list, global_ID, local_ID, comment, short_flist, short_llist)
    _find_nickname(cmt_data_list, global_ID, local_ID, comment, nickname_str)
    # Add something to the 2D list to signal that the comment has no named entities.
    if len(cmt_data_list) == add_blank:
        cmt_data_list.append([global_ID, local_ID])
    return cmt_data_list

def _find_name(cmt_data_list, global_ID, local_ID, comment, name_str):
    """
    Finds any names (full, first, and last) in the comment and adds to cmt_data_list.
    """
    re_obj = re.compile(name_str, re.IGNORECASE)
    re_list = re_obj.findall(comment)
    for entity in re_list:
        cmt_data_list.append([global_ID, local_ID, string.capwords(entity), "U-PER"])
    return cmt_data_list

def _find_short_name(cmt_data_list, global_ID, local_ID, comment, short_flist,
    short_llist):
    """
    Finds any shortened versions of the players names in a comment using regular
    expressions. While finding nicknames and full names uses regular expressions,
    shortened names are a little bit more tricky. For example, if you are looking
    for a nickname like "Rich" in the string "Richard", it'll still return a hit
    even though we are only looking for "Rich".
    """
    no_punc = re.sub(r'[^\w\s]','',comment).lower()
    # Split into every word, assume shortened names are one words
    comm_split = no_punc.split()
    for term1 in short_flist:
        count_short = (comm_split.count(term1.lower()) +
            comm_split.count(term1.lower() + "s"))
        while (count_short != 0):
            cmt_data_list.append([global_ID, local_ID, term1, "U-PER"])
            count_short -= 1
    for term2 in short_llist:
        count_long = (comm_split.count(term2.lower()) +
            comm_split.count(term2.lower() + "s"))
        while (count_long != 0):
            cmt_data_list.append([global_ID, local_ID, term2, "U-PER"])
            count_long -= 1
    return cmt_data_list

def _find_nickname(cmt_data_list, global_ID, local_ID, comment, nickname_str):
    """
    Checks and adds to list any mentions of named entities as nicknames. The
    function ignores case and adds a nickname with the first letters of the word
    capitalized even if the word within the comment has incorrect case.
    """
    re_obj = re.compile(nickname_str, re.IGNORECASE)
    re_list = re_obj.findall(comment)
    for term in re_list:
        cmt_data_list.append([global_ID, local_ID, string.capwords(term), "U-PER"])
    return cmt_data_list

def _make_name_str(full_name, first_name, last_name):
    """
    Make a string to input for the regular expression.
    """
    str_re = ''
    for term_full in full_name:
        str_re += term_full + "|"
    for term_first in first_name:
        if not pandas.isnull(term_first):
            str_re += term_first + "|"
    for term_last in last_name:
        if not pandas.isnull(term_last):
            str_re += term_last + "|"
    return str_re[:-1]

def _make_nickname_str(nickname_list):
    """
    Make a regular expression string for nicknames.
    """
    str_re = ''
    for term in nickname_list:
        str_re += term + "|"
    return str_re[:-1]

def _create_list(roster_file, col_name):
    """
    Returns and creates a two-dimensional list according to the column name
    passed in as a parameter. Used for creating a list of nicknames, shortened
    first or last names.
    Some players might have multiple nicknames or shortened names.

    Parameter roster_file: the csv file contianing the column col_name.
    Precondition: must be a reader object from the pandas module.
    Paramter col_name: the name of the column in nameFile to create the list for.
    Precondition: must be a string
    """
    items = roster_file[col_name]
    return_list = []
    for index in range(roster_file.shape[0]):
        if not pandas.isnull(items[index]):
            list_names = items[index].split(",")
            return_list += list_names
    return return_list

def get_global_ID(raw_data_file):
    """
    Returns a list of the global IDs in the scrapped data file. The global ID
    of a comment distinguishes it from comments in different threads (so two
    comments in the same thread have the same global ID).

    If the terms in the column don't have the correct type, raise a TypeError.

    Parameter raw_data_file: the reader object with the csvfile that you want
    to extract the global IDs from.
    Precondition: must be a DataFrame object created from the pandas module.
    """
    assertions.assert_raw_data_file_format(raw_data_file)

    col = raw_data_file["global_ID"]
    glob_ID_list = []
    # add non-duplicate IDs to the glob_ID_list
    for item in col:
        if item not in glob_ID_list:
            glob_ID_list.append(item)
    return glob_ID_list
