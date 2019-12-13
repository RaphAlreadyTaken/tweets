import util
import re

# 0: neutre
# 1: positif
# 2: négatif
# 3: mixte

dict_hashtags = {'#irrespect': 2}
dict_words = {'pute': 2}
dict_date = {}

data = util.get_all_tweets()
for tweet in data:
    # print(tweet['_source']['message'])
    tweet_score = 0

    message = tweet['_source']['message']
    message_clean = util.clean_message(message)
    message_clean_splitted = message_clean.split()

    for mot in message_clean_splitted:
        if dict_words.get(mot) == 0:
            print("coucou")


    # print(message_clean_splitted_no)
    # print(message_clean)
    # for mot in message_clean_splitted_no:
        # print(mot)
    # for mot in message_split:
    #     print(mot)
    # print("nouveau tweet")
    # if(tweet)