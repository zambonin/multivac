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
        self.factors = self.nuple_factors()

    def __str__(self):
        """Pretty-prints the board with black and white bullets."""
        os.system('cls' if os.name == 'nt' else 'clear')

        letter_row = "     " + " ".join(
            chr(i) for i in range(65, 65 + len(self.board[0]))) + '\n'
        top_row = '   ┏' + '━' * (2 * len(self.board[0]) + 1) + '┓\n'
        bottom_row = '   ┗' + '━' * (2 * len(self.board[0]) + 1) + '┛'
        mid_rows = ""

        for row, i in zip(self.board, range(len(self.board))):
            mid_rows += '{:02d} ┃ '.format(i + 1) + ' '.join(
                self.stones[i] for i in row) + ' ┃\n'

        return letter_row + top_row + mid_rows + bottom_row

    def nuple_factors(self, default=0.1):
        """
        Produces the right factors given a 1-uple initial value. In the case
        of Gomoku, one n-uple should always be worth more than all the
        (n-1)-uples combined. Hence, choosing a value for the lowest n-uple
        possible will drastically affect the bigger ones.

        15 - n + 1 is the number of n-uples with the same color consecutively
        in a row; there are three axis (horizontal, vertical and diagonal);
        and about 7.5 rows (112~113 maximum stones for a given player, divided
        by 15 rows).

        Args:
            default:    value of a single piece in the board matrix
                        representation.

        Returns:
            Dictionary with length of n-uple as key and its
            multiplicative factor as value.
        """
        factors = [default]
        for i in range(2, 5):
            nuples = (self.side - i + 1) * 3 * 7.5
            factors += [round(nuples * factors[i - 2:i - 1][0])]

        return {i + 1: j for i, j in enumerate(factors)}

    def diagonals(self, invert=True):
        """
        Creates lists with all the board matrix's diagonals, starting from the
        bottom-left element and going towards the top-right. Based on [1].

        Args:
            invert: inverts the board to create antidiagonals.

        Returns:
            All the diagonals from the matrix.

        [1] http://stackoverflow.com/a/23069625
        """
        board = [i[::-1] for i in self.board] if invert else self.board
        diags, hgt, wdt = [], len(board), len(board[0])

        for i in range(hgt + wdt - 1):
            poss_range = range(max(i - wdt + 1, 0), min(hgt - 1, i) + 1)
            diags.append([board[hgt - 1 - j][i - j] for j in poss_range])

        return diags

    def victory(self):
        """
        Covers all the possible victory conditions given a board with some
        configuration of stones.

        Returns:
            True if there exists a set of five stones with the same color
            horizontally, vertically or diagonally aligned on the board,
            False otherwise.
        """
        for board in [self.board, zip(*self.board),
                      self.diagonals(), self.diagonals(invert=True)]:
            for row in board:
                lengths = ((piece, sum(1 for _ in group))
                           for piece, group in groupby(row))
                if any(i and j >= 5 for i, j in lengths):
                    return True
        return False

    def place_stone(self, player, position):
        """
        Places a stone on the desired position if it is available.

        Args:
            player:     a integer representing the player; 1 uses the black
                        stones and -1, the white ones.
            position:   the board matrix's coordinates for the play.
        """
        x_coord, y_coord = position
        self.board[x_coord][y_coord] = player

    def is_empty_space(self, position):
        """
        Checks if a given position on the board matrix is empty.

        Args:
            position:   the board matrix's coordinates.

        Returns:
            True if the position is empty, False otherwise.
        """
        x_coord, y_coord = position
        return self.board[x_coord][y_coord] == 0

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
        x_coord, y_coord = position
        neighbors = []

        for i in range(1, radius + 1):
            neighbors += list(starmap(lambda a, b: (x_coord + a, y_coord + b),
                                      product((0, -i, +i), (0, -i, +i))))

        return list(filter(
            lambda x: x != position and all((0 <= j < self.side) for j in x),
            neighbors))

    def empty_neighbors(self, board, position, radius):
        """
        Checks if neighbors are empty given a starting coordinate.

        Args:
            board:      the matrix representation for the board.
            position:   the board matrix's coordinates for the last play.
            radius:     depth of the neighbor search around the coordinate.

        Returns:
            List of empty neighbors' coordinates.
        """
        return [(i, j) for i, j in self.neighbor_board(position, radius)
                if not board[i][j]]

    def filled_spaces(self, player):
        """
        Elaborates which spaces of the board matrix were played by some
        player, or are empty (if the player argument is zero).

        Args:
            board:  the matrix representation for the board.
            player: a integer representing the player, or its absence.

        Returns:
            List with the coordinates of the valid places.
        """
        size = range(len(self.board))
        _list = [[(i, j) for j in size if self.board[i][j] == player]
                 for i in size]

        return list(chain.from_iterable(_list))

    def row_values(self, board, player):
        """
        Calculates a numeric 'score' for the board state given
        the horizontally aligned stones of the same color.

        This calculation takes in account consecutive groupings
        (n-uples), n-uples (with n > 3) that need only one stone
        to be completed, generally in the middle, and how many
        "open sides" there are for a combination.

        Args:
            board:  the matrix representation for the board.
            player: a integer representing a player.

        Returns:
            An integer that reflects these factors.
        """
        open_sides = {2: 1, 1: 1 / 2, 0: 0.1}
        value = 0

        for row in (i for i in board if sum(i)):
            row = [2] + list(row) + [2]
            lengths = [[piece, sum(1 for _ in group)]
                       for piece, group in groupby(row)]

            for i in range(1, len(lengths) - 1):
                sides = lengths[i - 1][0] == 0 + lengths[i + 1][0] == 0
                if (lengths[i] == [0, 1] and
                        lengths[i - 1][1] + lengths[i + 1][1] >= 4 and
                        lengths[i - 1][0] == lengths[i + 1][0] == player):
                    return 2**32
                elif lengths[i][0] == player:
                    if lengths[i][1] >= 4 and sides:
                        return 2**32
                    else:
                        value += (self.factors[lengths[i][1]] *
                                  open_sides[sides])

        return value

    def col_values(self, board, player):
        """
        Calculates a numeric 'score' for the board state given
        the vertically aligned stones of the same color.

        Args:
            board:  the matrix representation for the board.
            player: a integer representing a player.

        Returns:
            An integer that reflects these factors.
        """
        return self.row_values(zip(*board), player)

    def diag_values(self, board, player):
        """
        Calculates a numeric 'score' for the board state given
        the diagonally aligned stones of the same color.

        Args:
            board:  the matrix representation for the board.
            player: a integer representing a player.

        Returns:
            An integer that reflects these factors.
        """
        return (self.row_values(self.diagonals(board), player) +
                self.row_values(self.diagonals(invert=True), player))

    def evaluate(self, board, player):
        """
        Calculates a numeric 'score' for the board state given the
        combinations with already placed stones.

        In the case of Gomoku, one n-uple should always be worth more
        than all the (n-1)-uples combined (that can be calculated through
        simple combinatorics). Hence, choosing a value for the lowest n-uple
        possible will drastically affect the bigger ones.

        Args:
            board:  the matrix representation for the board.
            player: a integer representing a player.

        Returns:
            An integer that takes in account the groupings of stones
            with the same color, representing their contribution to
            a possible victory.
        """
        value = 0
        for i in ('row', 'col', 'diag'):
            func = getattr(self, '{}_values'.format(i))
            value += func(board, player) - func(board, -player)

        return value

    def rnd_board(self):
        """
        Produces a randomly populated board for debugging purposes, overriding
        the attribute for the class.
        """
        self.board = [[randint(-1, 1) for _ in range(self.side)]
                      for _ in range(self.side)]
