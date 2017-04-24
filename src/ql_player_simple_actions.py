"""
ql_player.py

Defines a Q-Learning Ludo player through the QLPlayer class.
"""

import copy
import math
import random

from player import Player
from player import PlayerKind


class QLPlayer(Player):
    """
    Class that defines a Ludo player that uses Q-Learning.
    """

    # QL Parameters
    debug = False
    learning_rate = 0.8
    discount_rate = 0.95

    def __init__(self, id, train=False, nn=None, epsilon=0.0):
        """
        Construct a new Q-Learning player.

        :param: train: If True, the player trains the neural network while playing. Otherwise, it just plays.
        :param: nn: A PyBrain neural network to use for this player.
        """

        # Initialize a generic player
        Player.__init__(self, id, PlayerKind.QLearning)

        # QLPlayer-specific section
        self.old_board_state = None
        self.old_to_new_cat = None
        self.old_to_new_action = None
        self.new_board_state = None
        self.train = train
        self.nn = nn
        self.epsilon = epsilon
        self.cum_reward = 0.0

    def board_state_and_category_to_nn_inputs(self, board_state, category):
        """
        Transform a state-action category pair to an input suitable for a neural network.

        :param board_state: The board state with 4 players.
        :param category: The action category (see the Player.****_MOVE constants).
        :return: A list of 237 elements: the first 59 elements represent the state of the current player. The next
        59 elements represent the state of the next player. And so on. The last element represents the action category
        normalized between 0 and 1.
        """

        inputs = [0.0, ] * 237

        # First, put the state of all players
        i = 0

        for p_order in range(0, 4):
            for s in board_state[(self.id + p_order) % 4].state:
                inputs[i] = s
                i += 1

        # Next, put the action
        if category == Player.DEFENSIVE_MOVE:
            inputs[236] = 0.20
        elif category == Player.AGGRESSIVE_MOVE:
            inputs[236] = 0.40
        elif category == Player.FAST_MOVE:
            inputs[236] = 0.60
        elif category == Player.RELEASE_MOVE:
            inputs[236] = 0.80
        elif category == Player.RANDOM_MOVE:
            inputs[236] = 1.00

        return inputs

    def reward(self):
        """
        Commit the accumulated rewards (only in the train mode).
        """

        # If not training or if the accumulated reward is 0, we don't need to do anything
        if not self.train or self.cum_reward == 0.0:
            self.cum_reward = 0.0
            return

        # print "Player " + str(self.id) + ": I was just rewarded with " + str(self.cum_reward) + " for action " + \
        #     str(self.old_to_new_action)

        # Provide the neural network with a training point
        if self.old_board_state is not None and self.old_to_new_cat is not None and self.new_board_state is not None:
            # Convert the old board state to inputs for the neural network
            old_inputs = self.board_state_and_category_to_nn_inputs(self.old_board_state, self.old_to_new_cat)

            # Now, apply the Q-Learning update: start by finding Q(s_t, a)
            old_q = self.nn.evaluate(old_inputs)

            # Then the estimate of optimal future value: 0 when the new state is a final state
            final_state = False
            min_q_est = 0
            max_q_est = 0

            for p in self.new_board_state:
                if p.state[58] == 1:
                    final_state = True
                    break

            if not final_state:
                min_q_est = float("inf")
                max_q_est = float("-inf")

                # Evaluate all possible categories at the next state
                next_player = self.new_board_state[(self.id + 1) % 4]

                # First obtain the possible successors
                app_categories = []

                for dice in range(1, 6 + 1):
                    new_successors = next_player.get_next_states(dice, self.new_board_state)

                    if new_successors is not None:
                        for s in new_successors:
                            if s['categories'] & Player.DEFENSIVE_MOVE > 0:
                                app_categories.append(Player.DEFENSIVE_MOVE)

                            if s['categories'] & Player.AGGRESSIVE_MOVE > 0:
                                app_categories.append(Player.AGGRESSIVE_MOVE)

                            if s['categories'] & Player.FAST_MOVE > 0:
                                app_categories.append(Player.FAST_MOVE)

                            if s['categories'] & Player.RELEASE_MOVE > 0:
                                app_categories.append(Player.RELEASE_MOVE)

                            if s['categories'] & Player.RANDOM_MOVE > 0:
                                app_categories.append(Player.RANDOM_MOVE)

                # Delete duplicate categories
                app_categories = list(set(app_categories))

                # Evaluate the categories
                for c in app_categories:
                    new_inputs = next_player.board_state_and_category_to_nn_inputs(self.new_board_state, c)
                    new_q_est = self.nn.evaluate(new_inputs)

                    if new_q_est > max_q_est:
                        max_q_est = new_q_est

                    if new_q_est < min_q_est:
                        min_q_est = new_q_est

            if max_q_est == float("-inf"):
                max_q_est = 0

            if min_q_est == float("inf"):
                min_q_est = 0

            # Calculate the new Q value (alpha = 0.5, gamma = 0.95)
            new_q = old_q + QLPlayer.learning_rate * (self.cum_reward - QLPlayer.discount_rate * min_q_est - old_q)

            # Train the neural network with this data point
            self.nn.train_with_datapoint(old_inputs, new_q)

        # Reset the accumulated reward
        self.cum_reward = 0.0

    def select_new_state(self, board_state, successors, timestamp):
        """
        Override the parent method in order to implement the Q-Learning strategy.
        """

        if QLPlayer.debug:
            print "P" + str(self.id) + ": " + str(len(successors)) + " successor(s)"

        # Store the current state as the old state
        self.old_board_state = copy.deepcopy(board_state)

        # Compile a list of applicable action categories
        app_categories = []

        for s in successors:
            if s['categories'] & Player.DEFENSIVE_MOVE > 0:
                app_categories.append(Player.DEFENSIVE_MOVE)

            if s['categories'] & Player.AGGRESSIVE_MOVE > 0:
                app_categories.append(Player.AGGRESSIVE_MOVE)

            if s['categories'] & Player.FAST_MOVE > 0:
                app_categories.append(Player.FAST_MOVE)

            if s['categories'] & Player.RELEASE_MOVE > 0:
                app_categories.append(Player.RELEASE_MOVE)

            if s['categories'] & Player.RANDOM_MOVE > 0:
                app_categories.append(Player.RANDOM_MOVE)

        if QLPlayer.debug:
            print "P" + str(self.id) + ": Successors: ",

            for s in successors:
                print str(s['action']) + " [" + str(s['categories']) + "] ",

            print ""

        # Remove duplicate action categories
        app_categories = list(set(app_categories))

        if QLPlayer.debug:
            print "P" + str(self.id) + ": Categories: " + str(app_categories)

        # Use an epsilon-greedy policy to choose the next category when training (otherwise choose the best)
        if self.train and random.uniform(0, 1) < self.epsilon:
            # Choose a random category
            self.old_to_new_cat = app_categories[random.randint(0, len(app_categories) - 1)]
        else:
            # Evaluate each action category using the neural network and choose the best (ties are broken randomly)
            q_values = []

            for c in app_categories:
                q_values.append(self.nn.evaluate(self.board_state_and_category_to_nn_inputs(self.old_board_state, c)))

            if QLPlayer.debug:
                print "P" + str(self.id) + ": Q values: " + str(q_values)

            max_q_value = max(q_values)

            if QLPlayer.debug:
                print "P" + str(self.id) + ": Max Q value: " + str(max_q_value)

            if math.isnan(max_q_value):
                print "Got NaN!"
                exit()
            else:
                cat_candidates = []

                for i in range(len(q_values)):
                    if q_values[i] == max_q_value:
                        cat_candidates.append(i)

                self.old_to_new_cat = app_categories[cat_candidates[random.randint(0, len(cat_candidates) - 1)]]

        if QLPlayer.debug:
            print "P" + str(self.id) + ": Chosen category: " + str(self.old_to_new_cat)

        # Choose a random successor that belong to the chosen category
        s_with_category = []

        for i in range(len(successors)):
            if successors[i]['categories'] & self.old_to_new_cat > 0:
                s_with_category.append(i)

        successor_index = s_with_category[random.randint(0, len(s_with_category) - 1)]

        # Store the action and the new state
        self.old_to_new_action = (successors[successor_index]["action"][0], successors[successor_index]["action"][1])
        self.new_board_state = successors[successor_index]["new_state"]

        # Assign rewards
        cur_board_state = board_state
        action = self.old_to_new_action
        new_board_state = self.new_board_state

        # Find out if the player won the game and reward players appropriately
        if new_board_state[self.id].state[58] == 1.0:
            # The current player won
            self.cum_reward += 1.0

            # The others lost: reward negatively
            try:
                cur_board_state[(self.id + 1) % 4].cum_reward += -1.0
            except AttributeError:
                pass

            try:
                cur_board_state[(self.id + 2) % 4].cum_reward += -1.0
            except AttributeError:
                pass

            try:
                cur_board_state[(self.id + 3) % 4].cum_reward += -1.0
            except AttributeError:
                pass

        # Find out if the player released one of its pieces and reward appropriately
        if new_board_state[self.id].state[0] < cur_board_state[self.id].state[0]:
            self.cum_reward += 5.25

        # Find out if a vulnerable piece was defended
        src_piece_loc = action[0]

        # A vulnerable piece must be in the circular track
        if 1 <= src_piece_loc <= 51:
            # A vulnerable piece must have been in a non-safe square
            if src_piece_loc not in [1, 9, 14, 22, 27, 35, 40, 48]:
                # A vulnerable piece must have been alone
                if cur_board_state[self.id].state[src_piece_loc] == 0.25:
                    # A vulnerable piece must have been within knocking range
                    vulnerable = False

                    for np in range(1, 4):
                        # Transform the piece position to be as seen by opponent np
                        src_piece_loc_in_np = (src_piece_loc - 13 * np) % 52

                        # The only catch is that this transformation yields 0 for what's supposed to be square 52.
                        # However, this is perfect for the next step.

                        # Go through this opponent's pieces to see if any of them can knock the piece in question
                        for op in range(1, 52):
                            if cur_board_state[(self.id + np) % 4].state[op] == 0:
                                continue

                            if 0 < src_piece_loc_in_np - op <= 6:
                                vulnerable = True
                                break

                        if vulnerable:
                            self.cum_reward += 5.2
                            break

        # Find out if the player knocked a piece belonging to an opponent and reward appropriately
        for np in range(1, 4):
            diff = new_board_state[(self.id - np) % 4].state[0] - cur_board_state[(self.id - np) % 4].state[0]

            if diff > 0:
                self.cum_reward += 4.15 * diff * 4

        # Find out if the player knocked a piece belonging to the previous player and reward that player negatively
        diff = new_board_state[(self.id - 1) % 4].state[0] - cur_board_state[(self.id - 1) % 4].state[0]

        if diff > 0 and timestamp > 0 and cur_board_state[(self.id - 1) % 4].timestamp == timestamp - 1:
            try:
                cur_board_state[(self.id - 1) % 4].cum_reward += -4.25
            except AttributeError:
                pass

        # Find out if the current player moved a piece closest to home (not including pieces at the start)
        cur_closest = 57

        while True:
            if cur_closest == 0:
                # We reached the start area. No reward will be given
                break
            elif cur_board_state[self.id].state[cur_closest] > 0:
                # We found a piece closest to home in the current board. Check if it moved
                if new_board_state[self.id].state[cur_closest] < cur_board_state[self.id].state[cur_closest]:
                    self.cum_reward += 3.1
                break
            else:
                cur_closest -= 1

        # Find out if the current player formed a blockade (in the circular track) and reward appropriately
        for l in range(1, 52):
            # Ignore safe squares
            if l in [1, 9, 14, 22, 27, 35, 40, 48]:
                continue

            if new_board_state[self.id].state[l] >= 0.5 > cur_board_state[self.id].state[l]:
                self.cum_reward += 1.05
                break

        # Commit rewards for this player and the previous ones
        for i in range(0, 4):
            try:
                cur_board_state[(self.id - i) % 4].reward()
            except AttributeError:
                pass

        return successor_index
