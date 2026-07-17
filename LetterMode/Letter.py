from dispatcher import EventDispatcher
from gpiozero import Button
from mainandersrum import translateintoascii
import time

dispatcher_press = EventDispatcher()
dispatcher_not_press = EventDispatcher()
stringdata = ""
button = Button(17, bounce_time=0.01)
lastchangetime = time.time()
print("test")


def listener_p(time_pressed):
    global stringdata
    print("listener1")
    if time_pressed <= 0.2:
        stringdata += "."
    elif 0.2 < time_pressed < 0.5:
        stringdata += "_"
    else:
        print(time_pressed)


def listener_n(time_released):
    global stringdata
    print("Listener2")
    if 0.2 < time_released < 0.22:
        stringdata += ""  # there would be a space but not important for letter
    elif 0.48 < time_released < 0.8:
        stringdata += ""  # there would be three spaces but not important for letter
        print(translateintoascii(stringdata))


print("Vor add_listener")
dispatcher_press.add_listener(listener_p)
dispatcher_not_press.add_listener(listener_n)

print("Nach add_listener")


def button_pressed():
    now = time.time()
    global lastchangetime
    not_pressed_time = abs(lastchangetime - now)
    last_change_time = now
    dispatcher_not_press.trigger_event(not_pressed_time)


def button_released():
    now = time.time()
    global lastchangetime
    pressed_time = abs(lastchangetime - now)
    lastchangetime = now
    dispatcher_press.trigger_event(pressed_time)


button.when_pressed = button_pressed
button.when_released = button_released
while True:
    pass
