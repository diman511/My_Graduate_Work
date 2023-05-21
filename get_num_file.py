
f = open('data/agaricus-lepiota.data.txt', 'r')
f1 = open('data/agaricus-lepiota-num.data.txt', 'w')
mushroomsStart = [item.replace('\n', '').split(',') for item in f.readlines()]

rules = {'p': 0.2, 'x': 0.4, 's': 0.6, 'n': 0.8, 't': 1, 'f': 1.2, 'c': 1.4, 'k': 1.6, 'e': 1.8,
         'w': 2, 'o': 2.2, 'u': 2.4, 'y': 2.6, 'a': 2.8, 'b': 3, 'g': 3.2, 'l': 3.4, 'm': 3.6, 'v': 3.8, 'd': 4,
         'r': 4.2, 'h': 4.4, '?': 0}

rules1 = [{'b': 1, 'c': 2, 'x': 3, 'f': 4, 'k': 5, 's': 6},
        {'f': 1, 'g': 2, 'y': 3, 's': 4},
        {'n': 1, 'b': 2, 'c': 3, 'g': 4, 'r': 5, 'p': 6, 'u': 7, 'e': 8, 'w': 9, 'y': 10},
        {'t': 1, 'f': 2},
        {'a': 1, 'l': 2, 'c': 3, 'y': 4, 'f': 5, 'm': 6, 'n': 7, 'p': 8, 's': 9},
        {'a': 1, 'd': 2, 'f': 3, 'n': 4},
        {'c': 1, 'w': 2, 'd': 3},
        {'b': 1, 'n': 2},
        {'k': 1, 'n': 2, 'b': 3, 'h': 4, 'g': 5, 'r': 6, 'o': 7, 'p': 8, 'u': 9, 'e': 10, 'w': 11, 'y': 12},
        {'e': 1, 't': 2},
        {'b': 1, 'c': 2, 'u': 3, 'e': 4, 'z': 5, 'r': 6, '?': 0},
        {'f': 1, 'y': 2, 'k': 3, 's': 4},
        {'f': 1, 'y': 2, 'k': 3, 's': 4},
        {'n': 1, 'b': 2, 'c': 3, 'g': 4, 'o': 5, 'p': 6, 'e': 7, 'w': 8, 'y': 9},
        {'n': 1, 'b': 2, 'c': 3, 'g': 4, 'o': 5, 'p': 6, 'e': 7, 'w': 8, 'y': 9},
        {'p': 1, 'u': 2},
        {'n': 1, 'o': 2, 'w': 3, 'y': 4},
        {'n': 1, 'o': 2, 't': 3},
        {'c': 1, 'e': 2, 'f': 3, 'l': 4, 'n': 5, 'p': 6, 's': 7, 'z': 8},
        {'k': 1, 'n': 2, 'b': 3, 'h': 4, 'r': 5, 'o': 6, 'u': 7, 'w': 8, 'y': 9},
        {'a': 1, 'c': 2, 'n': 3, 's': 4, 'v': 5, 'y': 6},
        {'g': 1, 'l': 2, 'm': 3, 'p': 4, 'u': 5, 'w': 6, 'd': 7}]

new_array = []

for k in range(8124):
    new_array.append([0] * 23)


for i in range(len(mushroomsStart)):
    if mushroomsStart[i][0] == 'e':
        new_array[i][0] = 1
    else:
        new_array[i][0] = 0

    for j in range(len(mushroomsStart[i])):
        if j != 0:
            new_array[i][j] = rules1[j-1][mushroomsStart[i][j]]

for i in range(8124):
    for j in range(23):
        f1.write(str(new_array[i][j]))
        if j != 22:
            f1.write(',')
    f1.write('\n')

print(new_array)
