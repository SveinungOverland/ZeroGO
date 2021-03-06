# -*- coding: utf-8 -*-
"""DCNN_V1.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1vgBnZ8BY5kBuPgJnNI5_FS2jWnztyVBq

# Deep Convolutional Neural Net for ZeroGO V1
"""

# Commented out IPython magic to ensure Python compatibility.
# %tensorflow_version 2.x
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np

tf.__version__

"""## Utils

### Batch normalization axis

Batch normalization only supports NHWC tensor on CPU
(Num_samples, Height, Width, Channels) (channel_last)

On GPU however NCHW is faster
(Num_samples, Channels, Height, Width)
"""

class DataFormats:
  ChannelsFirst = 'channels_first'
  ChannelsLast = 'channels_last'

def data_format_axis(data_format):
  return 1 if data_format == DataFormats.ChannelsFirst else 3

"""## Layers and heads

### Residual layer
"""

def add_residual_layer(x, data_format, filters, kernel_size):
  bn_axis = data_format_axis(data_format)
  res = layers.Conv2D(filters, kernel_size=kernel_size, padding='same', data_format=data_format)(x)
  res = layers.BatchNormalization(axis=bn_axis)(res)
  res = layers.ReLU()(res)
  res = layers.Conv2D(filters, kernel_size=kernel_size, padding='same', data_format=data_format)(res)
  res = layers.BatchNormalization(axis=bn_axis)(res)
  res = layers.ReLU()(res)
  res = layers.add([res, x])
  return layers.ReLU()(res)

"""### Create trunk"""

def create_trunk(shape, nr_residual_layers, filters, data_format, kernel_size):
  # Add lambda layer here to transpose NHWC to NCHW automatically
  bn_axis = data_format_axis(data_format)
  inputs = keras.Input(shape=shape)
  x = layers.Conv2D(filters, kernel_size=kernel_size, padding='same', data_format=data_format)(inputs)
  x = layers.BatchNormalization(axis=bn_axis)(x)
  x = layers.ReLU()(x)
  for i in range(nr_residual_layers):
    x = add_residual_layer(x, data_format, filters, kernel_size)
  return keras.Model(inputs, x)

"""### Create value head"""

def create_value_head(shape, filters, data_format, kernel_size):
  bn_axis = data_format_axis(data_format)
  return keras.Sequential([
      layers.Conv2D(1, kernel_size=(1,1), padding='same', data_format=data_format),
      layers.BatchNormalization(axis=bn_axis),
      layers.ReLU(),
      layers.Dense(filters),
      layers.ReLU(),
      layers.GlobalMaxPooling2D(data_format),
      layers.Flatten(),
      layers.Dense(1, activation="tanh")
  ])

"""### Create policy head"""

def create_policy_head(shape, filters, data_format, kernel_size):
  bn_axis = data_format_axis(data_format)
  return keras.Sequential([
      layers.Conv2D(2, kernel_size=(1,1), padding='same', data_format=data_format),
      layers.BatchNormalization(axis=bn_axis),
      layers.ReLU(),
      layers.GlobalMaxPooling2D(data_format),
      layers.Flatten(),
      layers.Dense(shape[0] * shape[1] + 1, activation='softmax')
  ])

"""## Mode class"""

class Mode:
  Trunk = 0
  Value = 1
  Policy = 2
  ValueHead = 3
  PolicyHead = 4

"""## Model class"""

class Model:
  def __init__(self, trunk, value_head, policy_head, data_format, kernel_size):    
    # Can be choosen by mode
    self.trunk = trunk # Is a model
    self.value_head = value_head
    self.policy_head = policy_head
  
    self.data_format = data_format
    self.kernel_size = kernel_size
  
    # Can also be choosen by mode
    self.value_path = keras.Sequential([self.trunk, self.value_head])
    self.policy_path = keras.Sequential([self.trunk, self.policy_head])
    
  def save(self, file_name: str, overwrite=False):
    self.__retrieve_net(Mode.Trunk).save_weights(file_name + "/trunk/trunk", overwrite=overwrite)
    self.__retrieve_net(Mode.ValueHead).save_weights(file_name + "/value/value", overwrite=overwrite)
    self.__retrieve_net(Mode.PolicyHead).save_weights(file_name + "/policy/policy", overwrite=overwrite)

#   def loss_fn(self, value_true, value_pred, policy_true, policy_pred):
#     # (z - v)^2 - pi^T * log(p) + c*||O||^2, der z = self-play-winner, v = predicted value, pi = search probabilities, p = nn move probability, O = nn parameters (weights), c = parameter controlling the level of L2 weight regularisation to prevent overfitting
#     # sum of mean-squared error and cross-entropy loss
#     return keras.losses.MSE(y_true, y_pred) + keras.losses.categorical_crossentropy(policy_true, policy_pred) # v1
#     pass
  
  def get_trunk_weights(self):
    return self.trunk.get_weights()
  
  def __retrieve_net(self, mode):
    if mode == Mode.Trunk:
      net = self.trunk
    elif mode == Mode.Value:
      net = self.value_path
    elif mode == Mode.Policy:
      net = self.policy_path
    elif mode == Mode.ValueHead:
      net = self.value_head
    elif mode == Mode.PolicyHead:
      net = self.policy_head
    else:
      print("No acceptible mode given!")
      raise Exception("No acceptible mode given!")
    return net
  
  def train(self, mode: Mode, loss, learning_rate=0.01):
    net = self.__retrieve_net(mode)
    with tf.GradientTape() as tape:
      gradients = tape.gradient(tf.convert_to_tensor(loss, dtype=tf.float32), net.trainable_variables)
      keras.optimizers.SGD(learning_rate).apply_gradients(zip(gradients, net.trainable_variables))
  
  def predict(self, mode, X):
    net = self.__retrieve_net(mode)
    return net.predict(X)
  
  def describe(self, mode):
    net = self.__retrieve_net(mode)
    return net.summary()
  
  def load(self, file_name):
    self.__retrieve_net(Mode.PolicyHead).load_weights(file_name + "/policy/policy")
    self.__retrieve_net(Mode.ValueHead).load_weights(file_name + "/value/value")
    self.__retrieve_net(Mode.Trunk).load_weights(file_name + "/trunk/trunk")
    return self
  
  @classmethod
  def create(cls, shape=(5,5,7), nr_residual_layers=10, kernel_size=(3,3), filters=256, data_format=DataFormats.ChannelsLast):
    trunk = create_trunk(shape, nr_residual_layers, filters, data_format, kernel_size)
    value_head = create_value_head(shape, filters, data_format, kernel_size)
    policy_head = create_policy_head(shape, filters, data_format, kernel_size)
    return cls(trunk, value_head, policy_head, data_format, kernel_size)