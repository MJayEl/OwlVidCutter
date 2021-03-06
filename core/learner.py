from ../scripts/constant import IMAGE_DIMS, BATCH_SIZE, INIT_LR, EPOCHS, IMAGE_PATH
from keras.preprocessing.image import ImageDataGenerator
from sklearn.model_selection import train_test_split
from cnn import ConvolutionalNeuralNet
from keras.models import Sequential 
from keras.optimizers import Adam
#import matplotlib.pyplot as plt
import numpy as np
import cv2
import os

input_shape = IMAGE_DIMS

ad_directory = os.path.join(IMAGE_PATH, 'ad')
notad_directory = os.path.join(IMAGE_PATH, 'notad')

ad_images = [os.path.join(ad_directory, x) for x in os.listdir(ad_directory) if 'DS_Store' not in x][:MAX_IMAGES]
notad_images = [os.path.join(notad_directory, x) for x in os.listdir(notad_directory) if 'DS_Store' not in x][:MAX_IMAGES]
all_images = ad_images + notad_images

ad_labels = [1 for x in ad_images]
notad_labels = [0 for x in notad_images]
all_labels = ad_labels + notad_labels

#Loading images into arrays 
print('[INFO] Loading images...')
all_image_data = [cv2.resize(cv2.imread(x, 0), (input_shape[0], input_shape[1])) for x in all_images]
random_permutation = np.random.permutation(len(all_image_data))
#Turn images and labels into a numpy array and randomise the indexes
x,y = (np.array(all_image_data, dtype='float')/255)[random_permutation], np.array(all_labels)[random_permutation]

x_train, x_test, y_train, y_test = train_test_split(x,y, test_size=0.27, random_state=37)

#Reshape array into [input_shape e.g. (num of iamges,100,100,1)
x_train = np.reshape(x_train, (x_train.shape[0], input_shape[0], input_shape[1], input_shape[2]))
x_test = np.reshape(x_test, (x_test.shape[0], input_shape[0], input_shape[1], 1))

#plt.imshow(x_train[0], cmap='gray')
#plt.show()

aug = ImageDataGenerator(rotation_range=0, width_shift_range=0.1, 
        height_shift_range=0.1, shear_range=0.2, zoom_range=0.2, 
        horizontal_flip=True, fill_mode='nearest')

model = ConvolutionalNeuralNet.build(width=input_shape[0], height=input_shape[1], 
        depth=input_shape[2], classes=2)
opt = Adam(lr=INIT_LR, decay=INIT_LR / EPOCHS)

#Compile the model
print('[INFO] Compiling the model...')
model.compile(loss="sparse_categorical_crossentropy", 
        optimizer=opt,
        metrics=["accuracy"])

#Train the model
print('[INFO] Training the network...')
model.fit_generator(aug.flow(x_train, y_train, batch_size=BATCH_SIZE), 
        validation_data=(x_test, y_test), 
        steps_per_epoch=len(x_train)//BS,
        epochs=EPOCHS, verbose=1)

#Save the model locally
print('[INFO] Saving model...')
model.save("cnn.model")
