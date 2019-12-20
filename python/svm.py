import json
import util

lexique_filename = '../common/data/raw/lexique_svm.json'
test_corpus_filename = "../common/data/raw/test.txt"

polarity_map = {"negatif": 0, "positif": 1, "mixte": 2, "neutre": 3}

def clean_message(message):
    message_clean = util.clean_message_light(message)
    message_clean_splitted = message_clean.split()
    message_clean_splitted = util.remove_elisions(message_clean_splitted)
    message_clean = util.lemmatize(message_clean_splitted)

    return message_clean

def load_lexique_from_file():
    with open(lexique_filename, 'r', encoding="utf-8") as file:
        lexique_dict = json.load(file)

    return lexique_dict


def add_learning_corpus_to_lexique():
    data = util.get_all_tweets()

    lexique_dict = load_lexique_from_file()

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


def tweets_to_svm_format():
    lexique_dict = load_lexique_from_file()
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
            print(annotated_tweet)
            svm_file.write(str(polarity_map.get(data_annotated[annotated_tweet])) + ' ' + str(message_to_svm_format(tweet_message_clean)) + '\n')


if __name__ == '__main__':

    # add_learning_corpus_to_lexique()
    # print("Entering 2nd method")
    # add_test_corpus_to_lexique()
    tweets_to_svm_format()