import CLOPE as cl
import numpy
import pandas as pd
from memory_profiler import profile
from time import time


def get_count_clusters(data, clope):
    # Выводим распределение по кластерам съедобных и несъедобных грибов
    answ = []
    for item in range(0, clope.max_cluster_number):
        answ.append({'e': 0, 'p': 0})
    for itemTransact in clope.transaction:
        cluster = clope.transaction[itemTransact]
        if data[itemTransact][0] == 'e':
            answ[cluster]['e'] += 1
        else:
            answ[cluster]['p'] += 1
    edible = 0
    poisonous = 0
    for i in range(clope.max_cluster_number):
        edible += answ[i]['e']
        poisonous += answ[i]['p']
    return [pd.DataFrame(answ), edible, poisonous]


# Прочитываем данные
f = open('data/agaricus-lepiota.data.txt', 'r')
# Разделяем данные
mushroomsStart = [item.replace('\n', '').split(',') for item in f.readlines()]
seed = 40
numpy.random.seed(seed)
numpy.random.shuffle(mushroomsStart)

mushrooms = {}
miss_count = 0
for rowIndex in range(0, len(mushroomsStart)):
    for columnIndex in range(0, len(mushroomsStart[rowIndex])):
        # Первый столбец -- признак (съедобные (e) или нет(p)). Данный столбец является целым классом. По этому столбцу
        # проверяется качество тестирования
        if columnIndex != 0:
            if mushroomsStart[rowIndex][columnIndex] != '?':
                mushrooms[rowIndex][columnIndex - 1] = mushroomsStart[rowIndex][columnIndex] + str(columnIndex)
            else:
                # print('Пропущен объект. Номер транзакции:', rowIndex, '. Номер объекта:', columnIndex)
                miss_count += 1
        else:
            mushrooms[rowIndex] = [''] * 22

# print('Общее число пропущенных объектов:', miss_count)


# Начальные данные
repulsion = 2.7
noiseLimit = 0
t0 = time()
# Инициализируем алгоритм

@profile
def training_clope():
    clope = cl.CLOPE(print_step=1000, is_save_history=False, random_seed=seed)
    clope.init_clusters(mushrooms, repulsion, noiseLimit)
    df = get_count_clusters(mushroomsStart, clope)
    while clope.next_step(mushrooms, repulsion, noiseLimit) > 0:
        pass
    return(df[0])
# clope.print_history_count(repulsion, seed)


df = training_clope()
# print(df)
# pf = get_count_clusters(mushroomsStart, clope)
# print(pf[0])
t1 = time()
print('Время работы алгоритма: ', t1 - t0)

