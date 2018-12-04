from keras.models import Sequential
from keras.layers import Dense
import sys
import numpy as np

g_NUM_WAYS = 2

def run_nn(nn_in_fn, nn_out_fn):
   x_train = np.load(nn_in_fn)
   print x_train.shape
   y_train = np.load(nn_out_fn)
   print y_train.shape
   
   model = Sequential()

   #hyperbolic tangent activation function rather than sigmoid
   model.add(Dense(units=10, activation='sigmoid', input_dim=2))

   model.add(Dense(units=2, activation='linear'))

   model.compile(loss='categorical_crossentropy',
              optimizer='sgd',
              metrics=['accuracy'])



   model.fit(x_train, y_train, epochs=5, batch_size=32)


if __name__ == "__main__":
    if(len(sys.argv) < 3):
        print "Usage: nn_data.py  nn_x_train nn_y_train"

    run_nn(sys.argv[1], sys.argv[2])

