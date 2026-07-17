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



