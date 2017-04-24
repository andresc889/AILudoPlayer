"""
tk_ludo.py

Provides the TkLudo class, a GUI for a Ludo game.
"""

import random
import Tkinter as Tk
import tkMessageBox

from ludo import Ludo
from human_player import HumanPlayer
from ql_player import QLPlayer
from nn import NN
from player import GetKind


class PlayState:
    playing = 1
    paused = 2


class TkLudo(Ludo):
    """
    Class that provides a GUI for a Ludo game.
    """

    # Board dimensions (in pixels)
    board_w = 650
    board_h = 650

    # Coordinates where to place the indicator for the turn for each player (key = player #)
    tn_poss = {0: (218, 391),
               1: (218, 218),
               2: (391, 218),
               3: (391, 391)}

    # Coordinates of the starting squares for each player (key = player #)
    st_poss = {0:  (110, 499),
               1:  (110, 110),
               2:  (499, 110),
               3:  (499, 499)}

    # Coordinates of each square in the circular track (key = square #, 0 is the square below purple's start position)
    c_track = {0:  (261, 606),
               1:  (261, 563),
               2:  (261, 520),
               3:  (261, 477),
               4:  (261, 434),
               5:  (261, 390),
               6:  (218, 347),
               7:  (175, 347),
               8:  (131, 347),
               9:  (88, 347),
               10: (45, 347),
               11: (2, 347),
               12: (2, 304),
               13: (2, 261),
               14: (45, 261),
               15: (88, 261),
               16: (131, 261),
               17: (174, 261),
               18: (217, 261),
               19: (261, 218),
               20: (261, 175),
               21: (261, 131),
               22: (261, 88),
               23: (261, 45),
               24: (261, 2),
               25: (304, 2),
               26: (347, 2),
               27: (347, 45),
               28: (347, 88),
               29: (347, 131),
               30: (347, 174),
               31: (347, 217),
               32: (390, 261),
               33: (433, 261),
               34: (477, 261),
               35: (520, 261),
               36: (563, 261),
               37: (606, 261),
               38: (606, 304),
               39: (606, 347),
               40: (563, 347),
               41: (520, 347),
               42: (477, 347),
               43: (434, 347),
               44: (390, 347),
               45: (347, 390),
               46: (347, 434),
               47: (347, 477),
               48: (347, 520),
               49: (347, 563),
               50: (347, 606),
               51: (304, 606)}

    # Coordinates of the home track squares for player 0 (key = square #, 5 is home)
    h_trk_0 = {0:  (304, 563),
               1:  (304, 520),
               2:  (304, 477),
               3:  (304, 434),
               4:  (304, 391),
               5:  (304, 368)}

    # Coordinates of the home track squares for player 1 (key = square #, 5 is home)
    h_trk_1 = {0:  (45, 304),
               1:  (88, 304),
               2:  (131, 304),
               3:  (174, 304),
               4:  (218, 304),
               5:  (261, 304)}

    # Coordinates of the home track squares for player 2 (key = square #, 5 is home)
    h_trk_2 = {0:  (304, 45),
               1:  (304, 88),
               2:  (304, 131),
               3:  (304, 174),
               4:  (304, 218),
               5:  (304, 261)}

    # Coordinates of the home track squares for player 3 (key = square #, 5 is home)
    h_trk_3 = {0:  (563, 304),
               1:  (520, 304),
               2:  (477, 304),
               3:  (434, 304),
               4:  (391, 304),
               5:  (347, 304)}

    # Space between square borders and pieces (in pixels)
    square_margin_x = 2
    square_margin_y = 2

    # Piece dimensions (in pixels)
    piece_w = 8
    piece_h = 8

    # Space between pieces (in pixels)
    piece_pad = 2

    # Time (ms) to wait before rolling dice
    dice_before_ms = 200

    # Time (ms) for dice animation
    dice_ms = 5

    # Time (ms) before requesting a player for a move
    move_before_ms = 1000

    # For debugging
    # Predetermined sequence of dice values for debugging
    # pre_dice = [1, 1, 0, 0, 1, 3, 0, 0]

    def __init__(self):
        """
        Constructor for a new Ludo game using a GUI.
        """

        # Initialize a Ludo game
        nn = NN(237, '01062016_nn_exp_2_19_23.txt')
        players = [QLPlayer(id=0, train=False, nn=nn, epsilon=0),
                   HumanPlayer(id=1, name="Andres"),
                   QLPlayer(id=2, train=False, nn=nn, epsilon=0),
                   HumanPlayer(id=3, name="Sol")]

        """players = [QLPlayer(id=0, train=False, nn=nn, epsilon=0),
                   QLPlayer(id=1, train=False, nn=nn, epsilon=0),
                   QLPlayer(id=2, train=False, nn=nn, epsilon=0),
                   QLPlayer(id=3, train=False, nn=nn, epsilon=0)]"""

        Ludo.__init__(self, players)

        # For debugging
        # self.player_turn = 0
        # self.players[0].state[0] = 0.75
        # self.players[0].state[28] = 0.25

        # self.players[1].state[0] = 0.75
        # self.players[1].state[12] = 0.25

        # self.players[2].state[0] = 0.75
        # self.players[2].state[51] = 0.25

        # Initialize Tk frame: http://effbot.org/tkinterbook/tkinter-hello-tkinter.htm
        self.root = Tk.Tk()
        self.root.title("Ludo")
        self.root.resizable(0, 0)

        # Center window: http://stackoverflow.com/questions/14910858/how-to-specify-where-a-tkinter-window-opens
        ws = self.root.winfo_screenwidth()
        hs = self.root.winfo_screenheight() - 50
        x = (ws/2) - (TkLudo.board_w/2)
        y = (hs/2) - (TkLudo.board_h/2)

        self.root.geometry('%dx%d+%d+%d' % (TkLudo.board_w, TkLudo.board_h, x, y))

        # Create canvas: http://stackoverflow.com/questions/15795916/image-behind-buttons-in-tkinter-photoimage
        self.canvas = Tk.Canvas(self.root, width=TkLudo.board_w - 5, height=TkLudo.board_h - 5)
        self.canvas.pack()

        self.board_img = Tk.PhotoImage(file='ludo_board.gif')

        self.playState = PlayState.paused
        self.turn = 0

        self.play_btn = Tk.Button(self.root, text="Start!", width=10)
        self.play_btn.bind('<ButtonRelease-1>', self.handle_play_btn)

        self.onemove_btn = Tk.Button(self.root, text="One Move", width=10)
        self.onemove_btn.bind('<ButtonRelease-1>', self.handle_onemove_btn)

        self.dice_lbl = Tk.Label(self.root, text="", width=2, bg="#fff", font="Helvetica 16 bold", relief=Tk.RAISED)

        self.canvas.create_image(0, 0, image=self.board_img, anchor=Tk.NW)
        self.canvas.create_window(5, 5, window=self.play_btn, anchor=Tk.NW)
        self.canvas.create_window(176, 5, window=self.onemove_btn, anchor=Tk.NW)
        self.canvas.create_window(TkLudo.board_w - 6, 5, window=self.dice_lbl, anchor=Tk.NE)

        self.canvas_pieces_ids = []

        self.draw_current_state()

        self.root.protocol("WM_DELETE_WINDOW", self.handle_quit)
        self.root.mainloop()

    def handle_quit(self):
        """
        Handle the WM_DELETE_WINDOW protocol.
        """

        self.root.destroy()
        self.root = None

    def handle_play_btn(self, event):
        """
        Handle the left button release event on the play button.

        :param event: Event information.
        """

        try:
            if self.playState == PlayState.paused:
                self.playState = PlayState.playing
                self.play_btn.config(text="Pause")

                self.onemove_btn.unbind("<ButtonRelease-1>")
                self.onemove_btn.config(relief=Tk.RAISED, state=Tk.DISABLED)

                self.play()

                self.onemove_btn.bind("<ButtonRelease-1>", self.handle_onemove_btn)
                self.onemove_btn.config(relief=Tk.RAISED, state=Tk.NORMAL)
            else:
                self.playState = PlayState.paused
                self.play_btn.config(text="Play!")

                self.onemove_btn.bind("<ButtonRelease-1>", self.handle_onemove_btn)
                self.onemove_btn.config(relief=Tk.RAISED, state=Tk.NORMAL)

        finally:
            return

    def handle_onemove_btn(self, event):
        """
        Handle the left button release event on the one move button.

        :param event: Event information.
        """

        try:
            self.onemove_btn.unbind("<ButtonRelease-1>")
            self.onemove_btn.config(relief=Tk.RAISED, state=Tk.DISABLED)
            self.playState = PlayState.playing

            self.play_game_or_move(False)

            self.playState = PlayState.paused
            self.onemove_btn.bind("<ButtonRelease-1>", self.handle_onemove_btn)
            self.onemove_btn.config(relief=Tk.RAISED, state=Tk.NORMAL)
        finally:
            return


    def draw_current_state(self):
        """
        Draw the current state of the game (stored in self.players).
        """

        try:
            # Delete all pieces on the board first
            for pid in range(len(self.canvas_pieces_ids)):
                self.canvas.delete(self.canvas_pieces_ids.pop())

            # Place the turn indicator
            x = TkLudo.tn_poss[self.player_turn][0] + 5
            y = TkLudo.tn_poss[self.player_turn][1] + 5

            self.canvas_pieces_ids.append(self.canvas.create_oval(x, y, x + 30, y + 30, fill="#f9c60e"))
            self.canvas_pieces_ids.append(self.canvas.create_text(x + 16, y + 16, font="Helvetica 15 bold", text="P"))

            # Go through the positions for each player:
            position_offsets = [0, 13, 26, 39]
            colors = ["#ff00de", "#13a200", "#8e0000", "#00cccf"]
            home_tracks = [TkLudo.h_trk_0, TkLudo.h_trk_1, TkLudo.h_trk_2, TkLudo.h_trk_3]

            for player in range(len(self.players)):
                for position in range(len(self.players[player].state)):
                    if self.players[player].state[position] == 0:
                        continue

                    num_pieces = int(4 * self.players[player].state[position])
                    color = colors[player]

                    """
                    # Draw player kind labels
                    x = TkLudo.tn_poss[player][0] + 5
                    if player == 0 or player == 3:
                        y = TkLudo.tn_poss[player][1] + 40
                    else:
                        y = TkLudo.tn_poss[player][1] - 40

                    self.canvas_pieces_ids.append(self.canvas.create_oval(x, y, x + 30, y + 30, fill="#aaaaaa"))
                    self.canvas_pieces_ids.append(
                        self.canvas.create_text(
                            x + 16, y + 16, font="Helvetica 15 bold", text=GetKind(self.players[player].kind)))

                    # Draw player id labels
                    y = TkLudo.tn_poss[player][1] + 5
                    if player == 0 or player == 1:
                        x = TkLudo.tn_poss[player][0] - 40
                    else:
                        x = TkLudo.tn_poss[player][0] + 40

                    self.canvas_pieces_ids.append(self.canvas.create_oval(x, y, x + 30, y + 30, fill=color))
                    self.canvas_pieces_ids.append(
                        self.canvas.create_text(
                            x + 16, y + 16, font="Helvetica 15 bold", text=str(player)))
                    """

                    if position == 0:
                        # Handle the starting position
                        for pc in range(num_pieces):
                            x = (TkLudo.st_poss[player][0] + TkLudo.square_margin_x) + \
                                (TkLudo.piece_w + TkLudo.piece_pad) * pc - 1
                            y = (TkLudo.st_poss[player][1] + TkLudo.square_margin_y)

                            fid = self.canvas.create_oval(x, y, x + TkLudo.piece_w, y + TkLudo.piece_h, fill=color)
                            self.canvas_pieces_ids.append(fid)
                    elif 1 <= position <= 52:
                        # Handle positions in the circular track
                        sq = (position + position_offsets[player]) % 52

                        for pc in range(num_pieces):
                            x = (TkLudo.c_track[sq][0] + TkLudo.square_margin_x) + \
                                (TkLudo.piece_w + TkLudo.piece_pad) * pc - 1
                            y = (TkLudo.c_track[sq][1] + TkLudo.square_margin_y) + \
                                (TkLudo.piece_h + TkLudo.piece_pad) * player - 1

                            fid = self.canvas.create_oval(x, y, x + TkLudo.piece_w, y + TkLudo.piece_h, fill=color)
                            self.canvas_pieces_ids.append(fid)
                    elif 53 <= position <= 58:
                        # Handle positions in the home track
                        sq = position - 53

                        for pc in range(num_pieces):
                            x = (home_tracks[player][sq][0] + TkLudo.square_margin_x) + \
                                (TkLudo.piece_w + TkLudo.piece_pad) * pc - 1
                            y = (home_tracks[player][sq][1] + TkLudo.square_margin_y)

                            fid = self.canvas.create_oval(x, y, x + TkLudo.piece_w, y + TkLudo.piece_h, fill=color)
                            self.canvas_pieces_ids.append(fid)

            self.canvas.update()
        finally:
            return

    def delay(self, ms):
        """
        Block for a specified number of milliseconds.
        """

        if self.root is None:
            exit()
        else:
            self.root.after(ms)

    def roll_dice(self):
        """
        Override the parent method to provide animation.

        :return: A random number between 1 and 6.
        """

        self.dice_lbl.config(text="")
        self.canvas.update()

        self.delay(self.dice_before_ms)

        roll = 0

        for i in range(10):
            roll = random.randint(1, 6)
            self.dice_lbl.config(text=str(roll))
            self.canvas.update()
            self.delay(self.dice_ms)

        # For debugging
        # roll = self.pre_dice.pop(0)
        # self.dice_lbl.config(text=str(roll))
        # self.canvas.update()

        return roll

    def roll_manual_dice(self):
        """
        Prompt the user for a dice value.

        :return: A number between 1 and 6.
        """

        # Prompt for a dice value
        print "****************************************"

        while True:
            dice = input("Enter dice value: ")

            if 1 <= dice <= 6:
                break

        print "****************************************"
        print

        return dice

    def play(self):
        """
        Override the parent method to provide an interface to start a Ludo game.
        """

        self.play_game_or_move(True)

    def play_game_or_move(self, entire_game):
        """
        Plays an entire Ludo game or a single move.

        :param entire_game: If True, then the entire game is played. Otherwise, a single move is played.
        """

        # Keep track of the turn number as a timestamp

        while self.playState == PlayState.playing:
            cur_player = self.players[self.player_turn]

            # Roll dice
            dice = self.roll_manual_dice()

            self.delay(self.move_before_ms)

            # Prompt player for a move
            cur_player.move(dice, self.players, self.turn)

            # Update board state
            self.draw_current_state()

            # Check for a winner
            if Ludo.player_wins(cur_player):
                tkMessageBox.showinfo("Game Over!", "Player " + str(cur_player.id) + " won!", parent=self.root)
                return

            # Next player
            self.player_turn = (self.player_turn + 1) % 4

            # Update board state
            self.draw_current_state()

            self.turn += 1

            if not entire_game:
                break

TkLudo()
