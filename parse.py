from elasticsearch import Elasticsearch
import os

with open("FAQ.txt", "r") as f:
    data = f.readlines()

current_index = 0
idx = 1
parsed = []
ES_HOST = os.getenv('ES_HOST', default='localhost')
es = Elasticsearch([ES_HOST])
while current_index < len(data):
    question = data[current_index]
    i = 0
    while (current_index + i < len(data) and data[current_index + i] != '\n'):
        i += 1
    answer = "".join(data[current_index + 1:current_index + i])
    print ("ID: " + str(idx))
    print("Q: " + question)
    print("A: " + answer)
    current_index += (i + 1)
    idx += 1
    es.index("faqs", "faq", {"question": question, "answer": answer}, idx)
