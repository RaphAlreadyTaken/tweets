import json
import os
import time
from math import floor

import numpy as np
from keras import Sequential, metrics
from keras.callbacks import ModelCheckpoint, EarlyStopping, TensorBoard
from keras.engine.saving import load_model
from keras.layers import Dense
from keras.utils import to_categorical

import util

model_dir = "models\\keras"
best_model_dir = model_dir + "\\overall_best"
best_model_path = model_dir + best_model_dir + "\\best_model.hdf5"

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
    local_model.add(Dense(100, input_dim=input_size, activation="relu"))

    for i in range(7):
        local_model.add(Dense(100, activation="relu"))

    local_model.add(Dense(output_size, activation="softmax"))

    local_model.compile(loss="categorical_crossentropy", optimizer="Adadelta",
                        metrics=["categorical_accuracy"])

    return local_model


def dispatch_data(dataset, outputset):
    # Sub-datasets allocation
    training_size = floor(len(dataset) * 0.8)

    # Dataset split
    local_training_data = []
    local_validation_data = []
    local_training_output = []
    local_validation_output = []

    for i, s in enumerate(dataset[:training_size]):
        local_training_data.append(s["message"])
        local_training_output.append(output_map.get(outputset.get(s["id"])))

    for i, s in enumerate(dataset[training_size:]):
        local_validation_data.append(s["message"])
        local_validation_output.append(output_map.get(outputset.get(s["id"])))

    return local_training_data, local_training_output, local_validation_data, local_validation_output


if __name__ == '__main__':
    tweets = util.get_all_tweets()

    with open("../common/data/annotated/apprentissage.json", 'r') as f:
        polarites = json.load(f)

    # WARNING: très long, à ne faire qu'une fois (résultat dans common/trained/vectors.json)
    # data = util.prepare_learning_data_full(tweets)

    with open("../common/data/trained/vectors_v1.json", 'r') as f:
        data = json.load(f)

    training_data, training_output, validation_data, validation_output = dispatch_data(data, polarites)

    model = configure_model(len(training_data[0]), len(output_map))

    model_training_time = time.time()

    # Callback Tensorboard
    tensorboard = TensorBoard(log_dir="logs\\{}".format(model_training_time),
                              write_graph=True)

    # Callback ModelCheckpoint
    checkpoint = ModelCheckpoint("{}\\opti{}.hdf5".format(model_dir, model_training_time),
                                 monitor="categorical_accuracy",
                                 verbose=0, save_best_only=True, save_weights_only=False, mode="auto", period=1)

    # Callback EarlyStopping
    earlystop = EarlyStopping(monitor="val_loss", mode="min", verbose=1, patience=10)

    model.fit(np.array(training_data), np.array(training_output), epochs=500, verbose=1,
              validation_split=0.2, shuffle=True,
              callbacks=[checkpoint, tensorboard])
