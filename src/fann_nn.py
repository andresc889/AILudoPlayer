"""
fann_nn.py

Provides an interface for a single-output neural network in FANN.
"""

from fann2 import libfann


class FANN(object):
    """
    Class that provides an interface for a single-output neural network in PyBrain.
    """

    def __init__(self, num_inputs, learning_rate, momentum, src_file=None):
        """
        Constructor for a single-output neural network.

        :param num_inputs: Number of inputs to the neural network.
        :param learning_rate: Learning rate to use when training the neural network.
        :param momentum: Learning momentum to use when training the neural network.
        :param src_file: If None, then a neural network with random weights is initialized. Otherwise, the neural
        network is loaded from the file.
        """

        self.nn = libfann.neural_net()

        if src_file is not None:
            # Initialize neural network from file
            self.nn.create_from_file(src_file)
        else:
            self.nn.create_standard_array([num_inputs, 20, 1])

            self.nn.set_activation_function_hidden(libfann.SIGMOID_SYMMETRIC)
            self.nn.set_activation_function_output(libfann.LINEAR)

        self.nn.set_training_algorithm(libfann.TRAIN_INCREMENTAL)
        self.nn.set_learning_rate(learning_rate)
        self.nn.set_learning_momentum(momentum)

        self.num_inputs = num_inputs
        self.learning_rate = learning_rate
        self.momentum = momentum

    def write_to_file(self, dst_file):
        """
        Write the neural network to a file.

        :param dst_file: Name of the file where to write the network.
        """

        self.nn.save(dst_file)

    def train_with_datapoint(self, inputs, target):
        """
        Train the neural network with a single data point.

        :param inputs: Inputs to the neural network (as a list).
        :param target: Target output (as a number).
        """

        self.nn.train(inputs, [target])

    def evaluate(self, inputs):
        """
        Get the output of the neural network given the specified inputs.

        :param inputs: Inputs to the neural network (as a list).
        :return: The output of the neural network (as a number).
        """

        return self.nn.run(inputs)[0]
