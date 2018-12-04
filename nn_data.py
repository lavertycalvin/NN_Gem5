from keras.models import Sequential
from keras.layers import Dense
import sys
import numpy as np
import os

g_NUM_WAYS = 2

def run_nn():
   #modify to take in all input numpy arrays
   all_x_train = np.zeros(shape=(0,2))
   all_y_train = np.zeros(shape=(0,2))
   for file_name in os.listdir("."):
       if "nn_touched" in file_name:
           x_train = np.load(file_name)
           all_x_train = np.concatenate((all_x_train, x_train), axis=0)
       if "nn_scores" in file_name:
           y_train = np.load(file_name)
           all_y_train = np.concatenate((all_y_train, y_train), axis=0)
   print all_x_train.shape
   print all_y_train.shape
   
   model = Sequential()

   #hyperbolic tangent activation function rather than sigmoid
   model.add(Dense(units=10, activation='sigmoid', input_dim=2))

   model.add(Dense(units=2, activation='linear'))

   model.compile(loss='categorical_crossentropy',
              optimizer='sgd',
              metrics=['accuracy'])



   model.fit(all_x_train, all_y_train, epochs=5, batch_size=32)


if __name__ == "__main__":
    run_nn()

