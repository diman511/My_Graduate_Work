import gensim
import re
import pandas as pd
import nltk
import pymorphy2
from nltk.corpus import stopwords
from gensim.models import Phrases
import string
from nltk.stem import WordNetLemmatizer

lemmatizer = WordNetLemmatizer()

patterns = "[0-9!#$%&'()*+,./:;<=>?@[\]«»^_`{|}~�""\-]+"
f = open('D:/Учеба/Датасеты/20_newsgroups/alt.atheism/51060', 'r')
# df = pd.read_csv('D:/Учеба/Датасеты/20_newsgroups/alt.atheism/51060', sep='\0', encoding='cp1251')
texts = []
for item in f.readlines():
    for elem in item:
        if elem in patterns:
            test_str = item.replace(elem, "")
    texts.append(test_str.translate(str.maketrans('', '', string.punctuation)))

# print(texts)
texts2 = [[]]
for item in texts:
    texts2.append(item.replace('\n', '').split(' '))

# print(texts2)

stopwords_en = stopwords.words('english')
stopwords_en.extend(['xref', 'cantaloupe', 'srv', 'cs' 'cmu', 'mathew', 'europa', 'path', 'alt', ''])
texts3 = [[]]
for i in range(len(texts2)):
    test = []
    for j in range(len(texts2[i])):
        if texts2[i][j] not in stopwords_en:
            test.append(lemmatizer.lemmatize(texts2[i][j]))
    texts3.append(test)

texts4 = []
for i in range(len(texts3)):
    if i != 0:
        if i != len(texts3)-1:
            if texts3[i] != texts3[i+1]:
                if texts3[i] != texts3[i-1]:
                    texts4.append(texts3[i])

for i in range(len(texts4)):
    print(texts4[i])
#
# morph = pymorphy2.MorphAnalyzer()
#
# print(df)

# def lemmatize(doc):
#     doc = re.sub(patterns, ' ', doc)
#     tokens = []
#     for token in doc.split():
#         if token:
#             token = token.strip()
#             token = morph.normal_forms(token)[0]
#             if token not in stopwords_en:
#                 tokens.append(token)
#     if len(tokens) > 2:
#         return tokens
#     return None
#
#
# data_ready = df['text'].apply(lemmatize)
# for i in range(len(data_ready)):
#     print(data_ready[i])
#
# text_clean= []
# for index, row in df.iterrows():
#         text_clean.append(row['text'].split())
#
# bigram = Phrases(text_clean) # Создаем биграммы на основе корпуса
# trigram = Phrases(bigram[text_clean])# Создаем триграммы на основе корпуса
#
# for idx in range(len(text_clean)):
#     for token in bigram[text_clean[idx]]:
#         if '_' in token:
#             text_clean[idx].append(token) # Токен это биграмма? добавим в документ.
#     for token in trigram[text_clean[idx]]:
#         if '_' in token:
#             text_clean[idx].append(token) # Токен это триграмма? добавим в документ.
#
# id2word = corpora.Dictionary(data_ready)
# corpus = [id2word.doc2bow(text) for text in data_ready]
# # Строим модель
# lda_model = gensim.models.ldamodel.LdaModel(corpus=corpus,
#                                            id2word=id2word,
#                                            num_topics=2,
#                                            random_state=100,
#                                            update_every=1,
#                                            chunksize=10,
#                                            passes=1,
#                                            alpha='symmetric',
#                                            per_word_topics=True)
# pprint(lda_model.print_topics())






