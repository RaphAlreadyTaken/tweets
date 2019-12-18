import json
import os

import numpy as np
from keras.engine.saving import load_model
from keras.metrics import CategoricalAccuracy

from util import prepare_test_data_full


def evaluate_all_models():
    with open("../common/data/trained/vectors_test.json", 'r', encoding="utf-8") as f:
        test_data = json.load(f)

    local_model_dir = "models\\keras"

    classes = {0: "negatif", 1: "positif", 2: "mixte", 3: "neutre"}

    # Evaluate all models
    for file in os.listdir(local_model_dir):
        file_path = os.path.join(local_model_dir, file)

        # Chargement des modèles
        if os.path.isfile(file_path):
            # TODO : condition à supprimer quand les données vectorisées seront calculées (v2)
            if file == "opti1576631042.9595923.hdf5":
                model = load_model(file_path)

                output = []

                for data in test_data:
                    output_predict = model.predict(np.array([np.array(data["message"])]))
                    print(output_predict)
                    output_class = model.predict_classes(np.array([np.array(data["message"])]))
                    output_class = classes.get(output_class[0])
                    output.append([data["id"], output_class])

                with open("../common/data/metrics/result.txt", 'w', encoding="utf-8") as f:
                    for result in output:
                        f.write("{} {}\n".format(result[0], result[1]))


def format_test_data():
    test_data = []

    with open("../common/data/raw/test.txt", 'r', encoding="utf-8") as f:
        for line in f:
            split_line = line.split(" ", 1)
            test_data.append({"_id": split_line[0], "message": split_line[1].rstrip()})

    prepare_test_data_full(test_data)


if __name__ == '__main__':
    # format_test_data()

    evaluate_all_models()
