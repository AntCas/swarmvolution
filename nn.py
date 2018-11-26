import numpy as np

def sigmoid(x):
  return 1 / (1 + np.exp(-x))

class NeuralNetwork:
  def __init__(self, input_layer, hidden_layer_size, output_layer_size):
    self.input      = np.array(input_layer)
    self.weights_hl = np.random.rand(self.input.shape[0], hidden_layer_size) 
    self.weights_ol = np.random.rand(hidden_layer_size, output_layer_size)                 
    self.output     = np.zeros(output_layer_size)

  def feedforward(self):
    self.layer1 = sigmoid(np.dot(self.input, self.weights_hl))
    self.output = sigmoid(np.dot(self.layer1, self.weights_ol))

nn = NeuralNetwork([0.23, 0.0, 0.43, 0.33], 3, 2)
nn.feedforward()

print nn.output

