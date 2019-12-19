import json

import util

# Writing emojis polarity to file
with open('../common/data/annotated/emojis.json', 'w') as file:
    json.dump(util.load_emoji_classification('../common/data/external/Emoji_Sentiment_Data_v1.0.csv'), file)

# Loading dictionnaries from files
with open('../common/data/annotated/hashtags.json', 'r') as file:
    dict_hashtags = json.load(file)

with open('../common/data/annotated/words.json', 'r') as file:
    dict_words = json.load(file)

with open('../common/data/annotated/emojis.json', 'r') as file:
    dict_emojis = json.load(file)

heavy_negatives_list = util.load_list_from_file('../common/data/annotated/heavy_negatives.txt')
mildly_heavy_negatives_list = util.load_list_from_file('../common/data/annotated/midly_heavy_negatives.txt')

# print(midly_heavy_negatives_list)

# dict_hashtags = {'#irrespect': "negatif", "#2017LeDebat": "neutre", "#Joie": "positif"}
# dict_words = {'pute': "negatif", "content": "positif"}
dict_date = {}

dict_correspondances = {
    "positif": 1,
    "negatif": -1,
    "neutre": 0
}

data = util.get_all_tweets()
# data = util.get_all_unique_tweets()

tweets_polarity = {}

cptEmoji = 0

# Flags pour sélectionner quels critères utiliser
hand_annotated_words_lists_flag = True
hand_annotated_hashtags_lists_flag = True
emojis_flag = True
words_flag = True

seuil_mots = 4

for tweet in data:
    # print(tweet['_source']['message'])
    tweet_polarity = "neutre"

    ########### Message ###########
    isChanged = False

    message = tweet['_source']['message']

    # Get emojis
    message_emojis = util.get_emojis(message)

    message_clean = util.clean_message(message)

    message_clean_splitted = message_clean.split()
    message_clean_splitted = util.remove_elisions(message_clean_splitted)

    is_annotated = False
    if hand_annotated_words_lists_flag is True:
        for mot in message_clean_splitted:
            if mot in heavy_negatives_list:
                tweet_polarity = "negatif"
                is_annotated = True
            elif mot in mildly_heavy_negatives_list:
                tweet_polarity = "negatif"
                is_annotated = True

    if is_annotated is False:
        message_clean = util.lemmatize(message_clean_splitted)

        ########### Hashtags ###########
        if hand_annotated_hashtags_lists_flag is True:
            score_hashtag = 0
            hashtags = tweet['_source']['hashtags']
            for curHashtagDict in hashtags:
                if curHashtagDict is not False:
                    currentHashtag = curHashtagDict.get("text")
                    if dict_hashtags.get(currentHashtag) is not None:
                        score_hashtag += int(dict_correspondances.get(dict_hashtags.get(currentHashtag)))
            if score_hashtag is not 0:
                tweet_polarity = util.get_polarity_from_score(score_hashtag)
                is_annotated = True

        if is_annotated is False:
            score_tweet = 0
            ########### Emojis ###########
            if emojis_flag is True:
                score_emoji = 0
                for emoji in message_emojis:
                    if dict_emojis.get(emoji) is not None:
                        # score_emoji += int(dict_correspondances.get(dict_emojis.get(emoji)))
                        score_tweet += int(dict_correspondances.get(dict_emojis.get(emoji)))

                    if score_tweet is not 0:
                        # tweet_polarity = util.get_polarity_from_score(score_emoji)
                        # is_annotated = True
                        cptEmoji += 1

            ########### Mots ###########
            if words_flag is True:
                poids = 0
                found_words_count = 0
                for mot in message_clean:
                    if dict_words.get(mot) is not None:
                        poids += int(dict_correspondances.get(dict_words.get(mot)))
                        found_words_count += 1
                        if found_words_count >= seuil_mots:
                            score_tweet += poids
                        if poids is not 0:
                            isChanged = True

            # Sauvegarde du score final du tweet
            if isChanged is False:
                tweet_polarity = "neutre"
                is_annotated = True
            else:
                tweet_polarity = util.get_polarity_from_score(score_tweet)
                is_annotated = True

    if is_annotated is True:
        tweets_polarity[tweet['_id']] = tweet_polarity

print("Number of tweets annotated: {}".format(len(tweets_polarity)))

with open('../common/data/annotated/apprentissage.json', 'w') as file:
    json.dump(tweets_polarity, file)


################################ Notes:
# Emojis seuls: très peu efficace. Problème: emojis avec doubles polarités (emoji qui pleure de rire par exemple).
# Emojis + FEEL: peu efficace, trop de positifs