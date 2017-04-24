"""
fast_player.py

Defines a fast strategy Ludo player through the FastPlayer class.
"""

from strategy_player import *

class FastPlayer(StrategyPlayer):
    """
    Class that defines a Ludo player that makes moves based on fast strategy.
    """

    def __init__(self, id):
        """
        Construct a new fast player.
        """

        # Initialize a generic player
        StrategyPlayer.__init__(self, id, PlayerKind.Fast)

    def select_nonrandom_new_state(self, board_state, successors, timestamp):
        """
        Override the parent method in order to implement a fast-player strategy
        """
        # current candidate successor
        currentSuccessorIndex = -1

        for i in range(0, len(successors)):
            currentNewLoc = 0 if currentSuccessorIndex == -1 else successors[currentSuccessorIndex]["action"][1]
            successorNewLoc = successors[i]["action"][1]
            if (successorNewLoc > currentNewLoc):
                currentSuccessorIndex = i

        if currentSuccessorIndex != -1:
            return currentSuccessorIndex

        return -1

