from csv import reader
from random import randrange
from numpy import argmax

from pybrain.datasets import SupervisedDataSet
from pybrain.tools.shortcuts import buildNetwork
from pybrain.structure.modules import SoftmaxLayer, TanhLayer
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.utilities import percentError


def feature_scaling(a, n):
    def scale(x): return (x - min(a)) * n // (max(a) - min(a))
    return list(map(scale, a))


def to_matrix(a, n):
    return [a[i:i+n] for i in range(0, len(a), n)]


def gen_pgm_file(a, n):
    name = "{}_{:010x}.pgm".format(n % 10, randrange(16**10))
    with open(name, 'w') as f:
        f.write("P2\n{} {}\n255\n".format(len(a), len(a[0])))
        for i in a:
            f.write(" ".join(map(str, i)))
            f.write("\n")


def create_image_files(matrix):
    for i in matrix:
        n = int(i.pop())
        side = int(len(i) ** 0.5)
        gen_pgm_file(to_matrix(feature_scaling(i, 255), side), n)


def percent(x, y):
    return sum(i == j for i, j in zip(x, y)) / len(x)


def organize_data(a):
    def pos(x, y): return int(x == y % 10)
    return [[i[:-1], [pos(x, i[-1]) for x in range(10)]] for i in a]


def open_csv(path='sample.csv'):
    with open(path, 'r') as f:
        return [list(map(float, i)) for i in zip(*reader(f))]


data = organize_data(open_csv('sample.csv'))

ds = SupervisedDataSet(len(data[0][0]), 10)
for i in data:
    ds.addSample(i[0], i[1])

test_data, train_data = ds.splitWithProportion(0.2)
net = buildNetwork(train_data.indim, 40, train_data.outdim,
                   hiddenclass=TanhLayer, outclass=SoftmaxLayer)
trainer = BackpropTrainer(net, dataset=train_data, learningrate=0.04)

all_data = [argmax(i) for i in ds['target']]
train_data_orig = [argmax(i) for i in train_data['target']]
test_data_orig = [argmax(i) for i in test_data['target']]

for _ in range(100):
    trainer.train()
    all_data_neural = trainer.testOnClassData(dataset=ds)
    train_data_neural = trainer.testOnClassData(dataset=train_data)
    test_data_neural = trainer.testOnClassData(dataset=test_data)

    print("Epoch: {:3d}   All: {:.2f}%   Train: {:.2f}%   Test: {:.2f}%"
          .format(trainer.totalepochs,
                  percentError(all_data, all_data_neural),
                  percentError(train_data_orig, train_data_neural),
                  percentError(test_data_orig, test_data_neural)))
