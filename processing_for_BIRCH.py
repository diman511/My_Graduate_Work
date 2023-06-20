import pandas as pd
from sklearn.cluster import Birch
from time import time
from memory_profiler import profile

f = open('data/agaricus-lepiota-num.data.txt', 'r')
startData = [item.replace('\n', '').split(',') for item in f.readlines()]
trainingData = []

for k in range(8124):
    trainingData.append([0] * 22)

for rowIndex in range(0, len(startData)):
    for columnIndex in range(0, len(startData[rowIndex])):
        if columnIndex != 0:
            trainingData[rowIndex][columnIndex - 1] = startData[rowIndex][columnIndex]
        else:
            trainingData[rowIndex] = [''] * 22

clusters = 22
t0 = time()


@profile
def training_birch():
    birch = Birch(branching_factor=80, n_clusters=clusters, threshold=3)
    birch.fit(trainingData)
    lb = birch.labels_
    return lb


labels = training_birch()
t1 = time()

countsCluster = {item: 0 for item in range(0, clusters)}
clustersCount = []

for i in range(len(labels)):
    countsCluster[labels[i]] += 1


for item in range(0, clusters):
    clustersCount.append({'e': 0, 'p': 0})

for i in range(len(labels)):
    if startData[i][0] == '1':
        clustersCount[labels[i]]['e'] += 1
    else:
        clustersCount[labels[i]]['p'] += 1

edible = 0
poisonous = 0
for i in range(clusters):
    edible += clustersCount[i]['e']
    poisonous += clustersCount[i]['p']

df = pd.DataFrame(clustersCount)
# print(df)
print('Время работы алгоритма: ', t1 - t0)
# print('Edible: ', edible, 'Poisonous: ', poisonous)
