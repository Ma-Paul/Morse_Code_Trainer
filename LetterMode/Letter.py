from dispatcher import EventDispatcher
from mainandersrum import translateintoascii
import time
dispatcher_press = EventDispatcher()
dispatcher_not_press = EventDispatcher()
stringdata = ""
button = Button(17, bounce_time=0.01)
lastchangetime = time()
def listener_p(data):
    nonlocal stringdata
    if 0.06 < data < 0.08:
        string += "."
    elif 0.2 < data < 0.22:
        stringdata += "_"

def listener_n(data)
    nonlocal stringdata
    if 0.2 < data < 0.22:
        stringdata += "" #there would be a space but not important for letter
    elif 0.48 < data < 0.5:
        stringdata += "" #there would be three spaces but not important for letter
        print(translateintoascii(stringdata)

dispatcher_press.add_listener(listener_p)
dispatcher_not_press.add_listener(listener_n)
def button_pressed():
    now = time()
    global lastchangetime
    not_pressed_time = lastchangetime - now
    last_change_time = now
    dispatcher_not_press.trigger_event(not_pressed_time)
    

def button_released():
    now = time()
    global lastchangetime
    pressed_time = lastchangetime - now
    lastchangetime = now
    dispatcher_press.trigger_event(pressed_time)

button.when_pressed = button_pressed
button.when_released = button.released

