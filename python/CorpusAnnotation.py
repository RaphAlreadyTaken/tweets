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

tweets_polarity = {}

cptMot = 0
cptEmoji = 0
# cptTweetAvecEmoji = 0

# Flags pour sélectionner quels critères utiliser
hand_annotated_words_lists_flag = False
hand_annotated_hashtags_lists_flag = False
emojis_flag = True
words_flag = False

seuil_mots = 2

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
                # print(message_clean)
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
            ########### Emojis ###########
            if emojis_flag is True:
                score_emoji = 0
                for emoji in message_emojis:
                    if dict_emojis.get(emoji) is not None:
                        score_emoji += int(dict_correspondances.get(dict_emojis.get(emoji)))
                    if score_emoji is not 0:
                        tweet_polarity = util.get_polarity_from_score(score_emoji)
                        is_annotated = True
                        cptEmoji += 1

            if is_annotated is False:
                ########### Mots ###########
                if words_flag is True:
                    score_mot = 0
                    poids = 0
                    found_words_count = 0
                    for mot in message_clean:
                        if dict_words.get(mot) is not None:
                            poids = int(dict_correspondances.get(dict_words.get(mot)))
                            score_mot += poids
                            if poids is not 0:
                                isChanged = True

                # Sauvegarde du score final du tweet
                if isChanged is False:
                    tweet_polarity = "neutre"
                else:
                    tweet_polarity = util.get_polarity_from_score(score_mot)

    # if tweet_score is not 0:
    #     print(tweet_score)

    if is_annotated is True:
        tweets_polarity[tweet['_id']] = tweet_polarity
    # print(message_clean)

# print(cptMot)
# print(cptCount2)

# print(tweets_polarity)
print(cptEmoji)
# print(cptTweetAvecEmoji)

with open('../common/data/annotated/apprentissage.json', 'w') as file:
    json.dump(tweets_polarity, file)


################################ Notes:
# Emojis seuls: très peu efficace. Problème: emojis avec doubles polarités (emoji qui pleure de rire par exemple).