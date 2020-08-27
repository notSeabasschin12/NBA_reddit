"""
Module that uses a Naive Bayes Classifier to train a sentiment analysis model.
The inputted data set used to train/test the model is Twitter sample data.
While the model was trained through Twitter data, this module will be used to
find the sentiment of Reddit comments.

To write this module, I followed a tutorial written by Shaumik Daityari posted on
the website Digital Ocean.

Creator: Shaumik Daityari
Implementor: Sebastian Guo
"""
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import twitter_samples, stopwords
from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize
from nltk import FreqDist, classify, NaiveBayesClassifier
import re, string, random, pandas
import assertions

def _remove_noise(tokenized_tweet, stop_words = ()):
    """
    Function to return a cleaned up a tokenized tweet string. Gets rid of URLs,
    stop words, and @usernames. Then lemmatize the tokens.

    Parameter tokenized_list: a list of tokens created by method tokenize() that
    represents a single tweet.

    Parameter stop_words: words that will be considered unecessary for the training
    model and removed.
    """
    cleaned_tokens = []

    for token, tag in pos_tag(tokenized_tweet):
        # Remove URLs and @references
        token = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|'\
                       '(?:%[0-9a-fA-F][0-9a-fA-F]))+','', token)
        token = re.sub("(@[A-Za-z0-9_]+)","", token)

        if tag.startswith("NN"):
            pos = 'n'
        elif tag.startswith('VB'):
            pos = 'v'
        else:
            pos = 'a'

        lemmatizer = WordNetLemmatizer()
        # Lemmatize the word according to the tag of the token.
        token = lemmatizer.lemmatize(token, pos)

        if len(token) > 0 and token not in string.punctuation and token.lower() not in stop_words:
            cleaned_tokens.append(token.lower())
    return cleaned_tokens

def _get_all_words(cleaned_tweet_tokens_list):
    """
    Function to return a generator object that loops through all of the tokenized
    tweets and the tokens.

    Parameter cleaned_tweet_tokens_list: a 2D list containing tokenized tweets
    as 1D lists.
    """
    for tokenized_tweet in cleaned_tweet_tokens_list:
        for token in tokenized_tweet:
            yield token

def _get_tweets_for_model(cleaned_tweet_tokens_list):
    """
    Function to return a generator object that creates a dictionary for each
    tokenized tweet and assigns tokens(keys) a True value pair. This is done
    to format the tweet tokens in preparation for training the model.

    Parameter cleaned_tweet_tokens_list: a 2D list containing tokenized tweets
    as 1D lists.
    """
    for tokenized_tweet in cleaned_tweet_tokens_list:
        yield dict([token, True] for token in tokenized_tweet)

def _calc_word_freq(cleaned_tweet_tokens_list, num_comm_words):
    """
    A function to create a generator object iterating through every token. It
    then prints out the most common words (the number of different words depends on
    input parameter)
    """
    all_pos_words = _get_all_words(cleaned_tweet_tokens_list)
    freq_dist_pos = FreqDist(all_pos_words)
    print(freq_dist_pos.most_common(num_comm_words))

def train_classifier():
    """
    Function to prepare data, train and return a Naive Bayes Classifier model.
    First, function prepares tweet data to be fed as a datset for training a model.
    The data from twitter is pre-labeled tweets with positive or negative
    sentiment. It then tokenizes the tweets, lemmatizes the tokens, and formats
    the tokens to be fed into the training function.
    """
    stop_words = stopwords.words('english')
    # Tokenizes tweets and stores all tweets in a 2D list. Individual tweets are 1D lists.
    # [[tweet 1 token, tweet 1 token], [tweet 2 token, 2 tweet token, tweet 2 token]]
    positive_tweets_tokenized = twitter_samples.tokenized('positive_tweets.json')
    negative_tweets_tokenized = twitter_samples.tokenized('negative_tweets.json')
    positive_cleaned_tweets_token_list = []
    negative_cleaned_tweets_token_list = []
    # For each tokenized tweet, clean up noise and lemmatize the tokens.
    for tokenized_tweet in positive_tweets_tokenized:
        positive_cleaned_tweets_token_list.append(_remove_noise(tokenized_tweet, stop_words))
    for tokenized_tweet in negative_tweets_tokenized:
        negative_cleaned_tweets_token_list.append(_remove_noise(tokenized_tweet, stop_words))
    # _calc_word_freq(positive_tweets_tokenized, 15)

    positive_tweets_token_for_model = _get_tweets_for_model(positive_cleaned_tweets_token_list)
    negative_tweets_token_for_model = _get_tweets_for_model(negative_cleaned_tweets_token_list)
    # For each dictionary/tokenized tweet, assign a positive/negative label.
    # Store each dataset as a list with tuples for tokenized tweet dict and "pos/neg" label.
    positive_dataset = [(tweet_dict, "Positive")
                         for tweet_dict in positive_tweets_token_for_model]
    negative_dataset = [(tweet_dict, "Negative")
                         for tweet_dict in negative_tweets_token_for_model]
    dataset = positive_dataset + negative_dataset
    random.shuffle(dataset)

    train_data = dataset[:7000]
    test_data = dataset[7000:]
    classifier = NaiveBayesClassifier.train(train_data)
    # print("Accuracy is:", classify.accuracy(classifier, test_data))
    return classifier

def manager_cmt_sentiment(classifier, cmt_lvl_rost_ment_reader, global_ID,
    roster_list, mgmt_list, team):
    """
    Function to analyze the sentiment of comments that contain mentions of management.
    The function then finds the number of positive and negative comments for
    a manager in a dictionary. The file that is analyzed will be a csv file
    created from function comment_roster_glob() which sorts out comments by global ID.

    Parameter classifier: a trained model to analyze sentiment.
    Precondition: an object from the Naive Bayes Classiifer class.

    Parameter cmt_lvl_rost_ment_reader: a csv file created from comment_roster_glob().
    Contains comments for a global ID.
    Precondition: must be a DataFrame object with the correct headers.

    Parameter global_ID: the global ID/game that the function looks at.
    Precondition: must be of type integer and more than zero.

    Parameter roster_list: a list containing every player on a basketball team.
    Precondition: must be a list with string entries.

    Parameter mgmt_list: a list of the management for a basketball team.
    Precondition: must be of type list with string entries.

    Parameter team: the basketball team the function looks at.
    Precondition: must be a string.
    """
    _assertion_mgmt_cmt_sent(classifier, cmt_lvl_rost_ment_reader, global_ID, roster_list, mgmt_list, team)
    sentiment_dict = {}
    # Find row indices in comment mention file that have mentions of managers and
    # run sentiment analysis on those comments
    for manager in mgmt_list:
        sentiment_dict[manager] = [0,0]
        for row_ind in cmt_lvl_rost_ment_reader.index[cmt_lvl_rost_ment_reader[manager] == 1].tolist():
            comment = cmt_lvl_rost_ment_reader["comment"][row_ind]
            tokenized_comment = _remove_noise(word_tokenize(comment))
            sentiment = classifier.classify(dict([token, True] for token in tokenized_comment))
            if sentiment == "Positive":
                sentiment_dict[manager][0] += 1
            else:
                sentiment_dict[manager][1] += 1
    return sentiment_dict

def _assertion_mgmt_cmt_sent(classifier, cmt_lvl_rost_ment_reader, global_ID,
    roster_list, mgmt_list, team):
    """ Assertions for function manager_cmt_sentiment() """
    assertions.assert_classifier(classifier)
    assertions.assert_cmt_lvl_ment_file_format(cmt_lvl_rost_ment_reader, roster_list)
    assertions.assert_global_ID(global_ID)
    assertions.assert_str_list(roster_list)
    assertions.assert_str_list(mgmt_list)
    assertions.assert_team(team)
