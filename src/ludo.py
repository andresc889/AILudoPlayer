"""
ludo.py

Provides the Ludo class, a controller for a Ludo game.
"""

import random


class Ludo(object):
    """
    Class that provides a controller for a Ludo game.
    """

    def __init__(self, players):
        """
        Constructor for a new Ludo game.
        """

        # Specify the player types
        self.players = players

        # Initially, all players are at the starting positions
        for player in self.players:
            player.state = [0.0, ] * 59
            player.state[0] = 1.00

        # Randomly choose which player starts the game
        self.player_turn = random.randint(0, 3)

    @staticmethod
    def player_wins(player):
        """
        Determine if the given player has won the game.

        :param player: The player to check.
        :return: True if the player has won (player.state[58] = 1). False otherwise.
        """

        if player.state[58] == 1:
            return True

        return False

    def roll_dice(self):
        """
        Roll a dice.

        :return: A random integer between 1 and 6 (inclusive).
        """

        return random.randint(1, 6)

    def play(self):
        """
        Start a Ludo game.
        """

        # Keep track of the turn number as a timestamp
        turn = 0

        while True:
            cur_player = self.players[self.player_turn]

            # Roll dice
            dice = self.roll_dice()

            # Prompt player for a move
            cur_player.move(dice, self.players, turn)

            # Check for a winner
            if Ludo.player_wins(cur_player):
                return cur_player

            # Next player
            self.player_turn = (self.player_turn + 1) % 4

            turn += 1
