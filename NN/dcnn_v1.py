# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# Change working directory from the workspace root to the ipynb file location. Turn this addition off with the DataScience.changeDirOnImportExport setting
# ms-python.python added
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np

print(tf.__version__)

# Batch normalization only supports NHWC tensor on CPU
# (Num_samples, Height, Width, Channels) (channel_last)
# 
# On GPU however NCHW is faster
# (Num_samples, Channels, Height, Width)
# 
# 

class DataFormats:
  ChannelsFirst = 'channels_first'
  ChannelsLast = 'channels_last'

def data_format_axis(data_format):
  return 1 if data_format == DataFormats.ChannelsFirst else 3

def add_residual_layer(x, data_format):
  bn_axis = data_format_axis(data_format)
  res = layers.Conv2D(256, kernel_size=(3,3), padding='same', data_format=data_format)(x)
  res = layers.BatchNormalization(axis=bn_axis)(res)
  res = layers.ReLU()(res)
  res = layers.Conv2D(256, kernel_size=(3,3), padding='same', data_format=data_format)(res)
  res = layers.BatchNormalization(axis=bn_axis)(res)
  res = layers.ReLU()(res)
  res = layers.add([res, x])
  return layers.ReLU()(res)

def create_trunk(shape, nr_residual_layers, filters, data_format):
  bn_axis = data_format_axis(data_format)
  inputs = keras.Input(shape=shape, batch_size=1)
  x = layers.Conv2D(filters, kernel_size=(3,3), padding='same', data_format=data_format)(inputs)
  x = layers.BatchNormalization(axis=bn_axis)(x)
  x = layers.ReLU()(x)
  for i in range(nr_residual_layers):
    x = add_residual_layer(x, data_format)
  return keras.Model(inputs, x)

def create_value_head(shape, filters, data_format):
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

def create_policy_head(shape, filters, data_format):
  bn_axis = data_format_axis(data_format)
  return keras.Sequential([
      layers.Conv2D(2, kernel_size=(1,1), padding='same', data_format=data_format),
      layers.BatchNormalization(axis=bn_axis),
      layers.ReLU(),
      layers.GlobalMaxPooling2D(data_format),
      layers.Flatten(),
      layers.Dense(shape[0] * shape[1] + 1, activation='softmax')
  ])

# %%
class Mode:
  Trunk = 0
  Value = 1
  Policy = 2
  ValueHead = 3
  PolicyHead = 4

class Model:
  def __init__(self, trunk, value_head, policy_head, data_format):    
    # Can be choosen by mode
    self.trunk = trunk # Is a model
    self.value_head = value_head
    self.policy_head = policy_head
  
    self.data_format = data_format
  
    # Can also be choosen by mode
    self.value_path = keras.Sequential([self.trunk, self.value_head])
    self.policy_path = keras.Sequential([self.trunk, self.policy_head])
    
  def save(self, file_name: str, overwrite=True):
    self.__retrieve_net(Mode.Trunk).save_weights(file_name + "/trunk", overwrite=overwrite)
    self.__retrieve_net(Mode.Value).save_weights(file_name + "/value", overwrite=overwrite)
    self.__retrieve_net(Mode.Policy).save_weights(file_name + "/policy", overwrite=overwrite)
  
  def get_trunk_weights(self):
    return self.trunk.get_weights()
  
  def __retrieve_net(self, mode: Mode):
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
  
  def train(self, mode: Mode, loss):
    net = self.__retrieve_net(mode)
    tape = tf.GradientTape()
    gradients = tape.gradient(loss, net.trainable_variables)
    #optimizer.apply_gradients(zip(gradients, net.trainable_variables))
    # where is the optimizer from @Svenung 
  
  def predict(self, mode, X):
    net = self.__retrieve_net(mode)
    return net.predict(X)
  
  def describe(self, mode):
    net = self.__retrieve_net(mode)
    return net.summary()
  
  def load(self, file_name, mode: Mode):
    self.__retrieve_net(mode.Policy).load_weights(file_name + "/policy")
    self.__retrieve_net(mode.Value).load_weights(file_name + "/value")
    self.__retrieve_net(mode.Trunk).load_weights(file_name + "/trunk")
    return self
  
  @classmethod
  def create(cls, shape=(5,5,7), nr_residual_layers=10, filters=256, data_format=DataFormats.ChannelsLast):
    trunk = create_trunk(shape, nr_residual_layers, filters, data_format)
    value_head = create_value_head(shape, filters, data_format)
    policy_head = create_policy_head(shape, filters, data_format)
    return cls(trunk, value_head, policy_head, data_format)


