#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""game.py

Control logic for the Gomoku game and main class for the program.
"""

from gomoku_board import GomokuBoard
from itertools import cycle
from random import randint
from os import system


def process_input(board):
    while True:
        try:
            raw = input("Place the stone on: ")
            pos = [int(i) for i in raw.split(",")]
            valid_pos = all(type(i) is int and (0 <= i <= 14) for i in pos)
            if len(pos) != 2 or not valid_pos or not board.is_empty_space(pos):
                raise ValueError
            break
        except ValueError:
            print("Invalid input.", end=' ')

    return pos


def human_human(board):
    turn = cycle([1, -1])
    player = next(turn)

    while not board.victory():
        system('clear')
        print(board, "\nTurn: {}".format(board.stones[player]))
        pos = process_input(board)
        board.place_stone(player, pos)
        player = next(turn)

    system('clear')
    if board.draw():
        print(board, "\nDraw!")
    else:
        print(board, "\nWinner: {}".format(board.stones[next(turn)]))
    board.clear()


def human_random(board):
    turn = cycle([1, -1])
    player = next(turn)

    while not board.victory():
        system('clear')
        print(board, "\nTurn: {}".format(board.stones[player]))
        if player == -1:
            pos = [randint(0, 14) for _ in range(2)]
            while not board.is_empty_space(pos):
                pos = [randint(0, 14) for _ in range(2)]
        else:
            pos = process_input(board)
        board.place_stone(player, pos)
        player = next(turn)

    system('clear')
    if board.draw():
        print(board, "\nDraw!")
    else:
        print(board, "\nWinner: {}".format(board.stones[next(turn)]))
    board.clear()


def main():

    choices = {
        "0": dict(desc="quit", func=exit),
        "1": dict(desc="human x human", func=human_human),
        "2": dict(desc="human x computer (random)", func=human_random),
    }

    print("How do you want to play Gomoku?")
    for key in sorted(choices.keys()):
        print("[{}] {}".format(key, choices[key]["desc"]))
    while True:
        option = input("Choice: ")
        if option not in choices.keys():
            print("Invalid input.", end=' ')
        else:
            board = GomokuBoard(15) if int(option) else 0
            choices[option]["func"](board)


if __name__ == '__main__':
    main()
