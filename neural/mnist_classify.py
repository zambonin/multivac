#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""mnist_classify.py

A neural network that classifies a portion of the MNIST database, that
contains handwritten digits, through the backpropagation with gradient
descent method.

    * `pybrain.datasets.SupervisedDataSet` has two fields, one for the
        input and one for the target;
    * `pybrain.structure.modules.SoftmaxLayer` is the softmax activation
        function [1];
    * `pybrain.structure.modules.TanhLayer` is the hyperbolic tangent
        activation function, a small variant of the sigmoid function;
    * `pybrain.supervised.trainers.BackpropTrainer` is the algorithm
        responsible for training the network, calculating the gradient
        of a cost function, trying to minimize that value by updating
        the network's weights after the optimization method (in this
        case, gradient descent);
    * `pybrain.tools.shortcuts.buildNetwork` is a function that
        builds networks according to a myriad of parameters;
    * `pybrain.utilities.percentError` calculates the error percentage
        between the trained data set and the desired output.

[1] https://en.wikipedia.org/wiki/Softmax_function
"""

from __future__ import absolute_import, division
from csv import reader
from random import randrange
from sys import argv

from numpy import argmax
from matplotlib import pyplot as plt
from pybrain.datasets import SupervisedDataSet
from pybrain.structure.modules import SoftmaxLayer, TanhLayer
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.tools.shortcuts import buildNetwork
from pybrain.utilities import percentError


def pgm_matrix(row):
    """
    Normalizes pixels with values inside the interval [-1, 1] to a
    [0, 255] grey scale through feature scaling.

    Args:
        row:    one image from the original dataset.

    Returns:
        A tuple with a square matrix with the normalized values, and
        the digit that it represents.
    """
    out, side = int(row.pop()), int(len(row) ** 0.5)
    _min, _max = min(row), max(row)
    nmat = list(map(lambda x: (x - _min) * 255 // (_max - _min), row))

    return [nmat[i : i + side] for i in range(0, len(nmat), side)], out


def gen_pgm_file(matrix, number):
    """
    Creates a PGM file with a seemingly random filename, prepended by the
    value which it represents.

    Args:
        m:  matrix with pixel data.
        n:  digit represented by the image.
    """
    name = "{}_{:010x}.pgm".format(number % 10, randrange(16 ** 10))
    with open(name, "w") as _file:
        _file.write("P2\n{} {}\n255\n".format(len(matrix), len(matrix[0])))
        for i in matrix:
            _file.write(" ".join(map(str, i)) + "\n")


def open_csv(path="sample.csv"):
    """
    Reads a CSV file with each image in a column, and its last value is
    a digit showing what it represents.

    Args:
        path:   path for the file.

    Returns:
        Transposed matrix with floating point values inside [-1, 1].
    """
    with open(path, "r") as _file:
        return [list(map(float, i)) for i in zip(*reader(_file))]


def to_dataset(data):
    """
    Creates a dataset for the neural network, transforming single-digit
    output values into vectors, to be interpreted by the network more easily.

    Args:
        data:   a matrix with pixel data.

    Returns:
        Dataset ready to be read by a network.
    """
    sds = SupervisedDataSet(len(data[0]) - 1, 10)
    for i in data:
        sds.addSample(i[:-1], [int(x == i[-1] % 10) for x in range(10)])

    return sds


def hit_rate(trainer, data):
    """
    Calculates the percentage for how many values the network got right.

    Args:
        trainer:    a trainer object, used to create result values.
        data:       original list of outputs.

    Returns:
        Metric that measures quality of the network.
    """
    result = trainer.testOnClassData(dataset=data)
    target = [argmax(i) for i in data["target"]]
    return 100 - percentError(result, target)


def plot_conf_matrix(trainer, data):
    """
    Plots a confusion matrix (easy way of visualizing how many and which
    values the network got right).

    Args:
        trainer:    a trainer object, used to create result values.
        data:       original list of outputs.
    """
    result = trainer.testOnClassData(dataset=data)
    target = [argmax(i) for i in data["target"]]

    side = max(target) - min(target) + 1
    mat = [[0 for _ in range(side)] for _ in range(side)]
    for xtr, yrs in zip(target, result):
        mat[xtr][yrs] += 1

    fig = plt.figure()
    axis = fig.add_subplot(111)

    res = axis.imshow(
        [[j / sum(i) for j in i] for i in mat],
        cmap=plt.cm.coolwarm,
        interpolation="nearest",
    )
    fig.colorbar(res)

    width, height = list(range(len(mat))), list(range(len(mat[0])))

    for wid in width:
        for hei in height:
            axis.annotate(
                mat[wid][hei],
                xy=(hei, wid),
                horizontalalignment="center",
                verticalalignment="center",
            )

    plt.xticks(width)
    plt.yticks(height)
    plt.savefig("confusion_matrix.png", format="png")


def classify_digits(data, prop=0.2, hln=40, lrate=0.04, epochs=1):
    """
    Creates a neural network with three layers:
        * 400 neurons for the input layer, one for each pixel;
        * some number of neurons for the hidden layer;
        * 10 neurons for the output layer, one for each possible output.

    Splits the dataset accordingly and trains the network.

    Args:
        data:   a matrix with pixel data.
        prop:   proportion percentage for how much of the dataset will be
                separated for test data.
        hln:    number of neurons for the hidden layer.
        lrate:  value for the learning rate.
        epochs: number of epochs.
    """
    dset = to_dataset(data)
    dtest, dtrain = dset.splitWithProportion(prop)
    net = buildNetwork(
        dtrain.indim,
        hln,
        dtrain.outdim,
        hiddenclass=TanhLayer,
        outclass=SoftmaxLayer,
    )
    trainer = BackpropTrainer(net, dataset=dtrain, learningrate=lrate)

    for _ in range(epochs):
        trainer.train()
        print(
            "Epoch: {:3d}   All: {:.2f}%   Train: {:.2f}%   Test: {:.2f}%".format(
                trainer.totalepochs,
                hit_rate(trainer, dset),
                hit_rate(trainer, dtrain),
                hit_rate(trainer, dtest),
            )
        )

    if "--plot" in argv:
        plot_conf_matrix(trainer, dset)


def main():
    """Main function for the program."""
    csv_data = open_csv()
    classify_digits(csv_data)

    if "--pgm" in argv:
        for number in csv_data:
            gen_pgm_file(*pgm_matrix(number))


if __name__ == "__main__":
    main()
