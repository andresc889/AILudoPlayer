"""
human_player.py

Defines a random Ludo player through the HumanPlayer class.
"""

import random

from player import *


class HumanPlayer(Player):
    """
    Class that defines a Ludo player that prompts a human player for a move.
    """

    def __init__(self, id, name=""):
        """
        Construct a new human player.
        """

        # Initialize a generic player
        Player.__init__(self, id, PlayerKind.Human)

        self.name = name

    def select_new_state(self, board_state, successors, timestamp):
        """
        Override the parent method in order to implement a human-move strategy.
        """

        print "====================> HUMAN PLAYER " + self.name + ":"

        # Show possible source positions
        possible = []

        print "Choices:                 ",

        for s in successors:
            print " " + str(s['action'][0]),
            possible.append(s['action'][0])

        print

        # Ask for the source position
        while True:
            src_position = input("Enter the source position: ")

            if src_position in possible:
                break

        print

        # Return the corresponding successor
        for i in range(len(successors)):
            if src_position == successors[i]['action'][0]:
                return i

        # We should never get here
        return random.randint(0, len(successors) - 1)
