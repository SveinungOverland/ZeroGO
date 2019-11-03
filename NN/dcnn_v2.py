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
from tensorflow.keras import backend
from tensorflow.keras.optimizers import SGD

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
  if data_format == DataFormats.ChannelsFirst:
    # (0,1,2,3) NHWC -> (0,3,1,2) NCHW
    inputs = layers.Lambda(lambda x: backend.permute_dimensions(x, (0, 3, 1, 2)))(inputs)
  x = layers.Conv2D(filters, kernel_size=kernel_size, padding='same', data_format=data_format)(inputs)
  x = layers.BatchNormalization(axis=bn_axis)(x)
  x = layers.ReLU()(x)
  for i in range(nr_residual_layers):
    x = add_residual_layer(x, data_format, filters, kernel_size)
  return (inputs, x)

"""### Create value head"""

def create_value_head(graph, shape, filters, data_format, kernel_size):
  bn_axis = data_format_axis(data_format)
  x = layers.Conv2D(1, kernel_size=(1,1), padding='same', data_format=data_format)(graph)
  x = layers.BatchNormalization(axis=bn_axis)(x)
  x = layers.ReLU()(x)
  x = layers.Dense(filters)(x)
  x = layers.ReLU()(x)
  x = layers.GlobalMaxPooling2D(data_format)(x)
  x = layers.Flatten()(x)
  x = layers.Dense(1, activation="tanh", name='value')(x)
  return x

"""### Create policy head"""

def create_policy_head(graph, shape, filters, data_format, kernel_size):
  bn_axis = data_format_axis(data_format)
  x = layers.Conv2D(2, kernel_size=(1,1), padding='same', data_format=data_format)(graph)
  x = layers.BatchNormalization(axis=bn_axis)(x)
  x = layers.ReLU()(x)
  x = layers.GlobalMaxPooling2D(data_format)(x)
  x = layers.Flatten()(x)
  x = layers.Dense(shape[0] * shape[1] + 1, activation='softmax', name='policy')(x)
  return x

"""## Mode class"""

class Mode:
  Trunk = 0
  Model = 2
  ValueHead = 3
  PolicyHead = 4

"""## Model class"""

class Model:
  def __init__(self, inputs, value_head, policy_head, data_format, kernel_size):    
    # Can be choosen by mode
    self.inputs = inputs
    self.value_head = value_head
    self.policy_head = policy_head
  
    self.data_format = data_format
    self.kernel_size = kernel_size
  
    self.model = keras.Model(inputs=self.inputs, outputs=[self.value_head, self.policy_head])
    
  def save(self, file_name: str, overwrite=False):
    self.__retrieve_net(Mode.Model).save_weights(file_name + "/model", overwrite=overwrite)

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
    elif mode == Mode.Model:
      net = self.model
    elif mode == Mode.ValueHead:
      net = self.value_head
    elif mode == Mode.PolicyHead:
      net = self.policy_head
    else:
      print("No acceptible mode given!")
      raise Exception("No acceptible mode given!")
    return net
  
  def train(self, x, y_value, y_policy, learning_rate=0.01, momentum=0.9, epochs=5):
    net = self.__retrieve_net(Mode.Model)
    # assuming net is a model already
    net.compile(
      optimizer=SGD(lr=learning_rate, momentum=momentum),
      loss=['mean_squared_error', tf.nn.softmax_cross_entropy_with_logits],
      metrics=['accuracy'],
    )
    net.fit(x, [y_value, y_policy], epochs=epochs)
    
    return net.evaluate(x, [y_value, y_policy], verbose=0)
    # with tf.GradientTape() as tape:
    #   gradients = tape.gradient(tf.convert_to_tensor(loss, dtype=tf.float32), net.trainable_variables)
    #   keras.optimizers.SGD(learning_rate).apply_gradients(zip(gradients, net.trainable_variables))
  
  def predict(self, mode, X):
    net = self.__retrieve_net(mode)
    return net.predict(X)
  
  def describe(self, mode):
    net = self.__retrieve_net(mode)
    return net.summary()
  
  def load(self, file_name):
    self.__retrieve_net(Mode.Model).load_weights(file_name + "/model")
    return self
  
  @classmethod
  def create(cls, shape=(5,5,7), nr_residual_layers=10, kernel_size=(3,3), filters=256, data_format=DataFormats.ChannelsLast):
    inputs, trunk = create_trunk(shape, nr_residual_layers, filters, data_format, kernel_size)
    value_head = create_value_head(trunk, shape, filters, data_format, kernel_size)
    policy_head = create_policy_head(trunk, shape, filters, data_format, kernel_size)
    return cls(inputs, value_head, policy_head, data_format, kernel_size)