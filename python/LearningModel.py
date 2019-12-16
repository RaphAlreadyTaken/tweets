import json
import os
from math import floor

from keras import Sequential, metrics
from keras.engine.saving import load_model
from keras.layers import Dense

import util

model_dir = "models\\keras"
best_model_dir = model_dir + "\\overall_best"
best_model_path = model_dir + best_model_dir + "\\best_model.hdf5"

output_classes = ["negatif", "positif", "mixte", "autre"]


def configure_model(input_size, output_size):
    """Creates and configures the model

    :param input_size:  number of input attributes
    :param output_size: number of output classes
    :return: the created model
    """

    local_model = Sequential()
    local_model.add(Dense(100, input_dim=input_size, activation="relu"))

    for i in range(7):
        local_model.add(Dense(100, activation="relu"))

    local_model.add(Dense(output_size, activation="softmax"))

    local_model.compile(loss="sparse_categorical_crossentropy", optimizer="Adam",
                        metrics=[metrics.SparseCategoricalAccuracy()])

    return local_model


def find_best_model(test_data, test_output):
    """Tests all models and find the highest accuracy one

    :param test_data:   test dataset
    :param test_output: test output values
    :return: the best model
    """
    max_accuracy = 0
    best_model = None

    # Evaluate all models
    for file in os.listdir(model_dir):
        file_path = os.path.join(model_dir, file)

        if os.path.isfile(file_path):
            local_model = load_model(file_path)

            # Run model (evaluation)
            score = local_model.evaluate(test_data, test_output, verbose=0)
            print("Scores for model {}:".format(file))
            print("Test score:", score[0])
            print("Test accuracy:", score[1])
            print("\n")

            # Better score found → update best model
            if score[1] > max_accuracy:
                max_accuracy = score[1]
                best_model = local_model

    # Evaluate against current best model
    if os.path.exists(best_model_path):
        cur_best_model = load_model(best_model_path)
        # TODO: find test data
        score_best = cur_best_model.evaluate(test_data, test_output, verbose=0)

        # Better score found → update best model
        if score_best[1] > max_accuracy:
            best_model = cur_best_model

    print("Best model found with {} accuracy".format(max_accuracy))

    return best_model


def save_best_model(local_model):
    """Saves the model to its designated path

    :param local_model: model to save
    """
    local_model.save(best_model_path)


def display_model(local_model):
    """Displays a model summary

    :param local_model: the model to display
    """
    print(local_model.summary())


def display_best_model():
    """Retrieves the best model from its designated path and displays it
    """
    best_model = load_model(best_model_path)
    display_model(best_model)


def display_models():
    """Display all models
    """
    for file in os.listdir(model_dir):
        file_path = os.path.join(model_dir, file)

        if os.path.isfile(file_path):
            local_model = load_model(os.path.join(model_dir, file))
            display_model(local_model)


def dispatch_data(dataset, outputset):
    # Data size
    taille = len(dataset)

    # Sub-datasets allocation
    training_size = floor(taille * 0.8)
    validation_size = floor(taille * 0.2)

    # Dataset split
    local_training_data = dataset[:training_size]
    local_validation_data = dataset[training_size + 1: training_size + validation_size]

    local_training_output = []
    local_validation_output = []

    for i, s in enumerate(local_training_data):
        local_training_output.append(outputset.get(s["id"]))
        del local_training_data[i]["id"]
        local_training_data[i] = list(s.values())

    print(local_training_data)

    for i, s in enumerate(local_validation_data):
        local_validation_output.append(outputset.get(s["id"]))
        del local_validation_data[i]["id"]
        local_validation_data[i] = list(s.values())

    return local_training_data, local_training_output, local_validation_data, local_validation_output


# TODO : problème de forme du tableau (sous-tableaux de taille différente → keras fait chier).
#  Pistes : insérer l'info hashtags + emojis dans docvec ; casser le docvec et ajouter ses éléments au tableau de niveau supérieur
#  Convertir également les données textuelles en chiffres (mapping)
if __name__ == '__main__':
    tweets = util.get_all_tweets()

    with open("../java/src/fr/ceri/data/annotated/apprentissage.json", 'r') as f:
        polarites = json.load(f)

    data = util.prepare_learning_data(tweets)
    training_data, training_output, validation_data, validation_output = dispatch_data(data, polarites)

    model = configure_model(len(data[0]), len(output_classes))
    model.fit(training_data, training_output, epochs=1200, verbose=1,
              validation_data=(validation_data, validation_output))
