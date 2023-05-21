import pandas as pd
from sklearn.cluster import Birch

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

clusters = 25
model = Birch(branching_factor=1000, n_clusters=clusters, threshold=0.5)
model.fit(trainingData)
labels = model.labels_

countsCluster = {item: 0 for item in range(0, clusters)}
clustersCount = []

for i in range(len(labels)):
    countsCluster[labels[i]] += 1

# print(countsCluster)

for item in range(0, clusters):
    clustersCount.append({'e': 0, 'p': 0})

for i in range(len(labels)):
    if startData[i][0] == '1':
        clustersCount[labels[i]]['e'] += 1
    else:
        clustersCount[labels[i]]['p'] += 1

print(clustersCount)
# print(startData)