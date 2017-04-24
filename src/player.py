"""
player.py

Defines a generic Ludo player through the Player class.
"""

import copy


class PlayerKind:
    Random = 0 # Random player
    QLearning = 1 # Q-Learning player
    Fast = 2 # Fast strategy player
    Aggressive = 3 # Aggressive strategy player
    Defensive = 4 # Defensive strategy player
    Mixed = 5 # Mixed strategy player
    Human = 6 # Human player

def GetKind(kind):
    return {
        PlayerKind.Random: 'R',
        PlayerKind.QLearning: 'Q',
        PlayerKind.Fast: 'F',
        PlayerKind.Aggressive: 'A',
        PlayerKind.Defensive: 'D',
        PlayerKind.Mixed: 'M',
        PlayerKind.Human: 'H',
    }[kind]

def GetFullKind(kind):
    return {
        PlayerKind.Random: 'Random',
        PlayerKind.QLearning: 'Q-Learning',
        PlayerKind.Fast: 'Fast',
        PlayerKind.Aggressive: 'Aggressive',
        PlayerKind.Defensive: 'Defensive',
        PlayerKind.Mixed: 'Mixed-Strategy',
        PlayerKind.Human: 'Human',
    }[kind]

SafeSquares = [0, 1, 9, 14, 22, 27, 35, 40, 48]


class Player(object):
    """
    Class that defines a generic Ludo player. Actual players should inherit from this class.
    """

    # Masks to identify moves
    DEFENSIVE_MOVE = 1
    AGGRESSIVE_MOVE = 2
    FAST_MOVE = 4
    RELEASE_MOVE = 8
    RANDOM_MOVE = 16

    def __init__(self, id, kind):
        """
        Construct a new generic player.
        """

        # The player ID must match the position of the player in the board state list. For example:
        # [Player(0), Player(1), Player(2), Player(3)] -> Acceptable
        # [Player(3), Player(1), Player(0), Player(2)] -> Not acceptable
        self.id = id

        # R represents a random player
        self.kind = kind

        # 0: Jail
        # 1-57: Regular positions (Position 52 should never be occupied by this player)
        # 58: Home!
        self.state = [0.0, ] * 59

        # The board state that includes the states of all the players after performing self.action
        self.board_state = None

        # The last action (as a tuple) taken to arrive at self.board_state: the first element is the position of a
        # piece in the previous state. The second element is the position of that piece in the self.board_state.
        self.action = None

        # Timestamp of when self.action was taken (turn number)
        self.timestamp = -1

    def __deepcopy__(self, memo):
        """
        Overwrite the way a Player object is deep copied. We only want to copy the player's id and state. We don't want
        to copy the board_state member because that would form an unnecessary recursive copying. Hence, the action and
        timestamp members are unnecessary as well.
        """

        cpy = type(self)(self.id)

        # Copy the state of each player
        for l in range(len(self.state)):
            cpy.state[l] = self.state[l]

        # Do not copy the board_state (not needed)

        return cpy

    def get_c_track_pieces_next_player(self, board_state, order, position):
        """
        Given the position of a piece in a current player's state, return the value of that position as seen by the
        (order)th next player's state. It is assumed that the given position is in the circular track
        (0 < position <= 52).

        :param board_state: Board state with 4 players.
        :param order: 1 for the next player, 2 for the 2nd next player, etc.
        :param position: Position of the piece in the current player's state.
        :return: Position of the piece in the (order)th next player's state.
        """
        new_position = (position - 13 * order) % 52

        if new_position == 0:
            # In the circular track, this position will be square 52
            return board_state[(self.id + order) % 4].state[52]

        # Otherwise, this is a normal position
        return board_state[(self.id + order) % 4].state[new_position]

    def set_c_track_pieces_next_player(self, board_state, order, position, new_value):
        """
        Given the position of a piece in a current player's state, set the value of that position as seen by the
        (order)th next player's state. It is assumed that the given position is in the circular track
        (0 < position <= 52).

        :param board_state: Board state with 4 players.
        :param order: 1 for the next player, 2 for the 2nd next player, etc.
        :param position: Position of the piece in the current player's state.
        :param new_value: Value to set to at the position of the piece as seen by the (order)th next player's state.
        """
        new_position = (position - 13 * order) % 52

        if new_position == 0:
            # In the circular track, this position will be square 52
            board_state[(self.id + order) % 4].state[52] = new_value

        # Otherwise, this is a normal position
        board_state[(self.id + order) % 4].state[new_position] = new_value

    def get_simple_state(self, state):
        """
        Gets the state of a player as a list of 4 integers between 0 and 59
        :param state: State of a player represented by an array of 59 values each of which can be 0 to 1
        :return: Gets the state of a player as a list of 4 integers between 0 and 59
        """
        simple_state = []
        for i in range(0, 59):
            nPlayers = state[i] * 4
            while (nPlayers > 0):
                simple_state.append(i)
                nPlayers = nPlayers - 1

        return simple_state

    def get_simple_board_state(self, board_state):
        """
        Gets the state of the entire board as a dictionary of simple states for each player
        :param board_state: board_state as represented in the player class
        :return: Gets the state of the entire board as a dictionary of simple states for each player
        """
        simple_board_state = {}

        for i in range(0, 4):
            state = board_state[i].state
            simple_state = self.get_simple_state(state)
            simple_board_state[i] = simple_state

        return simple_board_state

    def get_relative_position(self, otherPlayerId, otherPosition):
        """
        Returns the relative position of other player w.r.t current player.
        Returns -1 if out of scope for current player
        :param otherPlayerId: id of the other player
        :param otherPosition: position of other player w.r.t itself
        :return: Returns the relative position of other player w.r.t current player
        """

        if (otherPlayerId == self.id):
            return otherPosition

        if otherPosition >= 52 or otherPosition == 0:
            return -1

        order = (otherPlayerId - self.id + 4) % 4

        relativePosition = (otherPosition + 13 * order) % 52

        if relativePosition == 0:
            relativePosition = 52

        return relativePosition

    def get_simple_relative_board_state(self, simple_board_state):
        """
        Gets the simple state of all the players as viewed by the current player.
        For squares not in the scope of the current player, we set -1
        :param simple_board_state: Simple board state as obtained from get_simple_board_state
        :return: Gets the entire board state as viewed by the current player
        """

        simple_relative_board_state = {}

        for p in range(0, 4):
            if (p == self.id):
                simple_relative_board_state[p] = list(simple_board_state[p])

            simple_relative_board_state[p] = []

            for position in simple_board_state[p]:
                relativePosition = self.get_relative_position(p, position)
                simple_relative_board_state[p].append(relativePosition)

        return simple_relative_board_state

    def transition_is_defensive(self, old_board_state, action, new_board_state):
        """
        Decide if a specific state transition was a defensive move.

        :param old_board_state: The old board state with all four players.
        :param action: The action that was taken.
        :param new_board_state: The new board state with all four players.
        :return: True if the transition is considered to be a defensive move. False otherwise.
        """

        src_piece_loc = action[0]

        # A vulnerable piece must be in the circular track
        if 1 <= src_piece_loc <= 51:
            # A vulnerable piece must have been in a non-safe square
            if src_piece_loc not in [1, 9, 14, 22, 27, 35, 40, 48]:
                # A vulnerable piece must have been alone
                if old_board_state[self.id].state[src_piece_loc] == 0.25:
                    # A vulnerable piece must have been within knocking range
                    vulnerable = False

                    for np in range(1, 4):
                        # Transform the piece position to be as seen by opponent np
                        src_piece_loc_in_np = (src_piece_loc - 13 * np) % 52

                        # The only catch is that this transformation yields 0 for what's supposed to be square 52.
                        # However, this is perfect for the next step.

                        # Go through this opponent's pieces to see if any of them can knock the piece in question
                        for op in range(1, 52):
                            if old_board_state[(self.id + np) % 4].state[op] == 0:
                                continue

                            if 0 < src_piece_loc_in_np - op <= 6:
                                vulnerable = True
                                break

                        if vulnerable:
                            return True

        return False

    def transition_is_aggressive(self, old_board_state, action, new_board_state):
        """
        Decide if a specific state transition was an aggressive move.

        :param old_board_state: The old board state with all four players.
        :param action: The action that was taken.
        :param new_board_state: The new board state with all four players.
        :return: True if the transition is considered to be an aggressive move. False otherwise.
        """

        for np in range(1, 4):
            diff = new_board_state[(self.id - np) % 4].state[0] - old_board_state[(self.id - np) % 4].state[0]

            if diff > 0:
                return True

        return False

    def transition_is_fast(self, old_board_state, action, new_board_state):
        """
        Decide if a specific state transition was a fast move.

        :param old_board_state: The old board state with all four players.
        :param action: The action that was taken.
        :param new_board_state: The new board state with all four players.
        :return: True if the transition is considered to be a fast move. False otherwise.
        """

        # Find out if the current player moved a piece closest to home (not including pieces at the start)
        cur_closest = 57

        while True:
            if cur_closest == 0:
                # We reached the start area. No reward will be given
                break
            elif old_board_state[self.id].state[cur_closest] > 0:
                # We found a piece closest to home in the current board. Check if it moved
                if new_board_state[self.id].state[cur_closest] < old_board_state[self.id].state[cur_closest]:
                    return True
                break
            else:
                cur_closest -= 1

        return False

    def transition_is_release(self, old_board_state, action, new_board_state):
        """
        Decide if a specific state transition was a releasing move.

        :param old_board_state: The old board state with all four players.
        :param action: The action that was taken.
        :param new_board_state: The new board state with all four players.
        :return: True if the transition is considered to be a releasing move. False otherwise.
        """

        if new_board_state[self.id].state[0] < old_board_state[self.id].state[0]:
            return True

        return False

    def get_next_states(self, dice_value, board_state):
        """
        Get the successors of the current board state (board_state) based on the value of the dice. Each element in the
        returned list is a dictionary of the form:

        {new_state: [...], action: (...), categories: X}

        The new_state key refers to a board state of 4 players with their new states. The action key refers to a tuple
        where the first element is the position of the piece that was moved in the current player's current state and
        the second element is the position where the piece was moved to in the current player's new state. The
        categories key refers to a bit vector (integer) that encodes the categories of the transition (see the
        Player.****_MOVE constants). All transitions belong to the Player.RANDOM_MOVE category.

        Each new state is a list of the four original players with their state members updated. However their
        board_state members are set to None because they are not needed.

        :param dice_value: The value of the dice roll.
        :param board_state: The current board state with all four players.
        :return: A list of dictionaries, each representing a successor of the form
        {new_state: [...], action: (...), categories: X}. If there are no successors, this method returns None.
        """

        if board_state is None:
            return None

        # If somebody has won, there are no successors
        for p in board_state:
            if p.state[58] == 1:
                return None

        successors = []

        cur_player_board = board_state[self.id].state

        # First, check if there are pieces at the starting position: we can release one if dice = 6
        if cur_player_board[0] > 0 and dice_value == 6:
            # Copy the board state for the new successor
            new_successor = copy.deepcopy(board_state)

            # Take a piece out of the starting position
            new_successor[self.id].state[0] -= 0.25
            new_successor[self.id].state[1] += 0.25

            # Incorporate the action information
            new_successor_w_action = {"new_state": new_successor,
                                      "action": (0, 1),
                                      "categories": Player.RANDOM_MOVE}

            successors.append(new_successor_w_action)

        # Second, check pieces in the circular track up to location 50 (51 will be handled later)
        for loc in range(1, 58):
            if cur_player_board[loc] == 0:
                continue

            # Copy the board state for the new successor
            new_successor = copy.deepcopy(board_state)

            # Check if there is a blockade that prevents moving a piece at loc
            blockade_found = False

            tmp_loc_lo = loc + 1
            tmp_loc_hi = tmp_loc_lo + dice_value

            # We must skip location 52
            if tmp_loc_lo <= 52 < tmp_loc_hi:
                tmp_loc_hi += 1

            for tmp_loc in range(tmp_loc_lo, tmp_loc_hi):
                # We don't need to worry about location 52 or (58 and after)
                if tmp_loc == 52 or (tmp_loc >= 58):
                    continue

                # We don't need to worry about safe squares
                if tmp_loc in SafeSquares:
                    continue

                # We have to worry about blockades formed by the current player
                if board_state[self.id].state[tmp_loc] >= 0.5:
                    blockade_found = True
                    break

                # Check if any of the next players have a blockade (this is needed only for location <= 51)
                if tmp_loc <= 51:
                    for np in range(1, 4):
                        if self.get_c_track_pieces_next_player(new_successor, np, tmp_loc) >= 0.5:
                            blockade_found = True
                            break

                    if blockade_found:
                        break

            if blockade_found:
                continue

            # At this point there is no blockade: we can move to the piece (but we can't move past home = 58)
            new_loc = loc + dice_value

            # We remember to skip square 52:
            if loc <= 52 <= new_loc:
                new_loc += 1

            if new_loc <= 58:
                new_successor[self.id].state[loc] -= 0.25
                new_successor[self.id].state[new_loc] += 0.25

                # Check if any opponent pieces were knocked off (first check if new_loc is a safe square)
                if new_loc <= 51 and new_loc not in SafeSquares:
                    for np in range(1, 4):
                        opp_pieces_knocked = self.get_c_track_pieces_next_player(new_successor, np, new_loc)

                        if self.get_c_track_pieces_next_player(new_successor, np, new_loc) > 0:
                            self.set_c_track_pieces_next_player(new_successor, np, new_loc, 0)
                            new_successor[(self.id + np) % 4].state[0] += opp_pieces_knocked

                # Incorporate action information
                new_successor_w_action = {"new_state": new_successor,
                                          "action": (loc, new_loc),
                                          "categories": Player.RANDOM_MOVE}

                successors.append(new_successor_w_action)

        if len(successors) > 0:
            # Categorize the successors
            for s in successors:
                if self.transition_is_defensive(board_state, s['action'], s['new_state']):
                    s['categories'] += Player.DEFENSIVE_MOVE

                if self.transition_is_aggressive(board_state, s['action'], s['new_state']):
                    s['categories'] += Player.AGGRESSIVE_MOVE

                if self.transition_is_fast(board_state, s['action'], s['new_state']):
                    s['categories'] += Player.FAST_MOVE

                if self.transition_is_release(board_state, s['action'], s['new_state']):
                    s['categories'] += Player.RELEASE_MOVE

            return successors
        else:
            return None

    def board_state_and_action_to_nn_inputs(self, board_state, action):
        """
        Transform a state-action pair to an input suitable for a neural network.

        :param board_state: The board state with 4 players.
        :param action: The action as a tuple (src, dst).
        :return: A list of 238 elements: the first 59 elements represent the state of the current player. The next
        59 elements represent the state of the next player. And so on. The last two elements represent the action
        normalized between 0 and 1.
        """

        compact = False

        if not compact:
            inputs = [0.0, ] * 238

            # First, put the state of all players
            i = 0

            for p_order in range(0, 4):
                for s in board_state[(self.id + p_order) % 4].state:
                    inputs[i] = s
                    i += 1

            # Next, put the action
            inputs[236] = action[0] / 58.0
            inputs[237] = action[1] / 58.0

            return inputs
        else:
            inputs = [0.0, ] * 18
            inputs_i = 0

            tmp = copy.deepcopy(board_state)

            for pi in range(0, 4):
                for i in range(len(tmp[(self.id + pi) % 4].state)):
                    while tmp[(self.id + pi) % 4].state[i] > 0.0:
                        inputs[inputs_i] = i
                        inputs_i += 1
                        tmp[(self.id + pi) % 4].state[i] -= 0.25

            inputs[16] = action[0]
            inputs[17] = action[1]

            for i in range(len(inputs)):
                inputs[i] /= 58.0

            return inputs

    def move(self, dice_value, players, timestamp):
        """
        Given a board state, make a move if possible. The passed board state is modified to reflect the new state after
        the move. If no move is possible, the function does not change the board state. This function calls
        self.select_new_state(...) to get the new state. Actual players need to override that method. A copy of the
        board state is passed to that method, so any modifications to that parameter are lost.

        :param dice_value: The value of the dice roll.
        :param players: Current board state with 4 players.
        :param timestamp: Turn number to associate with the move if successful.
        """

        # Get the possible new states
        successors = self.get_next_states(dice_value, players)

        # Select the new state
        if successors is not None:
            successor = successors[self.select_new_state(players, successors, timestamp)]

            # Memorize the result
            self.board_state = copy.deepcopy(successor["new_state"])
            self.action = (successor["action"][0], successor["action"][1])
            self.timestamp = timestamp

            # Modify the passed parameter to reflect the move
            for p in range(len(players)):
                for l in range(len(players[p].state)):
                    players[p].state[l] = self.board_state[p].state[l]

    def select_new_state(self, board_state, successors, timestamp):
        """
        Actual players (sub-classes) need to override this method to implement their own strategy. This method will
        only be called if successors is not Null.

        :param board_state: The current board state for all four players.
        :param successors: A list of successors to choose from. Each successor is a dictionary with two string keys:
        "new_state" is the new board state (all four players) and "action" is a tuple where the first element is the
        position of a piece in this player's current state and the second element is the position of that piece in this
        player's next state. Each new_state is a list of 4 players. The overriding method should only be accessing the
        state member of each of these elements.
        :param timestamp: The turn number.
        :return: The index of the chosen successor in the successors list.
        """

        return 0
