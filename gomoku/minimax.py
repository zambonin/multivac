#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""minimax.py

Class where various methods regarding heuristics for the game are placed.
"""

from copy import deepcopy
from itertools import chain
from random import choice


class Minimax():
    """
    Decision rule for minimizing the possible loss in a worst case
    scenario. It assumes that the first player is maximizing his chance
    of winning, and its opponent is trying to minimize that same chance
    (i.e. maximize its own chances).
    """

    def ab_pruning(self, board, depth, alpha, beta, player):
        """
        Improvement over the naïve minimax algorithm that seeks to decrease
        the number of nodes evaluated by the algorithm through pruning: if a
        subtree of the game graph is proven to be worse than some previously
        analysed node, then it needs not be analysed and as such, may be
        discarded. Hence, deeper searches may be performed.

        Args:
            board:  a GomokuBoard object.
            depth:  maximum depth before end of recursion; deeper searches
                    may perform better, although at a cost.
            alpha:  maximum score that the maximizing player is assured of.
            beta:   minimum score that the minimizing player is assured of.
            player: a integer representing the maximizing player.

        Returns:
            A tuple containing the score for a given board, and the best move
            evaluated by the algorithm.
        """
        filled_spots = list(chain.from_iterable(
            board.filled_spaces(board.board, i) for i in [1, -1]))
        empty_neighbors = list(chain.from_iterable(
            board.empty_neighbors(board.board, i, 1) for i in filled_spots))

        all_empty = board.filled_spaces(board.board, 0)
        moves = sorted(list(set(all_empty).intersection(empty_neighbors)))

        final_move_list = all_empty if not moves else moves

        if depth == 0:
            return self.evaluate(board, player), final_move_list[0]

        move = None

        while final_move_list:
            new_move = choice(final_move_list)
            temp_board = deepcopy(board)
            temp_board.place_stone(-player, new_move)

            if temp_board.victory():
                return self.evaluate(board, player) + 26000000, new_move

            temp = self.ab_pruning(temp_board, depth - 1, alpha, beta, -player)
            temp_score = temp[0]

            if player == -1:
                if temp_score > alpha:
                    alpha = temp_score
                    move = new_move
                if alpha >= beta:
                    break
            else:
                if temp_score < beta:
                    beta = temp_score
                    move = new_move
                if alpha >= beta:
                    break

            final_move_list.pop(0)

        score = alpha if player == -1 else beta
        return score, move

    def evaluate(self, board, player):
        """
        Calculates a numeric 'score' for the board state given the
        combinations with already placed stones.

        In the case of Gomoku, one n-uple should always be worth more
        than all the (n-1)-uples combined (that can be calculated through
        simple combinatorics). Hence, choosing a value for the lowest n-uple
        possible will drastically affect the bigger ones.

        Args:
            board:  a GomokuBoard object.
            player: a integer representing a player.

        Returns:
            An integer that takes in account the groupings of stones
            with the same color, representing their contribution to
            a possible victory.
        """
        return sum(board.nuples_quantity(player, i) * j
                   for i, j in zip([2, 3, 4], [1, 320, 94000]))
