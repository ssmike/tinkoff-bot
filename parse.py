from elasticsearch import Elasticsearch
import os

with open("FAQ.txt", "r") as f:
    data = f.readlines()

current_index = 0
idx = 1
parsed = []
stop = "++++"
ES_HOST = os.getenv('ES_HOST', default='localhost')
es = Elasticsearch([ES_HOST])
while current_index < len(data):
    question = []
    i = 0
    while (current_index + i < len(data) and data[current_index + i][:-1] != stop):
        question.append( data[current_index+i][:-1])
        i += 1

    current_index += i
    i = 0
    while (current_index + i < len(data) and data[current_index + i] != '\n'):
        i += 1
    answer = "".join(data[current_index + 1:current_index + i])

    for n,q in enumerate(question):
        es.index("faqs", "faq", {"question": q, "answer": answer}, idx+n)
#        print ("ID: " + str(idx+n))
#        print("Q: " + q)
#        print("A: " + answer)

    current_index += i+1
    idx += len(question)
