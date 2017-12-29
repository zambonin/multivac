#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""truck_driver.py

A fuzzy driver for a virtual truck. Run `java -jar fuzzy_truck_contest.jar`
and click "Iniciar/Reiniciar" to start the socket. Then, run this program
and it will try its best to park the truck.

    * `skfuzzy.defuzz` is the defuzzification function,
        using the centroid method;
    * `skfuzzy.interp_membership` finds the degree of membership
        for a given variable using linear interpolation;
    * `skfuzzy.trimf` is the triangular membership function generator.
    * Information about the `socket` parameters can be found here [1].

[1] http://man7.org/linux/man-pages/man2/socket.2.html
"""

from math import floor
from socket import socket, AF_INET, SOCK_STREAM
from sys import argv

import matplotlib.pyplot as plt
from numpy import arange, fmin, fmax
from skfuzzy import defuzz, interp_membership, trimf


def _min(_list):
    """
    Shorter way of minimizing variables and vectors.

    Args:
        _list:  a list with floating point numbers and a vector as its last
                member. Within this context, these are informations about the
                truck and how much it should turn.

    Returns:
        A NumPy array with the smallest numbers between the first arguments
        and the vector coordinate it is being compared to.
    """
    return fmin(fmin.reduce(_list[:-1]), _list[-1])


def normalize_angle(angle):
    """
    Shifts the truck to the right.

    Args:
        angle:  the number to be normalized.

    Returns:
        The normalized number.
    """
    return floor(((angle + 90) % 360.0) - 180.0)


def plot_fuzzy_sets():
    """Shows the fuzzy sets constructed below in pretty colors."""
    _, (ax0, ax1, ax2) = plt.subplots(nrows=3, figsize=(8, 9))

    ax0.plot(X_DIST, X_LO, 'b', linewidth=1.5, label='Left')
    ax0.plot(X_DIST, X_MD, 'g', linewidth=1.5, label='Center')
    ax0.plot(X_DIST, X_HI, 'r', linewidth=1.5, label='Right')
    ax0.set_title('X Distance')
    ax0.legend()

    ax1.plot(ANGLE_RANGE, A_STRG_LEFT, 'b', linewidth=1.5, label='Str. left')
    ax1.plot(ANGLE_RANGE, A_WEAK_LEFT, 'g', linewidth=1.5, label='Left')
    ax1.plot(ANGLE_RANGE, A_STRAIGHT, 'r', linewidth=1.5, label='Straight')
    ax1.plot(ANGLE_RANGE, A_WEAK_RIGHT, 'k', linewidth=1.5, label='Right')
    ax1.plot(ANGLE_RANGE, A_STRG_RIGHT, 'y', linewidth=1.5, label='Str. right')
    ax1.set_title('Rotation Power')
    ax1.set_xlim([-35, 35])
    ax1.legend()

    ax2.plot(INTENSITY, STEER_LVL01, 'g', linewidth=1.5, label='Lower')
    ax2.plot(INTENSITY, STEER_LVL02, 'b', linewidth=1.5, label='Low')
    ax2.plot(INTENSITY, STEER_LVL03, 'r', linewidth=1.5, label='Medium')
    ax2.plot(INTENSITY, STEER_LVL05, 'k', linewidth=1.5, label='High')
    ax2.plot(INTENSITY, STEER_LVL06, 'y', linewidth=1.5, label='Higher')
    ax2.set_title('Turn Power')
    ax2.legend()

    for axis in (ax0, ax1, ax2):
        axis.spines['top'].set_visible(False)
        axis.spines['right'].set_visible(False)
        axis.get_xaxis().tick_bottom()
        axis.get_yaxis().tick_left()

    plt.tight_layout()
    plt.show()


def drive_truck():
    """
    Connects to a server that provides a truck to be driven; sends a message
    to the server asking for data, and then processes it according to the
    membership functions. Finally, a reply is sent containing a number in
    the range [-1, 1] that turns the truck around.
    """
    sckt = socket(AF_INET, SOCK_STREAM)
    sckt.connect(('127.0.0.1', 4321))
    server = sckt.makefile()

    while True:
        sckt.send("r\r\n".encode())
        msg = server.readline().split()

        if msg:
            x_coord, _, angle = tuple(map(float, msg))
        else:
            break

        rot = normalize_angle(angle)

        x_lvl_lo = interp_membership(X_DIST, X_LO, x_coord)
        x_lvl_md = interp_membership(X_DIST, X_MD, x_coord)
        x_lvl_hi = interp_membership(X_DIST, X_HI, x_coord)

        drive_to = {
            'strg_right': interp_membership(ANGLE_RANGE, A_STRG_RIGHT, rot),
            'weak_right': interp_membership(ANGLE_RANGE, A_WEAK_RIGHT, rot),
            'straight': interp_membership(ANGLE_RANGE, A_STRAIGHT, rot),
            'weak_left': interp_membership(ANGLE_RANGE, A_WEAK_LEFT, rot),
            'strg_left': interp_membership(ANGLE_RANGE, A_STRG_LEFT, rot),
        }

        rules = [
            [
                [x_lvl_lo, drive_to['strg_left'], STEER_LVL06],
                [x_lvl_lo, drive_to['weak_left'], STEER_LVL06],
                [x_lvl_lo, drive_to['straight'], STEER_LVL06],
                [x_lvl_lo, drive_to['strg_right'], STEER_LVL06],
                [x_lvl_md, drive_to['strg_left'], STEER_LVL06],
            ],
            [
                [x_lvl_lo, drive_to['weak_right'], STEER_LVL05],
                [x_lvl_md, drive_to['weak_left'], STEER_LVL05],
            ],
            [
                [x_lvl_lo, drive_to['strg_right'], STEER_LVL04],
                [x_lvl_md, drive_to['straight'], STEER_LVL04],
                [x_lvl_hi, drive_to['strg_left'], STEER_LVL04],
            ],
            [
                [x_lvl_md, drive_to['weak_right'], STEER_LVL02],
                [x_lvl_hi, drive_to['weak_left'], STEER_LVL02],
            ],
            [
                [x_lvl_md, drive_to['strg_right'], STEER_LVL01],
                [x_lvl_hi, drive_to['straight'], STEER_LVL01],
                [x_lvl_hi, drive_to['weak_right'], STEER_LVL01],
                [x_lvl_hi, drive_to['strg_left'], STEER_LVL01],
                [x_lvl_hi, drive_to['strg_right'], STEER_LVL01],
            ],
        ]

        aggregated = [fmax.reduce(list(map(_min, i))) for i in rules]
        steer_value = defuzz(INTENSITY, fmax.reduce(aggregated), 'centroid')
        sckt.send((str(steer_value) + '\r\n').encode())

    sckt.close()


if __name__ == '__main__':
    # limitations from the server
    X_DIST = arange(0, 1.1, 0.1)
    Y_DIST = arange(0, 1.1, 0.1)
    ANGLE_RANGE = arange(-361, 361, 1)

    # the step value for this range can be customized
    INTENSITY = arange(-1, 1, 0.25)

    # position along the X axis
    X_LO = trimf(X_DIST, [0.0, 0.0, 0.5])
    X_MD = trimf(X_DIST, [0.2, 0.5, 0.8])
    X_HI = trimf(X_DIST, [0.5, 1.0, 1.0])

    # angle of truck
    A_STRG_RIGHT = trimf(ANGLE_RANGE, [10, 360, 360])
    A_WEAK_RIGHT = trimf(ANGLE_RANGE, [0, 15, 30])
    A_STRAIGHT = trimf(ANGLE_RANGE, [-5, 0, 5])
    A_WEAK_LEFT = trimf(ANGLE_RANGE, [-30, -15, 0])
    A_STRG_LEFT = trimf(ANGLE_RANGE, [-360, -360, -10])

    # level of steering (lower level means steering to the left)
    STEER_LVL01 = trimf(INTENSITY, [-1.0, -1.0, -0.5])
    STEER_LVL02 = trimf(INTENSITY, [-0.8, -0.3, 0.0])
    STEER_LVL04 = trimf(INTENSITY, [-0.1, 0.0, 0.1])
    STEER_LVL03 = trimf(INTENSITY, [-0.2, 0.0, 0.2])
    STEER_LVL05 = trimf(INTENSITY, [0.0, 0.3, 0.8])
    STEER_LVL06 = trimf(INTENSITY, [0.5, 1.0, 1.0])

    drive_truck()

    if len(argv) > 1 and argv[1] == "--plot":
        plot_fuzzy_sets()
