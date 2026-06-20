from gpiozero import Button

from time import time, sleep

# Button connected between GPIO 17 and GND

button = Button(17)

last_change_time = time()

pressed_durations = []

not_pressed_durations = []


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
