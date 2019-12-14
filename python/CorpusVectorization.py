import time
from pprint import pprint

from gensim.models.doc2vec import TaggedDocument, Doc2Vec

import util


def configure_model(local_documents):
    print("Configuring and building model")
    docs_to_vectorize = [TaggedDocument(tweet_text, tweet_id) for tweet_id, tweet_text in local_documents.items()]
    local_model = Doc2Vec(vector_size=100, min_count=2)
    local_model.build_vocab(docs_to_vectorize)
    print("Model ready")
    return local_model, docs_to_vectorize


def train_model(local_model, local_documents, epochs):
    print("Model training")
    local_model.train(local_documents, total_examples=local_model.corpus_count, epochs=epochs)
    print("Model trained")


def save_model(local_model):
    print("Saving model")
    target_path = "models/tweet_vectors_{}.model".format(time.time())
    local_model.save(target_path)
    print("Model saved to {}".format(target_path))


def get_vectors_from_model(model_path):
    local_model = Doc2Vec.load(model_path)
    return local_model.docvecs


if __name__ == '__main__':
    # tweet_messages = util.get_messages_as_dict()
    # model, documents = configure_model(tweet_messages)
    # train_model(model, documents, 100)
    # save_model(model)

    vectors = get_vectors_from_model("models/tweet_vectors_1576343839.7709334.model")

    for vector in vectors:
        pprint(vector)
