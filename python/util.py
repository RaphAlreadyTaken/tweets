import json
import re
import nltk

from elasticsearch import Elasticsearch, exceptions
from nltk import SnowballStemmer

from CorpusVectorization import infer_vector

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


def remove_punctuation(message):
    retour = message.replace(',', ' ')
    retour = retour.replace(':', ' ')
    retour = retour.replace('.', ' . ')
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


def format_message_split(message):
    retour = remove_elisions(message)
    retour = lemmatize(retour)
    return retour


def clean_full(message):
    retour = clean_message(message)
    retour_split = retour.split()
    retour_split = format_message_split(retour_split)
    return retour_split


def get_messages_as_dict(tweets):
    messages = {}

    for i, s in enumerate(tweets):
        tweet_id, tweet_text = get_message_as_dict(s)
        messages[tweet_id] = tweet_text

    return messages


def get_message_as_dict(tweet):
    tweet_id = tweet['_id']
    tweet_text = clean_full(tweet['_source']['message'])
    return tweet_id, tweet_text


# TODO : écrire dans un fichier (long)
def prepare_learning_data(tweets):
    formatted_input_data = []

    for tweet in tweets:
        print("Preparing tweet {}".format(tweet["_id"]))

        tweet_data = {"id": tweet["_id"]}

        _, tweet_text = get_message_as_dict(tweet)
        tweet_vectorized = infer_vector(tweet_text)
        tweet_data["message"] = tweet_vectorized

        # TODO : voir si utile (pas présent dans corpus de test)
        # tweet_data["username"] = tweet["_source"]["username"]

        # tweet_data["hashtags"] = []
        #
        # for hashtag in tweet["_source"]["hashtags"]:
        #     tweet_data["hashtags"].append(hashtag["text"])

        # TODO : voir si utile (pas présent dans corpus de test)
        # tweet_data["date"] = tweet["_source"]["date"]

        # TODO : appeler méthode permettant d'extraire les emojis
        tweet_data["emojis"] = 0

        formatted_input_data.append(tweet_data)

        # TODO: temporaire, à supprimer
        if tweet["_id"] == "10":
            break

    return formatted_input_data
