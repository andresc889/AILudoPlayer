"""
mixed_strategy_player.py

Defines a mixed strategy Ludo player through the MixedStrategyPlayer class.
First defensive, if not aggressive, if not fast, if not random strategy.
"""

from aggressive_player import *
from defensive_player import *
from fast_player import *

class MixedStrategyPlayer(StrategyPlayer):
    """
    Class that defines a Ludo player that makes moves based on mixed strategy.
    First defensive, if not aggressive, if not fast, if not random strategy.
    """

    def __init__(self, id):
        """
        Construct a new mixed_strategy player.
        """

        # Initialize a generic player
        StrategyPlayer.__init__(self, id, PlayerKind.Mixed)
        self.Defensive = DefensivePlayer(id)
        self.Aggressive = AggressivePlayer(id)
        self.Fast = FastPlayer(id)

    def select_nonrandom_new_state(self, board_state, successors, timestamp):
        """
        Override the parent method in order to implement a fast-player strategy
        """
        # current candidate successor

        successorIndex = self.Defensive.select_nonrandom_new_state(board_state, successors, timestamp)

        if (successorIndex != -1):
            return successorIndex

        successorIndex = self.Aggressive.select_nonrandom_new_state(board_state, successors, timestamp)

        if (successorIndex != -1):
            return successorIndex

        successorIndex = self.Fast.select_nonrandom_new_state(board_state, successors, timestamp)

        if (successorIndex != -1):
            return successorIndex

        return -1

