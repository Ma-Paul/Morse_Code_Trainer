import json
import sys
from pathlib import Path

from PySide6.QtCore import QObject, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine


STATE_FILE = Path("state.json")


class AppBridge(QObject):
    @Slot(str, str, str, str)
    def saveGlobals(self, eingabeart, lefttype, righttype, mode):
        data = {
            "eingabeart": eingabeart,
            "lefttype": lefttype,
            "righttype": righttype,
            "mode": mode,
        }

        STATE_FILE.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

        print("Saved:", data)


app = QGuiApplication(sys.argv)

engine = QQmlApplicationEngine()
bridge = AppBridge()

engine.rootContext().setContextProperty("AppBridge", bridge)
engine.load("main.qml")

if not engine.rootObjects():
    sys.exit(-1)

sys.exit(app.exec())