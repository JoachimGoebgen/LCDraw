import os, keras
import numpy as np
import matplotlib.pyplot as plt
from idx2numpy import convert_from_file
from configparser import ConfigParser
from sklearn.model_selection import train_test_split
from keras.utils import to_categorical
from keras.layers import Input, Dense, Activation
from keras.models import Model

# --- PARAMETERS ---
numEpochs = 10
optimizer = "adam"
lossFunction = "categorical_crossentropy"
batchSize = 25
validationPerc = 0.2

# --- IMPORT ---
data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

conf_fullpath = os.path.join(data_path, 'config.ini')
conf = ConfigParser()
conf.read(conf_fullpath)

imgData_fullpath = os.path.join(data_path, conf.get('learn', 'imgDataFile_idx'))
lblData_fullpath = os.path.join(data_path, conf.get('learn', 'lblDataFile_idx'))

imgData = convert_from_file(imgData_fullpath)
lblData = convert_from_file(lblData_fullpath)

sampleSize = imgData.shape[0]
numPixels = imgData.shape[1] * imgData.shape[2]
numLabels = max(lblData)+1

if (imgData.shape[0] != lblData.shape[0]):
    print("Image- and Label-data do not match!")
    exit

# --- PREPARE DATA ---    
x_total = imgData.reshape(sampleSize, numPixels) / 255.0 # make the image 1-dimensional and normalized
y_total = to_categorical(lblData, num_classes=numLabels) # one-hot-encoded

x_train, x_test, y_train, y_test = train_test_split(x_total, y_total, test_size=0.2, random_state=13)

# --- CREATE MODEL ---
inputLayer = Input(shape=(numPixels,))
hiddenLayer = Dense(units=16, activation="relu")(inputLayer)
outputLayer = Dense(units=numLabels, activation="sigmoid")(hiddenLayer)

model = Model(inputs=inputLayer, outputs=outputLayer)
print(model.summary())
model.compile(optimizer=optimizer, loss=lossFunction, metrics=["accuracy"])

# --- TRAIN MODEL ---
model.fit(x_train, y_train, batch_size=batchSize, epochs=numEpochs, validation_split=validationPerc)

# --- EVALUATE MODEL ---
print(model.metrics_names)
model.evaluate(x_test, y_test, batch_size=batchSize)


