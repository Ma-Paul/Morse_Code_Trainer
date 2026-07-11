class EventDispatcher:
    def __init__(self):
        self._listeners = []

    def add_listener(self, listener):
        self._listeners.append(listener)

    def remove_listener(self, listener):
        if listener in self._listeners:
            self._listeners.remove(listener)

    def trigger_event(self, event_data=None):
        for listener in self._listeners:
            listener(event_data)



def my_listener(data):
    print(data)

dispatcher = EventDispatcher()
dispatcher2 = EventDispatcher()
dispatcher2.add_listener(my_listener)
dispatcher.add_listener(my_listener)
dispatcher.trigger_event(input())
