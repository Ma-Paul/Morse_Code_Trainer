import string
import random
import time
from mainandersrum import translateintoascii

status = False
eingang = translateintoascii("._")
print(eingang)
zufall = "".join(random.choices(string.ascii_uppercase, k=1))

print(zufall)

start = time.time()


if status == True:
    print("Richtig!")
else:
    print("Leider Falsch :(")
end = time.time()
print("In " + str(round(end - start, 0)) + " Sekunden")
