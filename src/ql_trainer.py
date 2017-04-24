"""
ql_trainer.py

Provides a controller to train a Q-Learning neural network in the Ludo game.
"""

import random

from ludo import Ludo
from ql_player import QLPlayer
from rnd_player import RandomPlayer
from mixed_strategy_player import MixedStrategyPlayer
from nn import NN


class QLTrainer(Ludo):
    """
    Class that provides a Q-Learning trainer for a Ludo game.
    """

    def __init__(self, num_episodes, nn_file_dst, nn_file_src=None, debug=False):
        """
        Constructor for a new trainer.

        :param: num_episodes: Number of episodes to train the network with.
        :param nn_file_dst: The name of a file where to store the resulting neural network.
        :param nn_file_src: The name of a file where to retrieve an existing neural network and use it as the starting
        point. If no file is provided, the neural network will be initialize with random weights.
        :param debug: If True, print debugging information.
        """

        # Initialize a Ludo game
        Ludo.__init__(self, [])

        # Members specific to QLTrainer
        self.nn = NN(238, nn_file_src)
        self.num_episodes = num_episodes
        self.nn_file_dst = nn_file_dst
        self.debug = debug

    def train(self, test=False):
        # Keep track of how many times each player wins
        wins = [0, ] * 4

        # For the epsilon greedy strategy, start with 0.9 and decrease linearly to 0
        max_epsilon = 0.9
        epsilon = max_epsilon

        if self.debug:
            print "===================================================================================================="
            print "| TRAINING STARTED                                                                                 |"
            print "===================================================================================================="
            print

        # Test initially
        if test:
            print "%-10d %20.2f %20.2f" % (0,
                                           self.test(1000, "1_QL_AGAINST_3_RANDOM")[0],
                                           self.test(1000, "1_QL_AGAINST_3_EXPERT")[0])

        for episode in range(self.num_episodes):
            if self.debug:
                print "Training episode " + str(episode + 1) + "/" + str(self.num_episodes) + "..."

            # Players to train with
            self.players = [QLPlayer(id=0, train=True, nn=self.nn, epsilon=epsilon),
                            QLPlayer(id=1, train=True, nn=self.nn, epsilon=epsilon),
                            QLPlayer(id=2, train=True, nn=self.nn, epsilon=epsilon),
                            QLPlayer(id=3, train=True, nn=self.nn, epsilon=epsilon)]

            # Always start with the player 0
            self.player_turn = 0

            # Initially, all players are at the starting positions
            for player in self.players:
                player.state = [0.0, ] * 59
                player.state[0] = 1.00

            # Start the episode
            self.play()

            # Count wins
            for p in range(len(self.players)):
                if self.players[p].state[58] == 1.0:
                    wins[p] += 1

            # Decrease epsilon
            if episode < 0.1 * self.num_episodes:
                epsilon = ((0.1 * self.num_episodes - 1) - episode) * max_epsilon / (0.1 * self.num_episodes - 1)
            else:
                epsilon = 0

            if self.debug:
                print

            # Test regularly
            if test and episode > 0:
                if episode % 20000 == 0:
                    print "%-10d %20.2f %20.2f" % (episode,
                                                   self.test(1000, "1_QL_AGAINST_3_RANDOM")[0],
                                                   self.test(1000, "1_QL_AGAINST_3_EXPERT")[0])

            # Save the neural network to the specified file every 1000 episodes
            if episode % 1000 == 0:
                self.nn.write_to_file(self.nn_file_dst)

        # Save the final neural network to the specified file
        self.nn.write_to_file(self.nn_file_dst)

        # Display the percentage of wins
        for w in range(len(wins)):
            wins[w] = wins[w] * 100.0 / self.num_episodes

        if self.debug:
            print "Wins: " + str(wins)
            print

            print "===================================================================================================="
            print "| TRAINING ENDED                                                                                   |"
            print "===================================================================================================="
            print

    def test(self, games, setting):
        # Keep track of how many times each player wins
        wins = [0, ] * 4

        if self.debug:
            print "===================================================================================================="
            print "| TESTING STARTED                                                                                  |"
            print "===================================================================================================="
            print

        for episode in range(games):
            if self.debug:
                print "Testing game " + str(episode + 1) + "/" + str(games) + "..."

            # Players to test with
            if setting == "1_QL_AGAINST_3_RANDOM":
                self.players = [QLPlayer(id=0, train=False, nn=self.nn, epsilon=0),
                                RandomPlayer(id=1),
                                RandomPlayer(id=2),
                                RandomPlayer(id=3)]
            elif setting == "1_QL_AGAINST_3_EXPERT":
                self.players = [QLPlayer(id=0, train=False, nn=self.nn, epsilon=0),
                                MixedStrategyPlayer(id=1),
                                MixedStrategyPlayer(id=2),
                                MixedStrategyPlayer(id=3)]

            # Always start with the player 0
            self.player_turn = 0

            # Initially, all players are at the starting positions
            for player in self.players:
                player.state = [0.0, ] * 59
                player.state[0] = 1.00

            # Start the episode
            self.play()

            # Count wins
            for p in range(len(self.players)):
                if self.players[p].state[58] == 1:
                    wins[p] += 1

            if self.debug:
                print

        # Display the percentage of wins
        for w in range(len(wins)):
            wins[w] = wins[w] * 100.0 / games

        if self.debug:
            print "Wins: " + str(wins)
            print

        if self.debug:
            print "===================================================================================================="
            print "| TESTING ENDED                                                                                    |"
            print "===================================================================================================="
            print

        return wins

trainer = QLTrainer(500000 + 1, '01102016_nn_exp_1.txt', debug=False)

print "Parameters:"
print "================================================================================"
print "QL Learning Rate: " + str(QLPlayer.learning_rate)
print "QL Discount Rate: " + str(QLPlayer.discount_rate)
print "NN Learning Rate: " + str(NN.learning_rate)
print "NN Momentum:      " + str(NN.momentum)
print "Training:         " + "4 QL Players"
print
print "%-10s %20s %20s" % ("Episodes", "RND Win Percentage", "XPT Win Percentage")
print "================================================================================"

trainer.train(test=True)

