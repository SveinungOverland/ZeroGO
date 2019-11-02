from NN.dcnn_v1 import Model, Mode, DataFormats
import numpy as np

model_name = "test_model"

model = Model.create(shape=(2,2,1), kernel_size=(1,1), filters=100, data_format=DataFormats.ChannelsLast).load(model_name)

state = np.array([
    [[0,1],
    [0,0]]
]).reshape(1,2,2,1)

print("Policy prediction:", model.predict(Mode.Policy, state))
print("Value prediction:", model.predict(Mode.Value, state))

model.save(model_name)