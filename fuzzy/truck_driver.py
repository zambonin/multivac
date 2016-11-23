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

import socket
import matplotlib.pyplot as plt

from math import floor
from numpy import arange, fmin, fmax
from skfuzzy import defuzz, interp_membership, trimf
from sys import argv


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
    fig, (ax0, ax1, ax2) = plt.subplots(nrows=3, figsize=(8, 9))

    ax0.plot(x_dist, x_lo, 'b', linewidth=1.5, label='Left')
    ax0.plot(x_dist, x_md, 'g', linewidth=1.5, label='Center')
    ax0.plot(x_dist, x_hi, 'r', linewidth=1.5, label='Right')
    ax0.set_title('X Distance')
    ax0.legend()

    ax1.plot(angle_range, a_strg_left,  'b', linewidth=1.5, label='Str. left')
    ax1.plot(angle_range, a_weak_left,  'g', linewidth=1.5, label='Left')
    ax1.plot(angle_range, a_straight,   'r', linewidth=1.5, label='Straight')
    ax1.plot(angle_range, a_weak_right, 'k', linewidth=1.5, label='Right')
    ax1.plot(angle_range, a_strg_right, 'y', linewidth=1.5, label='Str. right')
    ax1.set_title('Rotation Power')
    ax1.set_xlim([-35, 35])
    ax1.legend()

    ax2.plot(intensity, steer_lvl01, 'g', linewidth=1.5, label='Lower')
    ax2.plot(intensity, steer_lvl02, 'b', linewidth=1.5, label='Low')
    ax2.plot(intensity, steer_lvl03, 'r', linewidth=1.5, label='Medium')
    ax2.plot(intensity, steer_lvl05, 'k', linewidth=1.5, label='High')
    ax2.plot(intensity, steer_lvl06, 'y', linewidth=1.5, label='Higher')
    ax2.set_title('Turn Power')
    ax2.legend()

    for ax in (ax0, ax1, ax2):
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.get_xaxis().tick_bottom()
        ax.get_yaxis().tick_left()

    plt.tight_layout()
    plt.show()


def drive_truck():
    """
    Connects to a server that provides a truck to be driven; sends a message
    to the server asking for data, and then processes it according to the
    membership functions. Finally, a reply is sent containing a number in
    the range [-1, 1] that turns the truck around.
    """
    sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sckt.connect((host, port))
    server = sckt.makefile()

    while True:
        sckt.send("r\r\n".encode())
        msg = server.readline().split()

        if msg:
            x, y, angle = tuple(map(float, msg))
        else:
            break

        rot = normalize_angle(angle)

        x_lvl_lo = interp_membership(x_dist, x_lo, x)
        x_lvl_md = interp_membership(x_dist, x_md, x)
        x_lvl_hi = interp_membership(x_dist, x_hi, x)

        strg_right = interp_membership(angle_range, a_strg_right, rot)
        weak_right = interp_membership(angle_range, a_weak_right, rot)
        straight = interp_membership(angle_range, a_straight, rot)
        weak_left = interp_membership(angle_range, a_weak_left, rot)
        strg_left = interp_membership(angle_range, a_strg_left, rot)

        rules_level_06 = [
            [x_lvl_lo, strg_left,  steer_lvl06],
            [x_lvl_lo, weak_left,  steer_lvl06],
            [x_lvl_lo, straight,   steer_lvl06],
            [x_lvl_lo, strg_right, steer_lvl06],
            [x_lvl_md, strg_left,  steer_lvl06],
        ]

        rules_level_05 = [
            [x_lvl_lo, weak_right, steer_lvl05],
            [x_lvl_md, weak_left,  steer_lvl05],
        ]

        rules_level_04 = [
            [x_lvl_lo, strg_right, steer_lvl04],
            [x_lvl_md, straight,   steer_lvl04],
            [x_lvl_hi, strg_left,  steer_lvl04],
        ]

        rules_level_02 = [
            [x_lvl_md, weak_right, steer_lvl02],
            [x_lvl_hi, weak_left,  steer_lvl02],
        ]

        rules_level_01 = [
            [x_lvl_md, strg_right, steer_lvl01],
            [x_lvl_hi, straight,   steer_lvl01],
            [x_lvl_hi, weak_right, steer_lvl01],
            [x_lvl_hi, strg_left,  steer_lvl01],
            [x_lvl_hi, strg_right, steer_lvl01],
        ]

        aggregated = [
            fmax.reduce(list(map(_min, rules_level_01))),
            fmax.reduce(list(map(_min, rules_level_02))),
            fmax.reduce(list(map(_min, rules_level_04))),
            fmax.reduce(list(map(_min, rules_level_05))),
            fmax.reduce(list(map(_min, rules_level_06))),
        ]

        steer_value = defuzz(intensity, fmax.reduce(aggregated), 'centroid')
        sckt.send((str(steer_value) + '\r\n').encode())

    sckt.close()


if __name__ == '__main__':

    # socket uses this
    host = "127.0.0.1"
    port = 4321

    # limitations from the server
    x_dist = arange(0, 1.1, 0.1)
    y_dist = arange(0, 1.1, 0.1)
    angle_range = arange(-361, 361, 1)

    # the step value for this range can be customized
    intensity = arange(-1, 1, 0.25)

    # position along the X axis
    x_lo = trimf(x_dist, [0.0, 0.0, 0.5])
    x_md = trimf(x_dist, [0.2, 0.5, 0.8])
    x_hi = trimf(x_dist, [0.5, 1.0, 1.0])

    # angle of truck
    a_strg_right = trimf(angle_range, [10, 360, 360])
    a_weak_right = trimf(angle_range, [0, 15, 30])
    a_straight = trimf(angle_range, [-5, 0, 5])
    a_weak_left = trimf(angle_range, [-30, -15, 0])
    a_strg_left = trimf(angle_range, [-360, -360, -10])

    # level of steering (lower level means steering to the left)
    steer_lvl01 = trimf(intensity, [-1.0, -1.0, -0.5])
    steer_lvl02 = trimf(intensity, [-0.8, -0.3, 0.0])
    steer_lvl03 = trimf(intensity, [-0.2, 0.0, 0.2])
    steer_lvl04 = trimf(intensity, [-0.1, 0.0, 0.1])
    steer_lvl05 = trimf(intensity, [0.0, 0.3, 0.8])
    steer_lvl06 = trimf(intensity, [0.5, 1.0, 1.0])

    drive_truck()

    if len(argv) > 1 and argv[1] == "--plot":
        plot_fuzzy_sets()
