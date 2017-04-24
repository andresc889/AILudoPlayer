"""
rnd_player.py

Defines a random Ludo player through the RandomPlayer class.
"""

import random

from player import *


class RandomPlayer(Player):
    """
    Class that defines a Ludo player that uses random moves.
    """

    def __init__(self, id):
        """
        Construct a new random player.
        """

        # Initialize a generic player
        Player.__init__(self, id, PlayerKind.Random)

    def select_new_state(self, board_state, successors, timestamp):
        """
        Override the parent method in order to implement a random-move strategy.
        """

        # Pick a successor randomly
        return random.randint(0, len(successors) - 1)
