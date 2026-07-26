import json
import signal
import sys
from pathlib import Path

from development import DevelopmentMode

from PySide6.QtCore import QObject, QStandardPaths, QTimer, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from Letter import LetterTrainer


class AppBridge(QObject):
    @Slot(str, str, str, str)
    def saveSettings(
        self,
        eingabeart: str,
        lefttype: str,
        righttype: str,
        mode: str,
    ) -> None:
        data = {
            "eingabeart": eingabeart,
            "lefttype": lefttype,
            "righttype": righttype,
            "mode": mode,
        }

        app_data_directory = Path(
            QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.AppDataLocation
            )
        )
        app_data_directory.mkdir(parents=True, exist_ok=True)

        settings_file = app_data_directory / "settings.json"

        try:
            settings_file.write_text(
                json.dumps(
                    data,
                    indent=2,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
        except OSError as error:
            print(
                f"Could not save settings to {settings_file}: {error}",
                file=sys.stderr,
            )


def main() -> int:
    # Restore the normal terminal behaviour for Ctrl+C.
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QGuiApplication(sys.argv)
    app.setOrganizationName("MorseCodeOverlay")
    app.setApplicationName("MorseCodeTrainer")

    # Wake the Python interpreter regularly so SIGINT is processed
    # while Qt owns the main event loop.
    signal_timer = QTimer()
    signal_timer.setInterval(100)
    signal_timer.timeout.connect(lambda: None)
    signal_timer.start()

    development_mode = DevelopmentMode()

    engine = QQmlApplicationEngine()
    bridge = AppBridge()
    letter_trainer = LetterTrainer()

    engine.rootContext().setContextProperty(
        "AppBridge",
        bridge,
    )
    engine.rootContext().setContextProperty(
        "LetterTrainer",
        letter_trainer,
    )
    engine.rootContext().setContextProperty(
        "DevelopmentMode",
        development_mode,
    )

    main_qml = Path(__file__).resolve().parent / "Main.qml"
    engine.load(main_qml.as_uri())

    if not engine.rootObjects():
        print(
            f"Could not load QML file: {main_qml}",
            file=sys.stderr,
        )
        return 1

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
