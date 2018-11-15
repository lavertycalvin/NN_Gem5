
from keras.models import Sequential
from keras.layers import Dense

g_NUM_CACHE_LINES = 100

model = Sequential()

model.add(Dense(units=10, activation='tansig', input_dim=g_NUM_CACHE_LINES)

model.add(Dense(units=10, activation='softmax'))

model.compile(loss='categorical_crossentropy',
              optimizer='sgd',
              metrics=['accuracy'])

x_train = "cache state"
y_train = "cache line to replace"


model.fit(x_train, y_train, epochs=5, batch_size=32)




