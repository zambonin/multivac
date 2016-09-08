#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""game.py

Control logic for the Gomoku game and main class for the program.
"""

from gomoku_board import GomokuBoard
from itertools import cycle
from minimax import Minimax
from random import choice, randint
from re import fullmatch


def player_input(board, player):

    while True:
        try:
            raw = input("   Place {} on which coordinate? ".format(
                board.stones[player]))

            raw = raw.upper() if raw else 'error'
            if raw[-1] in map(chr, range(65, 80)):
                raw = raw[len(raw)-1:] + raw[:len(raw)-1]

            valid_pos = fullmatch(r'[A-O](0?[1-9]|1[0-5])', raw)
            pos = (int(raw[1:]) - 1, ord(raw[:1]) - 65)

            if len(pos) != 2 or not valid_pos or not board.is_empty_space(pos):
                raise ValueError
            break
        except ValueError:
            print("   Invalid input.")

    return pos


def random_input(board):

    pos = [randint(0, 14) for _ in range(2)]
    while not board.is_empty_space(pos):
        pos = [randint(0, 14) for _ in range(2)]

    return pos


def game_loop(board, mode=None):

    if mode == 'exit':
        raise SystemExit

    turn = cycle(choice(([1, -1], [-1, 1])))
    mmax = Minimax()

    while not board.victory():
        player = next(turn)
        print(board)
        if mode == 'ai' and player == -1:
            s, pos = mmax.ab_pruning(board, 2, float('-inf'),
                                     float('inf'), player)
        elif mode == 'shodan':
            s, pos = mmax.ab_pruning(board, 2, float('-inf'),
                                     float('inf'), player)
        elif mode == 'random' and player == -1:
            pos = random_input(board)
        else:
            pos = player_input(board, player)
        board.place_stone(player, pos)

    message = "\nDraw!" if board.draw() else "\nWinner: {}".format(
        board.stones[player])

    print(board, message)
    board.clear()


def main():

    choices = {
        "0": dict(desc="quit", mode='exit'),
        "1": dict(desc="human x human", mode='two_player'),
        "2": dict(desc="human x computer (random)", mode='random'),
        "3": dict(desc="human x computer (AI)", mode='ai'),
        "4": dict(desc="computer x computer", mode='shodan')
    }

    while True:
        for key in sorted(choices.keys()):
            print("[{}] {}".format(key, choices[key]["desc"]))
        option = input("Choice: ")
        if option not in choices.keys():
            print("Invalid input.")
        else:
            game_loop(GomokuBoard(15), choices[option]['mode'])


if __name__ == '__main__':
    main()
