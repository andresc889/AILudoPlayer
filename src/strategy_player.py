"""
strategy_player.py

Defines a strategy based Ludo player through the StrategyPlayer class.
"""

from player import *
import random

class StrategyPlayer(Player):
    """
    Class that defines a Ludo player that makes moves based on a strategy.
    """

    def __init__(self, id, kind):
        """
        Construct a new strategy player.
        """

        # Initialize a generic player
        Player.__init__(self, id, kind)

    def select_nonrandom_new_state(self, board_state, successors, timestamp):
        return -1

    def select_new_state(self, board_state, successors, timestamp):
        """
        Override the parent method in order to implement a strategy-player strategy
        """
        successorIndex = self.select_nonrandom_new_state(board_state, successors, timestamp)

        if (successorIndex == -1):
            successorIndex = random.randint(0, len(successors) - 1)

        old_to_new_action = (successors[successorIndex]["action"][0], successors[successorIndex]["action"][1])
        new_board_state = successors[successorIndex]["new_state"]

        # Find out if the player won the game and reward players appropriately
        if new_board_state[self.id].state[58] == 1.0:
            # The others lost: reward negatively
            try:
                board_state[(self.id + 1) % 4].cum_reward += -1.0
            except AttributeError:
                pass

            try:
                board_state[(self.id + 2) % 4].cum_reward += -1.0
            except AttributeError:
                pass

            try:
                board_state[(self.id + 3) % 4].cum_reward += -1.0
            except AttributeError:
                pass

        # Find out if the player knocked a piece belonging to the previous player and reward that player negatively
        diff = new_board_state[(self.id - 1) % 4].state[0] - board_state[(self.id - 1) % 4].state[0]

        if diff > 0 and timestamp > 0 and board_state[(self.id - 1) % 4].timestamp == timestamp - 1:
            try:
                board_state[(self.id - 1) % 4].cum_reward += -0.25
            except AttributeError:
                pass

        # Commit rewards for this player and the previous ones
        for i in range(0, 4):
            try:
                board_state[(self.id - i) % 4].reward()
            except AttributeError:
                pass

        # Return a random index
        return successorIndex

