from mainandersrum import translateintoascii
import socket

translatedData = ""
client = socket.socket()
client.connect(("localhost", 2345))
while True:
    data = client.recv(1024).decode()
    if data:
        translatedData += translateintoascii(data.strip())
        print(translatedData)
