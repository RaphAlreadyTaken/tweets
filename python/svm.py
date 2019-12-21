import json

import spacy

import util

lexique_filename = '../common/data/raw/lexique_svm.json'
test_corpus_filename = "../common/data/raw/test.txt"
out_evaluation_platform_filename = "../common/data/metrics/svm/test_svm_evaluation_platform.txt"

polarity_map = {"negatif": 0, "positif": 1, "mixte": 2, "neutre": 3}

polarity_map_output = {0: "negatif", 1: "positif", 2: "mixte", 3: "autre"}

lemmatizer = spacy.load("fr_core_news_md")


def clean_message(message):
    message_clean = util.clean_message_light(message)
    message_clean_splitted = message_clean.split()
    message_clean_splitted = util.remove_elisions(message_clean_splitted)
    message_clean = util.lemmatize(message_clean_splitted, lemmatizer)

    return message_clean


def load_lexique_from_file():
    with open(lexique_filename, 'r', encoding="utf-8") as file:
        lexique_dict = json.load(file)

    return lexique_dict


def add_learning_corpus_to_lexique():
    data = util.get_all_tweets()

    lexique_dict = load_lexique_from_file()
    lexique_size = 1
    if len(lexique_dict) > 0:
        lexique_size = len(lexique_dict)

    for tweet in data:
        message = tweet['_source']['message']

        # Cleaning message
        message_clean = clean_message(message)

        for word in message_clean:
            if lexique_dict.get(word) is None:
                lexique_dict[word] = lexique_size
                lexique_size += 1

    with open(lexique_filename, 'w', encoding="utf-8") as file:
        json.dump(lexique_dict, file, indent=4)


def add_test_corpus_to_lexique():
    data = []
    with open(test_corpus_filename, 'r', encoding="utf-8") as f:
        for line in f:
            split_line = line.split(" ", 1)
            data.append(split_line[1].rstrip())

    lexique_dict = load_lexique_from_file()

    lexique_size = 1
    if len(lexique_dict) > 0:
        lexique_size = len(lexique_dict)

    for tweet in data:
        # Cleaning message
        message_clean = clean_message(tweet)

        for word in message_clean:
            if lexique_dict.get(word) is None:
                lexique_dict[word] = lexique_size
                lexique_size += 1
                # print(word)

    with open(lexique_filename, 'w', encoding="utf-8") as file:
        json.dump(lexique_dict, file, indent=4)


def message_to_svm_format(message):
    return_str = ""
    lexique_dict = load_lexique_from_file()

    dict_message = {}
    message_unique_words = set(message) #loop through unique elements
    for word in message_unique_words:
        dict_message[lexique_dict.get(word)] = message.count(word)

    for entry in sorted(dict_message):
        return_str += str(entry) + ':' + str(dict_message[entry]) + ' '

    return return_str


def tweets_learning_to_svm_format():
    data_full = util.get_all_tweets()
    with open('../common/data/annotated/apprentissage.json', 'r') as file:
        data_annotated = json.load(file)

    with open('../common/data/annotated/apprentissage_svm.svm', 'w') as svm_file:
        for annotated_tweet in data_annotated:
            # get full tweet with id of annotated tweet's id
            tweet = next(x for x in data_full if x['_id'] == annotated_tweet)
            # get message only
            tweet_message = tweet['_source']['message']
            # Cleaning message
            tweet_message_clean = clean_message(tweet_message)
            print(tweet_message_clean)
            # to get progress
            # print(annotated_tweet)
            svm_file.write(str(polarity_map.get(data_annotated[annotated_tweet])) + ' ' + str(message_to_svm_format(tweet_message_clean)) + '\n')


def test_corpus_to_svm_format():
    data = []
    with open(test_corpus_filename, 'r', encoding="utf-8") as f:
        for line in f:
            split_line = line.split(" ", 1)
            data.append(split_line[1].rstrip())

    with open('../common/data/raw/test_svm.svm', 'w') as svm_file:
        for tweet_message in data:
            # Cleaning message
            tweet_message_clean = clean_message(tweet_message)
            svm_file.write('1 ' + str(message_to_svm_format(tweet_message_clean)) + '\n')


def svm_output_to_evaluation_platform_format(test_out_filename):
    data_ids = []

    with open(test_corpus_filename, 'r', encoding="utf-8") as f:
        for line in f:
            split_line = line.split(" ", 1)
            data_ids.append(split_line[0])

    data_polarities = []
    with open(out_evaluation_platform_filename, 'w', encoding="utf-8") as output_file:
        with open(test_out_filename, 'r', encoding="utf-8") as f:
            line = f.readline()
            while line:
                data_polarities.append(line)
                line = f.readline()

        for index, id in enumerate(data_ids):
            output_file.write(str(id) + ' ' + polarity_map_output.get(int(data_polarities[index])) + '\n')


if __name__ == '__main__':

    # Create lexicon
    # add_learning_corpus_to_lexique()
    # add_test_corpus_to_lexique()

    # Format learning corpus (very long to execute)
    tweets_learning_to_svm_format()

    # Format test corpus
    # test_corpus_to_svm_format()

    # Format svm output to use file on evaluation platform
    # svm_output_to_evaluation_platform_format('../common/data/metrics/svm/out_svm.txt')


# Train model: liblinear-2.30/train -c 4 -e 0.1 common/data/annotated/apprentissage_svm.svm python/models/svm/tweets.model
# Predict: liblinear-2.30/predict common/data/raw/test_svm.svm python/models/svm/tweets.model common/data/metrics/svm/out_svm.txt