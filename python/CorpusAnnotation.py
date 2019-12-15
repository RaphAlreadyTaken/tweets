import json

import util

with open('../java/src/fr/ceri/data/annotated/hashtags.json', 'r') as file:
    dict_hashtags = json.load(file)

with open('../java/src/fr/ceri/data/annotated/words.json', 'r') as file:
    dict_words = json.load(file)

# dict_hashtags = {'#irrespect': "negatif", "#2017LeDebat": "neutre", "#Joie": "positif"}
# dict_words = {'pute': "negatif", "content": "positif"}
dict_date = {}

dict_correspondances = {
    "positif": 1,
    "negatif": -1,
    "neutre": 0
}

data = util.get_all_tweets()

tweets_polarity = {}

for tweet in data:
    # print(tweet['_source']['message'])
    tweet_score = 0
    tweet_polarity = "neutre"

    ########### Message ###########
    isChanged = False

    message = tweet['_source']['message']
    message_clean = util.clean_message(message)

    message_clean_splitted = message_clean.split()
    message_clean = util.format_message_split(message_clean_splitted)

    for mot in message_clean:
        if dict_words.get(mot) is not None:
            poids = int(dict_correspondances.get(dict_words.get(mot)))
            tweet_score += poids
            if poids is not 0:
                isChanged = True

    ########### Hashtags ###########
    hashtags = tweet['_source']['hashtags']
    for curHashtagDict in hashtags:
        if curHashtagDict is not False:
            currentHashtag = curHashtagDict.get("text")
            if dict_hashtags.get(currentHashtag) is not None:
                poids = int(dict_correspondances.get(dict_hashtags.get(currentHashtag)))
                tweet_score += poids
                if poids is not 0:
                    isChanged = True

    # if tweet_score is not 0:
    #     print(tweet_score)

    # Sauvegarde du score final du tweet
    if isChanged is False:
        tweet_polarity = "neutre"
    elif tweet_score > 0:
        tweet_polarity = "positif"
    elif tweet_score < 0:
        tweet_polarity = "negatif"
    else:
        tweet_polarity = "mixte"

    tweets_polarity[tweet['_id']] = tweet_polarity
    print(message_clean)

print(tweets_polarity)

with open('../java/src/fr/ceri/data/annotated/apprentissage.json', 'w') as file:
    json.dump(tweets_polarity, file)
