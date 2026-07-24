from gpiozero import Button

import time
from time import sleep

# Button connected between GPIO 17 and GND
# 23

button = Button(17, bounce_time=0.05)
button2 = Button(23)
last_change_time = time.perf_counter()

pressed_durations = []

not_pressed_durations = []

def checkforinputgeraet():
    return button2.pressed()
def button_pressed():

    global last_change_time

    now = time.perf_counter()

    # The button was not pressed before this event

    not_pressed_time = now - last_change_time

    not_pressed_durations.append(not_pressed_time)

    print(f"Button was not pressed for {not_pressed_time:.9f} seconds")

    last_change_time = now


def button_released():

    global last_change_time

    now = time.perf_counter()

    # The button was pressed before this event

    pressed_time = now - last_change_time

    pressed_durations.append(pressed_time)

    print(f"Button was pressed for {pressed_time:.2f} seconds")

    last_change_time = now


button.when_pressed = button_pressed

button.when_released = button_released

print("Waiting for button activity...")

while True:

    sleep(0.001)
