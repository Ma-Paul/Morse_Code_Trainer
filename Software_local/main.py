import json
import signal
import sys
from pathlib import Path

from development import DevelopmentMode

from PySide6.QtCore import QObject, QStandardPaths, QTimer, Slot

try:
    from gpiozero import Button
except ImportError:
    Button = None
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from Letter import LetterTrainer
from Word import WordTrainer
from Sentence import SentenceTrainer
from Online import OnlineBridge, OnlineGame


class PhysicalInputRouter:
    """Own the GPIO buttons once and forward them to the active trainer.

    Previously LetterTrainer, WordTrainer and SentenceTrainer all tried to
    reserve GPIO 17/27. The first trainer won, so real hardware only worked
    in Letter mode.
    """

    def __init__(self, letter, word, sentence, online_game, single_pin=17, right_pin=27):
        self.letter = letter
        self.word = word
        self.sentence = sentence
        self.online_game = online_game
        self.single_button = None
        self.right_button = None

        if Button is None:
            print("GPIO unavailable: keyboard development mode can still be used.")
            return

        try:
            self.single_button = Button(single_pin, bounce_time=0.01)
            self.right_button = Button(right_pin, bounce_time=0.01)
            self.single_button.when_pressed = lambda: self._dispatch(True, "primary")
            self.single_button.when_released = lambda: self._dispatch(False, "primary")
            self.right_button.when_pressed = lambda: self._dispatch(True, "right")
            self.right_button.when_released = lambda: self._dispatch(False, "right")
            print("Shared GPIO input active on pins", single_pin, "and", right_pin)
        except Exception as error:
            print(f"GPIO input unavailable: {error}")

    def _active_target(self):
        if self.online_game.running:
            return self.online_game
        if self.sentence.running:
            return self.sentence
        if self.word.running:
            return self.word
        if self.letter.running:
            return self.letter
        return None

    def _input_type(self, target):
        if target is self.online_game:
            trainer = self.online_game.trainer()
            return getattr(trainer, "_input_type", "1")
        return getattr(target, "_input_type", "1")

    def _dispatch(self, pressed, physical_button):
        target = self._active_target()
        if target is None:
            return

        if physical_button == "primary":
            button_name = "left" if self._input_type(target) == "2" else "single"
        else:
            # The second physical button is only meaningful for two-button input.
            if self._input_type(target) != "2":
                return
            button_name = "right"

        if pressed:
            target.buttonPressed(button_name)
        else:
            target.buttonReleased(button_name)


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
    letter_trainer = LetterTrainer(setup_gpio=False)
    word_trainer = WordTrainer(setup_gpio=False)
    sentence_trainer = SentenceTrainer(setup_gpio=False)
    online_bridge = OnlineBridge("http://127.0.0.1:8000")
    online_game = OnlineGame(online_bridge, letter_trainer, word_trainer, sentence_trainer)
    physical_input = PhysicalInputRouter(
        letter_trainer,
        word_trainer,
        sentence_trainer,
        online_game,
    )
    engine.rootContext().setContextProperty(
        "AppBridge",
        bridge,
    )
    engine.rootContext().setContextProperty(
        "LetterTrainer",
        letter_trainer,
    )
    engine.rootContext().setContextProperty(
        "WordTrainer",
        word_trainer,
    )
    engine.rootContext().setContextProperty(
        "SentenceTrainer",
        sentence_trainer,
    )
    engine.rootContext().setContextProperty(
        "OnlineBridge",
        online_bridge,
    )
    engine.rootContext().setContextProperty(
        "OnlineGame",
        online_game,
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
