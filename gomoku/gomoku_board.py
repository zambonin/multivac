#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""gomoku_board.py

Gomoku, also called "five in a row", is a game traditionally played on a
15 * 15 board with black and white stones. These may not be removed once
played. A victory occurs if a player forms an unbroken row of five or
more stones horizontally, vertically or diagonally.
"""

import os

from itertools import chain, groupby, product, starmap
from random import randint


class GomokuBoard():
    """Board with n * n intersections where stones are placed."""

    def __init__(self, side):
        """
        Inits GomokuBoard with the attributes introduced above.

        Args:
            side:   size of the square's side for the board.
        """
        assert side >= 5, "No victory conditions!"
        self.side = side
        self.board = [[0 for _ in range(side)] for _ in range(side)]
        self.stones = {0: ' ', 1: '●', -1: '○'}

    def __str__(self):
        """Pretty-prints the board with black and white bullets."""
        os.system('cls' if os.name == 'nt' else 'clear')

        top_row = '┏' + '━' * (2 * len(self.board) + 1) + '┓\n'
        bottom_row = '┗' + '━' * (2 * len(self.board) + 1) + '┛'
        mid_rows = ""

        for row, i in zip(self.board, range(len(self.board))):
            mid_rows += '┃ ' + ' '.join([self.stones[i] for i in row]) + ' ┃\n'

        return top_row + mid_rows + bottom_row

    def h_victory(self, board):
        """
        Tests possible horizontal victories grouping consecutive similar
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
        """
        Tests possible vertical victories checking horizontal alignments
        within the board's transposed matrix representation.

        Args:
            board:  the matrix representation for the board.

        Returns:
            True if there exists a set of five or more stones with the same
            color vertically aligned on the board, False otherwise.
        """
        return self.h_victory(zip(*board))

    def d_victory(self, board):
        """
        Tests possible diagonal victories checking horizontal alignments
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
        """
        Creates lists with all the board matrix's diagonals, starting from the
        (n, 1)th element and going towards the (1, n)th, where `n` is the
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
        """
        Creates lists with all the antidiagonals, reversing the board matrix
        such that the starting element need not be changed.

        Returns:
            All antidiagonals with length greater than five.
        """
        return self.diagonals([i[::-1] for i in board])

    def victory(self):
        """
        Covers all the possible victory conditions given a board with some
        configuration of stones.

        Returns:
            True if there exists a set of five stones with the same color
            horizontally, vertically or diagonally aligned on the board,
            False otherwise.
        """
        return (self.h_victory(self.board) or self.v_victory(self.board) or
                self.d_victory(self.board))

    def place_stone(self, player, position):
        """
        Places a stone on the desired position if it is available.

        Args:
            player:     a integer representing the player; 1 uses the black
                        stones and -1, the white ones.
            position:   the board matrix's coordinates for the play.
        """
        x, y = position
        self.board[x][y] = player

    def is_empty_space(self, position):
        """
        Checks if a given position on the board matrix is empty.

        Args:
            position:   the board matrix's coordinates.

        Returns:
            True if the position is empty, False otherwise.
        """
        x, y = position
        return self.board[x][y] == 0

    def clear(self):
        """
        Wipes all the plays from the board, which is equivalent to nullify all
        the contents of the board matrix's coordinates.
        """
        self.board = [[0 for _ in range(self.side)] for _ in range(self.side)]

    def draw(self):
        """
        Checks if the entire board is filled with stones.

        Returns:
            True if all the board is filled and there has not been a winner,
            False otherwise.
        """
        return (all(all(i for i in row) for row in self.board) and
                not self.victory())

    def neighbor_board(self, position, radius):
        """
        Generates the valid neighbors given a starting coordinate.

        Args:
            position:   the board matrix's coordinates for the last play.
            radius:     depth of the neighbor search around the coordinate.

        Returns:
            List of neighbors' coordinates.
        """
        x, y = position
        neighbors = []

        for i in range(1, radius + 1):
            neighbors += list(starmap(lambda a, b: (x + a, y + b),
                                      product((0, -i, +i), (0, -i, +i))))

        valid = [i for i in neighbors if all((0 <= j < self.side) for j in i)]

        return list(set(valid) - set([position]))

    def filled_spaces(self, board, player):
        """
        Elaborates which spaces of the board matrix were played by some
        player, or are empty (if the player argument is zero).

        Args:
            board:  the matrix representation for the board.
            player: a integer representing the player, or its absence.

        Returns:
            List with the coordinates of the valid places.
        """
        size = range(len(board))
        _list = [[(i, j) for j in size if board[i][j] == player] for i in size]

        return list(chain.from_iterable(_list))

    def row_nuples(self, board, player, n):
        """
        Sweeps the rows of the board matrix looking for groupings of stones
        with the same color.

        Args:
            board:  the matrix representation for the board.
            player: a integer representing the player.
            n:      length of groupings.

        Returns:
            Quantity of horizontal n-uples played by some player.
        """
        qnt = 0
        for row in board:
            lengths = [(piece, sum(1 for _ in group))
                       for piece, group in groupby(row)]
            qnt += len([i for i in lengths if i[0] == player and i[1] == n])

        return qnt

    def col_nuples(self, board, player, n):
        """
        Sweeps the columns of the board matrix looking for groupings of stones
        with the same color.

        Args:
            board:  the matrix representation for the board.
            player: a integer representing the player.
            n:      length of groupings.

        Returns:
            Quantity of vertical n-uples played by some player.
        """
        return self.row_nuples(zip(*board), player, n)

    def diag_nuples(self, board, player, n):
        """
        Sweeps the diagonals of the board matrix looking for groupings of
        stones with the same color.

        Args:
            board:  the matrix representation for the board.
            player: a integer representing the player.
            n:      length of groupings.

        Returns:
            Quantity of diagonal n-uples played by some player.
        """
        return (self.row_nuples(self.diagonals(board), player, n) +
                self.row_nuples(self.antidiagonals(board), player, n))

    def nuples_quantity(self, board, player, n):
        """
        Sweeps the entire board matrix looking for groupings of stones with
        the same color.

        Args:
            board:  the matrix representation for the board.
            player: a integer representing the player.
            n:      length of groupings.

        Returns:
            Quantity of n-uples played by some player throughout the board.
        """
        return (self.row_nuples(board, player, n) +
                self.col_nuples(board, player, n) +
                self.diag_nuples(board, player, n))

    def rnd_board(self):
        """
        Produces a randomly populated board for debugging purposes, overriding
        the attribute for the class.
        """
        self.board = [[randint(-1, 1) for _ in range(self.side)]
                      for _ in range(self.side)]
