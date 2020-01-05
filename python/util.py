import ast
import csv
import json
import re

import demoji
import pandas as pd
import spacy as spacy
from elasticsearch import Elasticsearch, exceptions
from spacy.lang.fr import French

import CorpusVectorization

demoji.download_codes()


# Regex for emoticons: http://sentiment.christopherpotts.net/tokenizing.html
# Code original (avant modifs): https://kb.objectrocket.com/elasticsearch/how-to-use-python-to-make-scroll-queries-to-get-all-documents-in-an-elasticsearch-index-752

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

    return tweets


def process_lexicon(lemm=True):
    print("Loading lemmatizer...")
    lemmatizer = spacy.load("fr_core_news_md")
    print("Lemmatizer loaded\n")
    formatted_words = {}

    print("Processing lexicon...")
    with open("../common/data/external/FEEL.csv", "r", encoding="utf-8") as file:
        csv_reader = csv.reader(file, delimiter=";")
        next(csv_reader)  # Ignore first line (headers)

        for row in csv_reader:
            word = row[1]
            words = []

            # Si mot unique
            if word.find(" ") == -1:
                word = word.lower()
                # Si entrée polymorphique
                if word.find("|") != -1:
                    # Split des mots
                    word_list = word.split("|")
                    for w in word_list:
                        words.append(w)
                else:
                    words.append(word)

                # Ajout au dictionnaire de mots
                for wo in words:
                    if lemm:
                        wo = lemmatize(wo, lemmatizer)

                    formatted_words[str(wo[0])] = row[2]
    print("Lexicon processed\n")

    print("Writing lexicon to file...")
    with open("../common/data/annotated/words_lemmatized.json", "w", encoding="utf-8") as file:
        json.dump(formatted_words, file, sort_keys=True, indent=4)
    print("Lexicon written\n")


def remove_punctuation(message):
    # Removing chars
    retour = message.replace(',', ' ')
    retour = retour.replace(':', ' ')
    retour = retour.replace('(', ' ')
    retour = retour.replace(')', ' ')
    retour = retour.replace('[', ' ')
    retour = retour.replace(']', ' ')
    retour = retour.replace(';', ' ')
    retour = retour.replace('+', ' ')
    retour = retour.replace('/', ' ')
    retour = retour.replace('=', ' ')
    retour = retour.replace('"', ' ')

    # Surround chars with blank spaces
    retour = retour.replace('.', ' . ')
    retour = retour.replace('?', ' ? ')
    retour = retour.replace('!', ' ! ')

    return retour


def remove_hashtag(message):
    return re.sub(r"(#\w+)", '', message)


def remove_username(message):
    return re.sub(r"(@\w+)", '', message)


def remove_url(message):
    return re.sub(r"(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)", '', message)


def remove_elisions(message):
    """Suppression des élisions
    ex: l'arbre, c'était, t'as, ... deviennent arbre, était, as, ...
    """
    for i, s in enumerate(message):
        match = re.search(".'([^\\s]*)", s)

        if match:
            message[i] = match.group(1)

    return message


def lemmatize(message, lemmatizer, nlp):
    """Lemmatisation
        Pour utiliser Spacy :
            pip3 install spacy
            python -m spacy download fr_core_news_md
        """
    # Le message passé est une liste de strings
    if isinstance(message, list):
        str_message = " ".join(message)
        result = lemmatizer(str_message)
    # Le message passé est une phrase
    else:
        result = lemmatizer(message)

    return [x.lemma_ for x in result if not nlp.vocab[x.lemma_].is_stop]


def clean_message_keep_quotes(message):
    retour = remove_hashtag(message)
    retour = remove_username(retour)
    retour = remove_url(retour)
    retour = message.replace(',', ' ')
    retour = retour.replace(':', ' ')

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


def format_message_split(message, lemmatizer):
    retour = remove_elisions(message)
    retour = lemmatize(retour, lemmatizer)
    return retour


def clean_message(message, lemmatizer, nlp):
    message = remove_hashtag(message)
    message = remove_username(message)
    message = remove_url(message)
    message = remove_punctuation(message)

    message = re.sub(' +', ' ', message)  # enlever les multiples espaces
    message = message.strip()  # enlever les trailing spaces

    message = message.lower()  # tout minuscule

    message = message.split()
    message = remove_elisions(message)
    message = lemmatize(message, lemmatizer, nlp)
    return message


def clean_light(message):
    retour = clean_message_light(message)
    retour_split = retour.split()
    retour_split = format_message_split(retour_split)
    return retour_split


def get_messages_as_dict(tweets):
    lemmatizer = spacy.load("fr_core_news_md")
    nlp = French()
    messages = {}

    for i, s in enumerate(tweets):
        get_message_as_dict(s, lemmatizer, nlp)

    return messages


def get_message_as_dict(tweet, lemmatizer, nlp):
    tweet_id = tweet['_id']
    tweet_text = clean_message(tweet['_source']['message'], lemmatizer, nlp)
    return tweet_id, tweet_text


def get_filtered_tweets(unfiltered_tweets):
    lemmatizer = spacy.load("fr_core_news_md")
    nlp = French()
    lexicon = load_extended_lexicon()
    messages = {}

    for i, s in enumerate(unfiltered_tweets):
        tweet_id = s['_id']
        tweet_text = clean_message(s['_source']['message'], lemmatizer, nlp)

        for text in tweet_text:
            if text in lexicon:
                messages[tweet_id] = tweet_text

    return messages


def save_filtered_tweets(filtered_tweets):
    with open("../common/data/processed/unlabeled_filtered.json", "w", encoding="utf-8") as file:
        file.write(json.dumps({int(x): filtered_tweets[x] for x in filtered_tweets.keys()}, indent=4, sort_keys=True))
        # json.dump(filtered_tweets, file, sort_keys=True, indent=4)


def get_message_test_as_dict(tweet, lemmatizer, nlp):
    tweet_id = tweet['_id']
    tweet_text = clean_message(tweet['message'], lemmatizer, nlp)
    return tweet_id, tweet_text


def prepare_learning_data(tweets, model, version):
    formatted_input_data = []
    i = 0

    for tweet_key in tweets.keys():
        print("Preparing tweet {}".format(tweet_key))

        tweet_data = {"id": tweet_key, "message": model.docvecs[i].tolist()}
        formatted_input_data.append(tweet_data)

        i += 1

    with open("../common/data/trained/vectors_v{}.json".format(version), "w", encoding="utf-8") as file:
        json.dump(formatted_input_data, file, indent=4, sort_keys=True)

    return formatted_input_data


def prepare_test_data(tweets):
    lemmatizer = spacy.load("fr_core_news_md")
    nlp = French()
    formatted_input_data = []

    for tweet in tweets:
        print("Preparing tweet {}".format(tweet["_id"]))

        tweet_data = {"id": tweet["_id"]}

        _, tweet_text = get_message_test_as_dict(tweet, lemmatizer, nlp)
        tweet_vectorized = CorpusVectorization.infer_vector(tweet_text)
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
                        if int(row[4]) > int(row[5]):
                            retour[row[0]] = "negatif"
                            max_value = int(row[4])
                        else:
                            retour[row[0]] = "neutre"
                            max_value = int(row[5])
                        if max_value < int(row[6]):
                            retour[row[0]] = "positif"

    return retour


def load_word_classification_ilikeit(filepath):
    retour = {}
    # 2 3 4
    # // colonnes : numéro de ligne ; terme ; # positif ; # neutre ; # négatif
    with open(filepath, 'r', encoding="utf8") as file:
        for line in file:
            line_split = line.split(';')
            if len(line_split) == 5:
                current_word = line_split[1].replace('"', '')
                if int(line_split[2]) > int(line_split[3]):
                    retour[current_word] = "positif"
                    max_value = int(line_split[2])
                else:
                    retour[current_word] = "neutre"
                    max_value = int(line_split[3])
                if max_value < int(line_split[4]):
                    retour[current_word] = "negatif"

    return retour


def load_extended_lexicon():
    nlp = French()

    with open("../common/data/external/Lexique383.csv", "r", encoding="utf-8") as file:
        csv_reader = csv.reader(file, delimiter=";")
        next(csv_reader)  # Ignore first line (headers)

        words = {}

        for row in csv_reader:
            # Si mot unique
            if row[2].find(" ") == -1:
                lexeme = nlp.vocab[row[2]]
                # On ignore les mots vides
                if not lexeme.is_stop:
                    words[row[2]] = None

    print(" Lemmas found: ", len(words))

    return words


def load_list_from_file(filename):
    return_list = [line.rstrip('\n') for line in open(filename, encoding="utf-8")]
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

    print(frequencies)


def filter_negative_words(file):
    lemmatizer = spacy.load("fr_core_news_md")
    nlp = French()
    negatives_list = load_list_from_file(file)
    normalized_negative_list = []
    ignore_list = ["!", "?", " "]

    for message in negatives_list:
        lemmatized = False
        if not any(x in message for x in ignore_list):
            message = lemmatize(message, lemmatizer, nlp)
            lemmatized = True

        if lemmatized:
            if len(message) > 0 and message[0] not in normalized_negative_list:
                normalized_negative_list.append(message[0])
        else:
            if message not in normalized_negative_list:
                normalized_negative_list.append(message)

    with open('{}_filtered.txt'.format(file), 'a+', encoding="utf-8") as file:
        for mot in normalized_negative_list:
            file.write(mot + "\n")


# Main pour effectuer certains traitements
if __name__ == '__main__':
    print("hello")
