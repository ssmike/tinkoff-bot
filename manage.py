from elasticsearch import Elasticsearch
import os
import sys
import time
import re

ES_HOST = os.getenv('ES_HOST', default='localhost')
es = Elasticsearch([ES_HOST])

good = False
while not good:
    good = False
    time.sleep(1)
    try:
        while not es.ping():
            print("Waiting for elasticsearch to launch...")
            time.sleep(1)
        good = True
    except:
        good = False

command = sys.argv[1]
index = sys.argv[2]
if (command == "delete"):
    os.system("curl -XDELETE http://$ES_HOST:9200/" + index)
elif (command == "create"):
    os.system("curl -XPUT http://$ES_HOST:9200/" + index)
    os.system("""curl -XPOST http://$ES_HOST:9200/""" +
              index + """/""" + index +
              """/_mapping -d'{\"""" + index +
              """\":{"_all":{"analyzer":"russian_morphology"}}}'""")
elif (command == "add"):
    filename = sys.argv[3]
    with open(filename, "r") as f:
        data = f.readlines()

    current_index = 0
    idx = 1
    parsed = []
    stop = "++++"

    while current_index < len(data):
        question = []
        i = 0
        while (current_index + i < len(data) and data[current_index + i][:-1] != stop):
            question.append(data[current_index+i][:-1])
            i += 1

        current_index += i
        i = 0
        while (current_index + i < len(data) and data[current_index + i] != '\n'):
            i += 1
        answer = "".join(data[current_index + 1:current_index + i])

        for n, q in enumerate(question):
            q = " ".join(re.split(r"[\'\"\:\-\.!?\s=\(\)]+", q))
            es.index(index, index, {"question": q.lower(), "answer": answer}, idx+n)

        current_index += i+1
        idx += len(question)
        if idx % 100 == 0:
            print(idx)
