"""
aggressive_player.py

Defines an aggressive strategy Ludo player through the AggressivePlayer class.
"""

from strategy_player import *

class AggressivePlayer(StrategyPlayer):
    """
    Class that defines a Ludo player that makes moves based on aggressive strategy.
    """

    def __init__(self, id):
        """
        Construct a new aggressive player.
        """

        # Initialize a generic player
        StrategyPlayer.__init__(self, id, PlayerKind.Aggressive)

    def select_nonrandom_new_state(self, board_state, successors, timestamp):
        """
        Override the parent method in order to implement a aggressive-player strategy
        """
        for i in range(0, len(successors)):
            successorState = successors[i]["new_state"]

            for p in range(0, 3):
                if (p == self.id):
                    continue

                # if jail has 1 player more in the successor state than the current board_state,
                # that indicates the elimination of opponent's piece. Prefer that
                if ((board_state[p].state[0] + 0.25) == successorState[p].state[0]):
                    return i

        return -1

