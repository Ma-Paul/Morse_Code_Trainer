import json
import numpy as np
import time


def Wordmode(inputascii):
    with open("data_w.json", "r") as f:
        d = json.load(f)
    #    word = random.choice(d)
    word = np.random.choice(d["words"])
    print(word)
    start = time.time()
    need = 0
    for i in range(len(word)):
        if inputascii == word[i]:
            need += 1
        else:
            print("Versuche diesen Buchstaben nochmal")
            i -= 1
        if need == len(word):
            print("Richtig!")
            end = time.time()
            finaltime = end - start
