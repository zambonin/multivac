#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""gomoku_board.py

Gomoku, also called "five in a row", is a game traditionally played on a
15 * 15 board with black and white stones. A victory occurs if a player
forms an unbroken row of five or more stones horizontally, vertically or
diagonally.
"""

from itertools import groupby
from random import randint


class GomokuBoard():
    """Board with 15 * 15 intersections where stones are placed. These may
    not be removed once played.
    """

    def __init__(self, side):
        """Inits GomokuBoard with the attributes introduced above.

        Args:
            side:   size of the square's side for the board.
        """
        assert side >= 5, "No victory conditions!"
        self.side = side
        self.board = [[0 for _ in range(side)] for _ in range(side)]

    def __str__(self):
        """Pretty-prints the board with black and white bullets."""
        stones = {0: ' ', 1: '●', -1: '○'}

        top_row = '┏' + '━' * (2 * len(self.board) + 1) + '┓\n'
        bottom_row = '┗' + '━' * (2 * len(self.board) + 1) + '┛'
        middle_rows = ""

        for row, i in zip(self.board, range(len(self.board))):
            middle_rows += '┃ ' + ' '.join([stones[i] for i in row]) + ' ┃\n'

        return top_row + middle_rows + bottom_row

    def h_victory(self, board):
        """Tests possible horizontal victories grouping consecutive similar
        stones and counting their individual lengths, dismissing groups of
        empty spaces.

        Args:
            board:  the matrix representation for the board.

        Returns:
            True if there exists a set of five or more stones with the same
            color horizontally aligned on the board, False otherwise.
        """
        for row in board:
            lengths = ((piece, sum(1 for _ in group))
                       for piece, group in groupby(row))
            if any(i and j >= 5 for i, j in lengths):
                return True
        return False

    def v_victory(self, board):
        """Tests possible vertical victories checking horizontal alignments
        within the board's transposed matrix representation.

        Args:
            board:  the matrix representation for the board.

        Returns:
            True if there exists a set of five or more stones with the same
            color vertically aligned on the board, False otherwise.
        """
        return self.h_victory(zip(*board))

    def d_victory(self, board):
        """Tests possible diagonal victories checking horizontal alignments
        within the board's diagonals and antidiagonals represented as rows.

        Args:
            board:  the matrix representation for the board.

        Returns:
            True if there exists a set of five or more stones with the same
            color diagonally aligned on the board, False otherwise.
        """
        return (self.h_victory(self.diagonals(board)) or
                self.h_victory(self.antidiagonals(board)))

    def diagonals(self, board):
        """Creates lists with all the board matrix's diagonals, starting from
        the (n, 1)th element and going towards the (1, n)th, where `n` is the
        order of the matrix. Based on [1].

        Returns:
            All diagonals with length greater than five, the minimum number
            of stones for a valid victory arrangement.

        [1] http://stackoverflow.com/a/23069625
        """
        diags, side = [], len(board)
        for i in range(2 * side - 1):
            poss_range = range(max(i - side + 1, 0), min(i + 1, side))
            diags.append([board[side - i + j - 1][j] for j in poss_range])

        return [i for i in diags if len(i) >= 5]

    def antidiagonals(self, board):
        """Creates lists with all the antidiagonals, reversing the board
        matrix such that the starting element need not be changed.

        Returns:
            All antidiagonals with length greater than five.
        """
        return self.diagonals([i[::-1] for i in board])

    def victory(self):
        """Covers all the possible victory conditions given a board with some
        configuration of stones.

        Returns:
            True if there exists a set of five stones with the same color
            horizontally, vertically or diagonally aligned on the board,
            False otherwise.
        """
        return (self.h_victory(self.board) or self.v_victory(self.board) or
                self.d_victory(self.board))

    def rnd_board(self):
        """Produces a randomly populated board for debugging purposes,
        overriding the attribute for the class.
        """
        self.board = [[randint(-1, 1) for _ in range(self.side)]
                      for _ in range(self.side)]
