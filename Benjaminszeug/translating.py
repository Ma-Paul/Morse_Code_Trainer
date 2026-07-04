from reading import button_tracker
from mainandersrum import translateintoascii
import socket

translatedData = ""
client = socket.socket()
client.connect(("localhost", 5000))
while True:
    data = client.recv(1024).decode()
    if data:
        translatedData += translateintoascii(data.strip())
