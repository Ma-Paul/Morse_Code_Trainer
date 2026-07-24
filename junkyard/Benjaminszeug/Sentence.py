import json
import numpy as np
import time


def Sentencemode(inputascii):
    with open("data_s.json", "r") as f:
        d = json.load(f)

    sentence = np.random.choice(d["sentences"])
    print(sentence)
    start = time.time()
    need = 0
    for i in range(len(sentence)):
        if inputascii == sentence[i]:
            need += 1
        else:
            print("Versuche diesen Buchstaben nochmal")
            i -= 1
        if need == len(sentence):
            print("Richtig!")
            end = time.time()
            finaltime = end - start
