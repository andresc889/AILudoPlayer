"""
defensive_player.py

Defines a defensive strategy Ludo player through the DefensivePlayer class.
"""

from strategy_player import *

class DefensivePlayer(StrategyPlayer):
    """
    Class that defines a Ludo player that makes moves based on defensive strategy.
    """

    def __init__(self, id):
        """
        Construct a new defensive player.
        """

        # Initialize a generic player
        StrategyPlayer.__init__(self, id, PlayerKind.Defensive)


    def get_knocking_range_count(self, simple_relative_board_state, board_state):
        knocking_range_count = 0

        for p in range(0, 4):
            position = simple_relative_board_state[self.id][p]
            # if it is a blockade, do not consider it for counting knocking range
            if (board_state[self.id].state[position] > 0.25):
                continue

            for opi in range(0, 4):
                if (opi == self.id):
                    continue

                for op in range(0, 4):
                    otherPosition = simple_relative_board_state[opi][op]
                    if (otherPosition != -1 and position <= 51 and (position not in SafeSquares)):
                        knocking_range = (position - otherPosition + 52) % 52
                        if (knocking_range >= 1 and knocking_range <= 6):
                            knocking_range_count = knocking_range_count + 1

        return knocking_range_count

    def select_nonrandom_new_state(self, board_state, successors, timestamp):
        """
        Override the parent method in order to implement a defensive-player strategy
        """

        knocking_range_count_list = []

        # current candidate successor
        currentSuccessorIndex = -1

        for i in range(0, len(successors)):

            successor = successors[i]
            successor_board_state = successor["new_state"]
            successor_simple_board_state = self.get_simple_board_state(successor_board_state)
            successor_simple_relative_board_state = self.get_simple_relative_board_state(successor_simple_board_state)
            successor_knocking_range_count\
                = self.get_knocking_range_count(successor_simple_relative_board_state, successor_board_state)

            knocking_range_count_list.append(successor_knocking_range_count)

        min_knocking_range_count = min(knocking_range_count_list)
        mincount_knocking_range_count = knocking_range_count_list.count(min_knocking_range_count)

        # Check if the knocking_range_count is not the same for all the players
        # If so, defensive strategy cannot make a choice.
        # If not, return the index with minimum knocking_range_count
        if (mincount_knocking_range_count != len(knocking_range_count_list)):
            return knocking_range_count_list.index(min_knocking_range_count)

        return -1