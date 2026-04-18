import time
import re
x = 0
eingang = input()
morseback = {
    "._": "a",
    "_...": "b",
    "_._.": "c",
    "_..": "d",
    ".": "e",
    ".._.": "f",
    "__.": "g",
    "....": "h",
    "..": "i",
    ".___": "j",
    "_._": "k",
    "._..": "l",
    "__": "m",
    "_.": "n",
    "___": "o",
    ".__.": "p",
    "__._": "q",
    "._.": "r",
    "...": "s",
    "_": "t",
    ".._": "u",
    "..._": "v",
    ".__": "w",
    "_.._": "x",
    "_.__": "y",
    "__..": "z",
}
ausgabe = ""
woerter = re.split(r"   ", eingang)
for anzahl in woerter:
    buchstaben = re.split(r" ", anzahl)
    for test in buchstaben:
        ausgabe += morseback[test]
    ausgabe += " "
print(ausgabe)