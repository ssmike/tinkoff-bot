import numpy as np
from cleantext import clean

__all__ = ["read_vectors", "importance", "trim"]

def read_vectors(vfile):
    word_cnt, vec_len = map(int, vfile[0].split())
    vecdict = {}
    for line in vfile[1:]:
        words = line.split()
        word = words[0]
        vec = np.array(list(map(float, words[1:])))
        vecdict[word] = vec
    return vecdict, vec_len


def importance(line, vecdict, vec_len):
    sm = np.zeros(vec_len)
    words = line.split()
    for word in words:
        if word in vecdict: 
            sm += vecdict[word]
        else:
            vecdict[word] = np.zeros(vec_len)
    sm /= np.sqrt(np.sum(sm**2))
    return list(zip(words, map(lambda x: np.sum(vecdict[x] * sm)/np.sqrt(np.sum(vecdict[x]**2)), words)))


def trim(line, vecdict, vec_len, threshold=0.6):
    line = clean(line)
    words = importance(line, vecdict, vec_len)
    if words == []:
        return ""
    max_val = max(map(lambda x: x[1], words))
    return " ".join(map(lambda x: x[0], filter(lambda x: x[1]/max_val > threshold, words)))
