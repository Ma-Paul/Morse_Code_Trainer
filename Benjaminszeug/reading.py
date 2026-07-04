from gpiozero import Button
import socket
from time import time, sleep

# Dit = 0.06 < time < 0.08
# Dah = 0.20 < time < 0.22
# Button connected between GPIO 17 and GND
server = socket.socket()
server.bind(("localhost", 5000))
server.listen(1)
conn, addr = server.accept()
print(f"Connected by {addr}")


def button_tracker():
    global conn
    zeichen = ""
    button = Button(17)
    last_change_time = time()

    pressed_durations = []
    not_pressed_durations = []
    previouslengthp = 0
    previouslengthn = 0

    def button_pressed():
        global last_change_time
        now = time()
        # The button was not pressed before this event
        not_pressed_time = now - last_change_time
        not_pressed_durations.append(not_pressed_time)
        print(f"Button was not pressed for {not_pressed_time:.2f} seconds")
        last_change_time = now

    def button_released():
        global last_change_time
        now = time()
        # The button was pressed before this event
        pressed_time = now - last_change_time
        pressed_durations.append(pressed_time)
        print(f"Button was pressed for {pressed_time:.2f} seconds")
        last_change_time = now

    button.when_pressed = button_pressed
    button.when_released = button_released
    print("Waiting for button activity...")
    while True:
        sleep(0.1)
        if len(pressed_durations) != previouslengthp:
            if 0.06 < pressed_durations[-1] < 0.08:
                zeichen += "."
            elif 0.20 < pressed_durations[-1] < 0.22:
                zeichen += "_"
            previouslengthp = len(pressed_durations)
        if len(not_pressed_durations) != previouslengthn:
            if 0.06 < not_pressed_durations[-1] < 0.08:
                zeichen += " "
                conn.sendall(zeichen.encode())
                zeichen = ""
            elif 0.20 < not_pressed_durations[-1] < 0.22:
                zeichen += "   "
                conn.sendall(zeichen.encode())
                zeichen = ""
            previouslengthn = len(not_pressed_durations)
