import json
import time

import numpy as np
from keras import Sequential
from keras.callbacks import ModelCheckpoint, EarlyStopping, TensorBoard
from keras.layers import Dense
from keras.utils import to_categorical

import util
from CorpusVectorization import get_model, latest_model

model_dir = "models\\keras"

output_classes = to_categorical([0, 1, 2, 3], num_classes=4, dtype="int")
output_map = {"negatif": output_classes[0], "positif": output_classes[1], "mixte": output_classes[2],
              "neutre": output_classes[3]}


def configure_model(input_size, output_size):
    """Creates and configures the model

    :param input_size:  number of input attributes
    :param output_size: number of output classes
    :return: the created model
    """

    local_model = Sequential()
    local_model.add(Dense(200, input_dim=input_size, activation="relu"))

    for j in range(7):
        local_model.add(Dense(200, activation="relu"))

    local_model.add(Dense(output_size, activation="softmax"))

    local_model.compile(loss="categorical_crossentropy", optimizer="Adam",
                        metrics=["categorical_accuracy"])

    return local_model


def dispatch_data(dataset, outputset):
    # Dataset split
    local_training_data = []
    local_training_output = []

    for j, t in enumerate(dataset):
        local_training_data.append(t["message"])
        local_training_output.append(output_map.get(outputset[t["id"]]))

    return local_training_data, local_training_output


if __name__ == "__main__":
    with open("../common/data/annotated/apprentissage.json", "r", encoding="utf-8") as f:
        polarites = json.load(f)

    with open("../common/data/processed/unlabeled_filtered.json", "r", encoding="utf-8") as file:
        loaded_filtered_tweets = json.load(file)

    d2v_model = get_model(latest_model)

    data = util.prepare_learning_data(loaded_filtered_tweets, d2v_model, 3)

    with open("../common/data/trained/vectors_v3.json", "r") as f:
        data = json.load(f)

    actual_tweet_ids = [x for x in polarites.keys()]

    # Filtrage pour conserver uniquement les tweets effectivement présents dans le corpus
    data = [x for x in data if x["id"] in actual_tweet_ids]

    training_data, training_output = dispatch_data(data, polarites)

    keras_model = configure_model(len(training_data[0]), len(output_map))

    model_training_time = time.time()

    # Callback Tensorboard
    tensorboard = TensorBoard(log_dir="logs\\{}".format(model_training_time),
                              write_graph=True)

    # Callback ModelCheckpoint
    checkpoint = ModelCheckpoint("{}\\opti{}.hdf5".format(model_dir, model_training_time),
                                 monitor="val_categorical_accuracy",
                                 verbose=0, save_best_only=True, save_weights_only=False, mode="auto", period=1)

    # Callback EarlyStopping
    earlystop = EarlyStopping(monitor="val_categorical_accuracy", mode="max", verbose=1, patience=200)

    keras_model.fit(np.array(training_data), np.array(training_output), epochs=2000, verbose=1, shuffle=True,
                    validation_split=0.2, callbacks=[checkpoint, earlystop])
