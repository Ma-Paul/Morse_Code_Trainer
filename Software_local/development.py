from PySide6.QtCore import QObject, Property, Signal, Slot


class DevelopmentMode(QObject):
    enabledChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._enabled = False

        # Space for future development options
        self._keyboard_simulation_enabled = True
        self._show_debug_information = False
        self._show_input_events = False

    @Property(bool, notify=enabledChanged)
    def enabled(self):
        return self._enabled

    @Slot()
    def toggle(self):
        self.setEnabled(not self._enabled)

    @Slot(bool)
    def setEnabled(self, enabled):
        enabled = bool(enabled)

        if self._enabled == enabled:
            return

        self._enabled = enabled
        self.enabledChanged.emit()

        if self._enabled:
            print("Development mode enabled")
        else:
            print("Development mode disabled")

    @Property(bool, constant=True)
    def keyboardSimulationEnabled(self):
        return self._keyboard_simulation_enabled
