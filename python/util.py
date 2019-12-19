import ast
import csv
import json
import re

import demoji
import nltk
import pandas as pd
from elasticsearch import Elasticsearch, exceptions
from nltk import SnowballStemmer

from CorpusVectorization import infer_vector

demoji.download_codes()
nltk.download("stopwords")


# Regex for emoticons: http://sentiment.christopherpotts.net/tokenizing.html
# Code original (avant modifs): https://kb.objectrocket.com/elasticsearch/how-to-use-python-to-make-scroll-queries-to-get-all-documents-in-an-elasticsearch-index-752


# TODO : écrire sur disque (long à relancer à chaque fois)
def get_all_tweets():
    # declare globals for the Elasticsearch client host
    DOMAIN = "localhost"
    PORT = 9200

    # concatenate a string for the client's host parameter
    host = str(DOMAIN) + ":" + str(PORT)

    # declare an instance of the Elasticsearch library
    client = Elasticsearch(host)

    try:
        # use the JSON library's dump() method for indentation
        info = json.dumps(client.info(), indent=4)

    except exceptions.ConnectionError as err:
        # print ConnectionError for Elasticsearch
        print("\nElasticsearch info() ERROR:", err)
        print("\nThe client host:", host, "is invalid or cluster is not running")

        # change the client's value to 'None' if ConnectionError
        client = None

    # valid client instance for Elasticsearch
    if client is not None:
        match_all = {
            "size": 100,
            "query": {
                "match_all": {}
            }
        }

        # make a search() request to get all docs in the index
        resp = client.search(
            index="tweet",
            body=match_all,
            scroll='10s'
        )

        # keep track of pass scroll _id
        old_scroll_id = resp['_scroll_id']

        retour = []

        # stockage 100 premiers
        for doc in resp['hits']['hits']:
            retour.append(doc)

        # use a 'while' iterator to loop over document 'hits'
        while len(resp['hits']['hits']):
            # make a request using the Scroll API
            resp = client.scroll(
                scroll_id=old_scroll_id,
                scroll='10s'  # length of time to keep search context
            )
            # keep track of pass scroll _id
            old_scroll_id = resp['_scroll_id']

            # iterate over the document hits for each 'scroll'
            for doc in resp['hits']['hits']:
                retour.append(doc)
        return retour


def get_all_unique_tweets():
    tweets = get_all_tweets()
    original_size = len(tweets)
    messages = []

    for i, s in enumerate(tweets):
        message = s["_source"]["message"]
        if message in messages:
            tweets.pop(i)
        else:
            messages.append(message)

    final_size = len(tweets)

    print("Original tweet number: {}".format(original_size))
    print("Duplicates removed: {}".format(original_size - final_size))
    print("Final tweet number: {}".format(final_size))

    with open("../common/data/processed/unlabeled_unique.json", "w", encoding="utf8") as file:
        json.dump(tweets, file, indent=4, sort_keys=True)


def remove_punctuation(message):
    retour = message.replace(',', ' ')
    retour = retour.replace(':', ' ')
    retour = retour.replace('.', ' . ')
    retour = retour.replace('"', ' " ')
    return retour


def remove_hashtag(message):
    return re.sub(r"(#\w+)", '', message)


def remove_username(message):
    return re.sub(r"(@\w+)", '', message)


def remove_url(message):
    return re.sub(r"(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)", '', message)


def remove_elisions(message):
    """Suppression des élisions
    ex: l'arbre, c'était, t'as, ... deviennent arbre, était, as, ... (voir si on peut faire plus propre)
    """
    for i, s in enumerate(message):
        match = re.search(".'([^\\s]*)", s)

        if match:
            message[i] = match.group(1)

    return message


def lemmatize(message):
    """Lemmatisation
    Le dictionnaire de correspondances doit être également lemmatisé avec Snowball
    (adaptation de Porter Stemmer en français)
    """
    stemmer = SnowballStemmer("french", ignore_stopwords=True)
    return [stemmer.stem(x) for x in message]


def clean_message(message):
    retour = remove_hashtag(message)
    retour = remove_username(retour)
    retour = remove_url(retour)
    retour = remove_punctuation(retour)

    retour = re.sub(' +', ' ', retour)  # enlever les multiples espaces
    retour = retour.strip()  # enlever les trailing spaces

    retour = retour.lower()  # tout minuscule

    return retour


def clean_message_light(message):
    retour = remove_username(message)
    retour = remove_url(retour)
    retour = remove_punctuation(retour)
    retour = retour.replace('.', ' ')

    retour = re.sub(' +', ' ', retour)  # enlever les multiples espaces
    retour = retour.strip()  # enlever les trailing spaces

    retour = retour.lower()  # tout minuscule

    return retour


def format_message_split(message):
    retour = remove_elisions(message)
    retour = lemmatize(retour)
    return retour


def clean_full(message):
    retour = clean_message(message)
    retour_split = retour.split()
    retour_split = format_message_split(retour_split)
    return retour_split


def clean_light(message):
    retour = clean_message_light(message)
    retour_split = retour.split()
    retour_split = format_message_split(retour_split)
    return retour_split


def get_messages_as_dict(tweets):
    messages = {}

    for i, s in enumerate(tweets):
        tweet_id, tweet_text = get_message_as_dict(s)
        messages[tweet_id] = tweet_text

    return messages


def get_messages_full_as_dict(tweets):
    messages = {}

    for i, s in enumerate(tweets):
        tweet_id, tweet_text = get_message_full_as_dict(s)
        messages[tweet_id] = tweet_text

    return messages


def get_message_as_dict(tweet):
    tweet_id = tweet['_id']
    tweet_text = clean_full(tweet['_source']['message'])
    return tweet_id, tweet_text


def get_message_test_as_dict(tweet):
    tweet_id = tweet['_id']
    tweet_text = clean_full(tweet['message'])
    return tweet_id, tweet_text


def get_message_full_as_dict(tweet):
    tweet_id = tweet['_id']
    tweet_text = clean_light(tweet['_source']['message'])
    return tweet_id, tweet_text


def get_message_test_full_as_dict(tweet):
    tweet_id = tweet['_id']
    tweet_text = clean_light(tweet['message'])
    return tweet_id, tweet_text


def prepare_learning_data(tweets):
    formatted_input_data = []

    for tweet in tweets:
        print("Preparing tweet {}".format(tweet["_id"]))

        tweet_data = {"id": tweet["_id"]}

        _, tweet_text = get_message_as_dict(tweet)
        tweet_vectorized = infer_vector(tweet_text)
        tweet_data["message"] = pd.Series(tweet_vectorized).to_json(orient='values')
        formatted_input_data.append(tweet_data)

    with open('../common/data/trained/vectors.json', 'w', encoding="utf-8") as file:
        json.dump(formatted_input_data, file)

    return formatted_input_data


def prepare_learning_data_full(tweets):
    formatted_input_data = []

    for tweet in tweets:
        print("Preparing tweet {}".format(tweet["_id"]))

        tweet_data = {"id": tweet["_id"]}

        _, tweet_text = get_message_full_as_dict(tweet)
        tweet_vectorized = infer_vector(tweet_text)
        tweet_data["message"] = ast.literal_eval(pd.Series(tweet_vectorized).to_json(orient='values'))
        formatted_input_data.append(tweet_data)

    with open('../common/data/trained/vectors.json', 'w', encoding="utf-8") as file:
        json.dump(formatted_input_data, file)

    return formatted_input_data


def prepare_test_data_full(tweets):
    formatted_input_data = []

    for tweet in tweets:
        print("Preparing tweet {}".format(tweet["_id"]))

        tweet_data = {"id": tweet["_id"]}

        _, tweet_text = get_message_test_full_as_dict(tweet)
        tweet_vectorized = infer_vector(tweet_text)
        tweet_data["message"] = ast.literal_eval(pd.Series(tweet_vectorized).to_json(orient='values'))
        formatted_input_data.append(tweet_data)

    with open('../common/data/trained/vectors_test.json', 'w', encoding="utf-8") as file:
        json.dump(formatted_input_data, file)

    return formatted_input_data


# Source: https://pypi.org/project/demoji/
def get_emojis(message):
    # # Regex to match emojis
    # regex_emoji = re.compile("(\u00a9|\u00ae|[\u2000-\u3300]|\ud83c[\ud000-\udfff]|\ud83d[\ud000-\udfff]|\ud83e[\ud000-\udfff])")
    #
    # ### Cleaning
    # message = message.replace("’", '')
    # message = message.replace(u"\u2026", '') # remove "..." unicode char
    # message = message.replace(u"\u2013", '') # remove "–" unicode char
    # message = message.replace(u"\u2014", '') # remove "–" unicode char
    #
    # # Split non separated emojis
    # message_splitted = list(x for x in regex_emoji.split(message) if x != '')
    #
    # # Return list of emojis
    # retour = [i for i in message_splitted if regex_emoji.match(i)]

    retour = list(demoji.findall(message).keys())

    return retour


def load_emoji_classification(filepath):
    retour = {}
    seuil = 50
    with open(filepath, 'r', encoding="utf8") as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] != 'Emoji':
                if int(row[2]) > seuil:
                    current_cat = row[8]
                    if current_cat == 'Emoticons' or \
                            current_cat == 'Dingbats' or \
                            current_cat == 'Miscellaneous Symbols' or \
                            current_cat == 'Miscellaneous Symbols and Pictographs':
                        print(current_cat)
                        if int(row[4]) > int(row[5]):
                            retour[row[0]] = "negatif"
                            max_value = int(row[4])
                        else:
                            retour[row[0]] = "neutre"
                            max_value = int(row[5])
                        if max_value < int(row[6]):
                            retour[row[0]] = "positif"

    return retour


def load_list_from_file(filename):
    return_list = [line.rstrip('\n') for line in open(filename)]
    return return_list


def get_polarity_from_score(score):
    if score > 0:
        return "positif"
    elif score < 0:
        return "negatif"
    else:
        return "mixte"


def get_word_frequencies():
    tweets = get_all_tweets()
    words = get_messages_as_dict(tweets)
    frequencies = {}

    for word in words.values():
        for w in word:
            if w in frequencies:
                frequencies[w] += 1
            else:
                frequencies[w] = 0

    frequencies = sorted(frequencies.items(), key=lambda x: x[1], reverse=True)

    # Fucking fuck encoding
    print(frequencies)
