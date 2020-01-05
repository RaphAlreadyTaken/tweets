import json
import re

import spacy
from spacy.lang.fr import French

import util

# Writing emojis polarity to file
with open('../common/data/annotated/emojis.json', 'w') as file:
    json.dump(util.load_emoji_classification('../common/data/external/Emoji_Sentiment_Data_v1.0.csv'), file)

# Loading dictionnaries from files
with open('../common/data/annotated/hashtags.json', 'r') as file:
    dict_hashtags = json.load(file)

with open('../common/data/annotated/words_lemmatized.json', 'r', encoding="utf-8") as file:
    dict_words = json.load(file)

# "Like it"
# dict_words = util.load_word_classification_ilikeit('../common/data/external/06032019-POLARITY-JEUXDEMOTS-FR.csv')

with open('../common/data/annotated/emojis.json', 'r') as file:
    dict_emojis = json.load(file)


heavy_negatives_list = util.load_list_from_file('../common/data/annotated/heavy_negatives_filtered.txt')
mildly_heavy_negatives_list = util.load_list_from_file('../common/data/annotated/midly_heavy_negatives_filtered.txt')
dict_date = {}

dict_correspondances = {
    "positif": 1,
    "negatif": -1,
    "neutre": 0
}

# data = util.get_all_tweets()
data = util.get_all_unique_tweets()

tweets_polarity = {}

cpt_neg_words = 0
cpt_hashtags = 0
cpt_emojis = 0
cpt_quotes = 0
cpt_other_words = 0
cpt_other = 0

cpt_positive = 0
cpt_negative = 0
cpt_mixte = 0
cpt_neutre = 0

# Flags pour sélectionner quels critères utiliser
hand_annotated_words_lists_flag = True
hand_annotated_hashtags_lists_flag = True
emojis_flag = True
quotes_flag = True
words_flag = True

seuil_mots = 2

lemmatizer = spacy.load("fr_core_news_md")
nlp = French()

for tweet in data:
    print("Annotating tweet {}".format(tweet["_id"]))
    tweet_polarity = ""

    ########### Message ###########
    message = tweet['_source']['message']

    # Get emojis
    message_emojis = util.get_emojis(message)

    message_almost_clean = util.clean_message_keep_quotes(message)
    message_clean = util.clean_message(message, lemmatizer, nlp)
    message_clean = util.remove_elisions(message_clean)

    is_annotated = False

    ########### Quotes ###########
    if is_annotated is False:
        if quotes_flag is True:
            match = re.search("^\"[^\"]*\"$", message_almost_clean)
            if match:
                tweet_polarity = "neutre"
                is_annotated = True
                cpt_quotes += 1

    ########### Negative words ###########
    if is_annotated is False:
        if hand_annotated_words_lists_flag is True:
            for mot in message_clean:
                if mot in heavy_negatives_list or mot in mildly_heavy_negatives_list:
                    tweet_polarity = "negatif"
                    is_annotated = True
                    break

            if is_annotated is True:
                cpt_neg_words += 1

    ########### Hashtags ###########
    if is_annotated is False:
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
                cpt_hashtags += 1

    ########### Emojis ###########
    if is_annotated is False:
        if emojis_flag is True:
            score_emoji = 0

            for emoji in message_emojis:
                if dict_emojis.get(emoji) is not None:
                    score_emoji += int(dict_correspondances.get(dict_emojis.get(emoji)))

            if score_emoji is not 0:
                tweet_polarity = util.get_polarity_from_score(score_emoji)
                is_annotated = True
                cpt_emojis += 1

    ########### Mots ###########
    if is_annotated is False:
        if words_flag is True:
            message_clean = util.lemmatize(message_clean, lemmatizer, nlp)
            score_message = 0  # Score global du message
            pos_mod = []  # Indicateur de modification positive du message
            neg_mod = []  # Indicateur de modification négative du message

            # Pour chaque mot du tweet
            for mot in message_clean:
                # On trouve le mot dans le dictionnaire FEEL
                if dict_words.get(mot):
                    new_score_message = score_message + int(dict_correspondances.get(dict_words.get(mot)))

                    # Si le nouveau score est plus élevé que l'ancien
                    if new_score_message > score_message:
                        pos_mod.append(True)
                    # Si le nouveau score est moins élevé que l'ancien
                    else:
                        neg_mod.append(True)

                    # Assignation de valeur pour itération suivante
                    score_message = new_score_message

            # Modifications du score dans les 2 sens
            if len(pos_mod) > 1 and len(neg_mod) > 1:
                tweet_polarity = "mixte"
                is_annotated = True
                cpt_other_words += 1
                cpt_mixte += 1
            # Modifications dans un sens + valeur absolue du score supérieure au seuil de prise en compte
            # TODO : plus de poids aux négatifs
            elif len(pos_mod) == 0 or len(neg_mod) == 0:
                if abs(score_message) >= seuil_mots:
                    tweet_polarity = util.get_polarity_from_score(score_message)
                    is_annotated = True
                    cpt_other_words += 1

    if is_annotated is True:
        tweets_polarity[tweet['_id']] = tweet_polarity

        if tweet_polarity == "negatif":
            cpt_negative += 1
        elif tweet_polarity == "positif":
            cpt_positive += 1
        else:
            cpt_neutre += 1

    else:
        tweets_polarity[tweet['_id']] = "neutre"
        cpt_other += 1
        cpt_neutre += 1

total_annotated = cpt_neg_words + cpt_hashtags + cpt_emojis + cpt_quotes + cpt_other_words + cpt_other

print("Number of tweets annotated: {}".format(total_annotated))
print("--- Number of tweets annotated thanks to negative words: {}".format(cpt_neg_words))
print("--- Number of tweets annotated thanks to hashtags: {}".format(cpt_hashtags))
print("--- Number of tweets annotated thanks to emojis: {}".format(cpt_emojis))
print("--- Number of tweets annotated thanks to quotes: {}".format(cpt_quotes))
print("--- Number of tweets annotated thanks to other words: {}".format(cpt_other_words))
print("--- Number of tweets annotated by default: {}".format(cpt_other))

print()

if len(tweets_polarity) != total_annotated:
    print("WARNING: number of annotated tweets ({}) does not match annotated tweet list size ({})!".format(
        total_annotated, len(tweets_polarity)))

print()

print("Number of negative tweets: {}".format(cpt_negative))
print("Number of positive tweets: {}".format(cpt_positive))
print("Number of mixed tweets: {}".format(cpt_mixte))
print("Number of neutral tweets: {}".format(cpt_neutre))

with open('../common/data/annotated/apprentissage.json', 'w') as file:
    json.dump(tweets_polarity, file)
