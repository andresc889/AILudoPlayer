"""
nn.py

Provides an interface for a single-output neural network.
"""

from fann_nn import FANN


class NN(object):
    """
    Class that provides an interface for a single-output neural network.
    """

    # Parameters
    learning_rate = 0.005
    momentum = 0.1

    def __init__(self, num_inputs, src_file=None):
        """
        Constructor for a single-output neural network.

        :param num_inputs: Number of inputs to the neural network.
        :param src_file: If None, then a neural network with random weights is initialized. Otherwise, the neural
        network is loaded from the file.
        """

        self.nn = FANN(num_inputs, NN.learning_rate, NN.momentum, src_file)

    def write_to_file(self, dst_file):
        """
        Write the neural network to a file.

        :param dst_file: Name of the file where to write the network.
        """

        self.nn.write_to_file(dst_file)

    def train_with_datapoint(self, inputs, target):
        """
        Train the neural network with a single data point.

        :param inputs: Inputs to the neural network (as a list).
        :param target: Target output (as a number).
        """

        self.nn.train_with_datapoint(inputs, target)

    def evaluate(self, inputs):
        """
        Get the output of the neural network given the specified inputs.

        :param inputs: Inputs to the neural network (as a list).
        :return: The output of the neural network (as a number).
        """

        return self.nn.evaluate(inputs)