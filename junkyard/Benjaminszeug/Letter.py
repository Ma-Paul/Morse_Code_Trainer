import string
import random
import time


def Lettermode(inputascii):
    status = False

    zufall = "".join(random.choices(string.ascii_uppercase, k=1))

    print(zufall)

    start = time.time()

    if inputascii == zufall:
        status = True

    if status == True:
        print("Richtig!")
    else:
        print("Leider Falsch :(")
    end = time.time()
    finaltime = end - start
    print("In " + str(round(end - start, 0)) + " Sekunden")
