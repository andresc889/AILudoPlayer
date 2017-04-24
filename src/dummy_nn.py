"""
dummy_nn.py

Provides an interface for a dummy neural network that always returns a single output with value = 1.
"""


class DummyNN(object):
    """
    Class that provides an interface for a dummy neural network that always returns a single output with value = 1.
    """

    def __init__(self, num_inputs, learning_rate, momentum, src_file=None):
        """
        Constructor for a single-output dummy neural network.

        :param num_inputs: Number of inputs to the neural network.
        :param learning_rate: Learning rate to use when training the neural network.
        :param momentum: Learning momentum to use when training the neural network.
        :param src_file: Ignored.
        """

        self.num_inputs = num_inputs
        self.learning_rate = learning_rate

    def write_to_file(self, dst_file):
        """
        Does nothing.

        :param dst_file: Name of the file where to write the network (ignored).
        """

        pass

    def train_with_datapoint(self, inputs, target):
        """
        Does nothing.

        :param inputs: Inputs to the neural network (as a list) (ignored).
        :param target: Target output (as a number) (ignored).
        """

        pass

    def evaluate(self, inputs):
        """
        Return 1.

        :param inputs: Inputs to the neural network (as a list) (ignored).
        :return: The output of the neural network (as a number) (ignored).
        """

        return 1
