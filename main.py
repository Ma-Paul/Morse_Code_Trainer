start = True
morse = {
    "a": "._",
    "b": "_...",
    "c": "_._.",
    "d": "_..",
    "e": ".",
    "f": ".._.",
    "g": "__.",
    "h": "....",
    "i": "..",
    "j": ".___",
    "k": "_._",
    "l": "._..",
    "m": "__",
    "n": "_.",
    "o": "___",
    "p": ".__.",
    "q": "__._",
    "r": "._.",
    "s": "...",
    "t": "_",
    "u": ".._",
    "v": "..._",
    "w": ".__",
    "x": "_.._",
    "y": "_.__",
    "z": "__..",
}
maxLeerzeichen = 1
eingabe = str.lower(input())
ausgabe = ""
for zeichen in eingabe:
    if zeichen == " ":
        while maxLeerzeichen <= 2:
            ausgabe += " "
            maxLeerzeichen += 1

    elif zeichen in morse:

        maxLeerzeichen = 1
        ausgabe += morse[zeichen]
        ausgabe += " "
print(ausgabe)
