import collections
import json
import time

import pandas as pd
from gensim.models.doc2vec import TaggedDocument, Doc2Vec

import util

latest_model = "models/doc2vec/tweet_vectors_1578093577.245187.model"


def configure_model(local_documents):
    print("Configuring and building model")
    docs_to_vectorize = [TaggedDocument(words=tweet_text, tags=[tweet_id]) for tweet_id, tweet_text in
                         local_documents.items()]
    local_model = Doc2Vec(vector_size=200, min_count=1)
    local_model.build_vocab(docs_to_vectorize)
    print("Model ready")
    return local_model, docs_to_vectorize


def train_model(local_model, local_documents, epochs):
    print("Model training")
    local_model.train(local_documents, total_examples=local_model.corpus_count, epochs=epochs)
    print("Model trained")


def save_model(local_model):
    print("Saving model")
    target_path = "models/doc2vec/tweet_vectors_{}.model".format(time.time())
    local_model.save(target_path)
    print("Model saved to", target_path)


def assess_model(local_model, local_documents, taille_eval):
    """ Checks model performance against its training corpus
    https://radimrehurek.com/gensim/auto_examples/tutorials/run_doc2vec_lee.html#sphx-glr-auto-examples-tutorials-run-doc2vec-lee-py
    """
    if taille_eval > 1000:
        print("Warning: assessing models with a large number of vectors can take a long time")

    print("Assessing model")

    ranks = []

    # Pour chaque tweet du corpus d'apprentissage, génération de son vecteur à partir du modèle (inferred_vector).
    # Parcours des vecteurs similaires (classés par similarité dans sims).
    # On cherche la position du tweet de même tweet_id et on récupère son rang (rank).
    # Si le rank est 0, signifie que le vecteur généré par le modèle pour le tweet x est le plus similaire au inferred_vector qu'on vient de générer.
    # Dans le résultat final, on veut vérifier qu'on a un maximum de ranks à 0 ou 1 (tweets similaires à eux-mêmes).
    for tweet_id, tweet_text in local_documents.items():
        inferred_vector = infer_vector(tweet_text)
        sims = local_model.docvecs.most_similar([inferred_vector], topn=len(local_model.docvecs))
        print("Testing tweet {}".format(tweet_id))
        rank = [tweet_id for tweet_id, sim in sims].index(tweet_id)
        ranks.append(rank)

        if tweet_id == str(taille_eval):
            break

    counter = collections.Counter(ranks)
    print("Assessing done. Results: {}".format(counter))


def get_model(model_path):
    return Doc2Vec.load(model_path)


def get_vectors_from_model(local_model):
    return local_model.docvecs.vectors_docs


def infer_vector(tweet_message):
    local_model = get_model(latest_model)
    return local_model.infer_vector(tweet_message)


if __name__ == '__main__':
    tweets = util.get_all_tweets()

    # Filtrage des tweets inutiles
    filtered_tweets = util.get_filtered_tweets(tweets)
    print(len(filtered_tweets))

    util.save_filtered_tweets(filtered_tweets)

    with open("../common/data/processed/unlabeled_filtered.json", "r", encoding="utf-8") as file:
        loaded_filtered_tweets = json.load(file)

    model, documents = configure_model(loaded_filtered_tweets)
    train_model(model, documents, 100)
    save_model(model)

    # model = get_model(latest_model)
    # print(assess_model(model, loaded_filtered_tweets, 1000))

    # print(model.most_similar(positive=["macron"]))

    # vectors = get_vectors_from_model(model)
    # for vector in vectors:
    #     pprint(vector)


