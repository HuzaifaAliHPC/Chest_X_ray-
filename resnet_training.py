# -*- coding: utf-8 -*-
"""RESNET_Training.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1PwnMsGgn0gPjlyvqWXRNjVX67RG4C6nE
"""

sample_images = [
                 ["/content/chest_xray/val/PNEUMONIA/person1946_bacteria_4875.jpeg"],["/content/chest_xray/val/PNEUMONIA/person1950_bacteria_4881.jpeg"]
                 ]
classes = ["NORMAL", "PNEUMONIA"]

import cv2
import os
import re
import glob
import random
import warnings
import numpy as np
import pandas as pd
import scipy as sp
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.image as mpimg
from platform import python_version
# from IPython.display import Image, display
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report,accuracy_score, confusion_matrix, ConfusionMatrixDisplay
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import *
from tensorflow.keras.layers import *
from tensorflow.keras.optimizers import *
from tensorflow.keras.applications import vgg16, ResNet152V2, InceptionResNetV2
from tensorflow.keras.preprocessing.image import img_to_array, array_to_img, ImageDataGenerator
import gradio as gr
warnings.simplefilter(action='ignore',category=FutureWarning)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
print(f'TensorFlow version: {tf.__version__}')
print(f'Python version: {python_version()}')

# Commented out IPython magic to ensure Python compatibility.
# %matplotlib inline
BASE_PATH = "/content/chest_xray/"
TRAIN_PATH = BASE_PATH + "train/"
TEST_PATH = BASE_PATH + "test/"
VAL_PATH = BASE_PATH + "val/"

SHAPE = (224,224,3)
batch_size = 64
classes = ["NORMAL", "PNEUMONIA"]

print(f'train_path: {TRAIN_PATH}')
print(f'test_path: {TEST_PATH}')
print(f'val_path: {VAL_PATH}')

training_data = len(os.listdir(os.path.join(TRAIN_PATH, classes[0]))) + len(os.listdir(os.path.join(TRAIN_PATH, classes[1])))
test_data = len(os.listdir(os.path.join(TEST_PATH, classes[0]))) + len(os.listdir(os.path.join(TEST_PATH, classes[1])))
print(training_data, test_data)

train_datagen = ImageDataGenerator(rescale=1/255,
                                  featurewise_center=False,  # set input mean to 0 over the dataset
                                  samplewise_center=False,  # set each sample mean to 0
                                  featurewise_std_normalization=False,  # divide inputs by std of the dataset
                                  samplewise_std_normalization=False,  # divide each input by its std
                                  zca_whitening=False,  # apply ZCA whitening
                                  rotation_range = 30,  # randomly rotate images in the range (degrees, 0 to 180)
                                  zoom_range = 0.2, # Randomly zoom image
                                  width_shift_range=0.1,  # randomly shift images horizontally (fraction of total width)
                                  height_shift_range=0.1,  # randomly shift images vertically (fraction of total height)
                                  horizontal_flip = True,  # randomly flip images
                                  vertical_flip=False)  # randomly flip images)
test_datagen = ImageDataGenerator(rescale=1/255)
val_datagen = ImageDataGenerator(rescale=1/255)

train_generator = train_datagen.flow_from_directory(
                  TRAIN_PATH,
                  target_size = (SHAPE[0],SHAPE[1]),
                  batch_size = batch_size,
                  class_mode = 'categorical',
                  shuffle = True,
                  subset = None,
                  seed = 33
                  )

test_generator = test_datagen.flow_from_directory(
                TEST_PATH,
                target_size = (SHAPE[0],SHAPE[1]),
                batch_size = batch_size,
                class_mode = 'categorical',
                shuffle = True,
                subset = None,
                seed = 33
)

val_generator = val_datagen.flow_from_directory(
                VAL_PATH,
                target_size = (SHAPE[0],SHAPE[1]),
                batch_size = batch_size,
                class_mode = 'categorical',
                shuffle = True,
                subset = None,
                seed = 33
)

test_num = test_generator.samples

label_test = []

for i in range((test_num // test_generator.batch_size)+1):
  X,y = test_generator.next()
  label_test.append(y)
label_test = np.argmax(np.vstack(label_test), axis=1)
label_test.shape

"""# Model Training for RESNET"""

def set_seed(seed):
  tf.random.set_seed(seed)
  os.environ['PYTHONHASHSEED'] = str(seed)
  np.random.seed(seed)
  random.seed(seed)

def res_model():
  set_seed(33)

  # for ResNet152V2
  res = ResNet152V2(weights='imagenet', include_top=False, input_shape = SHAPE)

  for layer in res.layers[:-8]:
    layer.trainable = False

  x = res.output
  x = Flatten()(x)
  x = Dropout(0.5)(x)
  x = Dense(512, activation="relu")(x)
  x = Dense(2, activation="softmax")(x)
  model = Model(res.input, x)
  model.compile(loss = "categorical_crossentropy",
  optimizer = SGD(learning_rate=0.0001, momentum=0.9),metrics=["accuracy"]) # SGD(learning_rate=0.0001, momentum=0.9) Adam(lr=1e-5)
  return model

RESNET = res_model()
RESNET.summary()
callback = tf.keras.callbacks.EarlyStopping(monitor='loss', patience=3)
RESNET.fit(train_generator,
          steps_per_epoch=train_generator.samples/train_generator.batch_size,
          epochs=1,
          callbacks=[callback]
          )
RESNET.save('/content/resnet_Chest_X_ray.h5')

