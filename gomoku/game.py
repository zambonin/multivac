#!/usr/bin/python3
# -*- coding: utf-8 -*-
# pylint: disable=W1632,W1638

"""game.py

Control logic for the Gomoku game and main class for the program.
"""

from __future__ import absolute_import
from itertools import cycle
from re import match

from gomoku_board import GomokuBoard
from minimax import ab_pruning


def clear_line():
    """
    VT100 terminal control codes for a pretty loop. \x1b is the VT100
    representation of <ESC> and the single bracket is a "Control Sequence
    Introducer". 1A moves the cursor up a single time, and 2K clears the
    entire line. [1]

    [1] http://www.termsys.demon.co.uk/vtansi.htm
    """
    cursor_up, erase_line = "\x1b[1A", "\x1b[2K"
    print(cursor_up + erase_line + cursor_up)


def player_input(board, player):
    """
    Input loop for the game. Matches valid coordinates on the board.

    Args:
        board:  a GomokuBoard object.
        player: integer in the set {-1, 1}.

    Returns:
        A tuple with the (x, y) coordinates on the Cartesian coordinate system.
    """
    while True:
        try:
            raw = input(
                "   Place {} on which coordinate? ".format(board.stones[player])
            )

            raw = raw.upper() if raw else "error"

            if match(r"Q[UIT]?", raw):
                raise SystemExit

            if raw[-1] in map(chr, range(65, 80)):
                # invert raw input if letter was typed after number
                raw = raw[len(raw) - 1 :] + raw[: len(raw) - 1]

            valid_pos = match(r"[A-O](0?[1-9]|1[0-5])\Z", raw)
            pos = (int(raw[1:]) - 1, ord(raw[:1]) - 65)

            if len(pos) != 2 or not valid_pos or not board.is_empty_space(pos):
                raise ValueError
            break
        except ValueError:
            clear_line()

    return pos


def game_loop(board, mode=None):
    """
    Controls the game logic by managing the board, and calling user inputs, or
    the minimax function if a computer is playing.

    Args:
        board:  a GomokuBoard object.
        mode:   a string that decides how the game should act.
    """
    if mode == "exit":
        raise SystemExit

    turn = cycle([1, -1])

    while not board.victory():
        player = next(turn)
        print(board)
        if mode == "shodan" and player == -1:
            _, pos = ab_pruning(board, 2, float("-inf"), float("inf"), player)
        else:
            pos = player_input(board, player)
        board.place_stone(player, pos)

    message = (
        "\nDraw!"
        if board.draw()
        else "\nWinner: {}".format(board.stones[player])
    )

    print(board, message)
    board.clear()


def main():
    """Menu for the game."""
    choices = {
        "0": dict(desc="quit", mode="exit"),
        "1": dict(desc="human x human", mode="two_player"),
        "2": dict(desc="human x computer", mode="shodan"),
    }

    for key in sorted(choices.keys()):
        print("[{}] {}".format(key, choices[key]["desc"]))
    while True:
        option = input("Choice: ")
        if option in choices.keys():
            game_loop(GomokuBoard(15), choices[option]["mode"])
        clear_line()


if __name__ == "__main__":
    main()
