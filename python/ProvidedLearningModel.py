import json
import sys
import time
import warnings

import numpy as np
from keras.callbacks import ModelCheckpoint
from keras.layers import GlobalMaxPooling1D, Conv1D, concatenate
from keras.layers import Input
from keras.layers.core import Dense, Activation, Dropout, Flatten
from keras.models import Model
from keras.optimizers import Adadelta
from keras.utils import to_categorical

from LearningModel import model_dir, dispatch_data

warnings.filterwarnings("ignore")

maxlen = 200  # Size of word embedding
word_nb_feature_maps = 200
hidden_size = 64
conv = "1,2,3,4,5"

sentence_input = Input(shape=(maxlen, 1, ))
output_classes = to_categorical([0, 1, 2, 3], num_classes=4, dtype="int")

x = Dense(200, input_dim=200, activation="relu")(sentence_input)
x = Dropout(0.3)(x)

xconv = []

for xnumber in conv.split(","):
    xconv.append(Conv1D(word_nb_feature_maps, int(xnumber), activation="relu")(x))

merged = concatenate(xconv, axis=1)

max_merged = GlobalMaxPooling1D()(merged)

x = Dropout(0.3)(max_merged)

x = Dense(hidden_size)(x)
x = Activation("relu")(x)

x = Dropout(0.2)(x)

x = Dense(4)(x)

model = Model(input=sentence_input, output=x)

with open("../common/data/annotated/apprentissage.json", 'r') as f:
    polarites = json.load(f)

with open("../common/data/trained/vectors_v3.json", 'r') as f:
    data = json.load(f)

actual_tweet_ids = [x for x in polarites.keys()]

# Filtrage pour conserver uniquement les tweets effectivement présents dans le corpus
data = [x for x in data if x["id"] in actual_tweet_ids]

training_data, training_output = dispatch_data(data, polarites)

# Rajout d'une dimension pour couche Convolutionnelle
training_data = np.expand_dims(training_data, axis=2)

model_training_time = time.time()

# Callback ModelCheckpoint
checkpoint = ModelCheckpoint("{}\\opti{}.hdf5".format(model_dir, model_training_time),
                             monitor="accuracy",
                             verbose=0, save_best_only=True, save_weights_only=False, mode="auto", period=1)

optim = Adadelta(lr=1.0, rho=0.95, epsilon=1e-06)
model.compile(loss="categorical_crossentropy", optimizer=optim, metrics=["accuracy"])
model.fit(np.array(training_data), np.array(training_output), nb_epoch=50, batch_size=128, shuffle=True, callbacks=[checkpoint])
