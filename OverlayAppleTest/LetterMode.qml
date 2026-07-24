import QtQuick
import QtQuick.Controls

Page {
    id: root
    property bool showMorseCode: true
    property string activeLetter: "l"
    property real resultTime: 0
    property bool failed: false

    function newLetter() {
        const alphabet = "abcdefghijklmnopqrstuvwxyz"
        activeLetter = alphabet[Math.floor(Math.random() * alphabet.length)]
        failed = false
        LetterTrainer.startLetter(activeLetter)
    }

    Component.onCompleted: newLetter()
    Component.onDestruction: LetterTrainer.stop()

    background: Rectangle {
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#FBFBFD" }
            GradientStop { position: 1.0; color: "#EEF1F5" }
        }
    }

    Keys.onPressed: event => {
        if (event.key === Qt.Key_Period) {
            LetterTrainer.submitSymbol(".")
            event.accepted = true
        } else if (event.key === Qt.Key_Minus) {
            LetterTrainer.submitSymbol("_")
            event.accepted = true
        } else if (event.key === Qt.Key_Return || event.key === Qt.Key_Space) {
            LetterTrainer.finishLetter()
            event.accepted = true
        }
    }
    focus: true

    Rectangle {
        x: 28; y: 24; width: 54; height: 54; radius: 27
        color: backMouse.pressed ? "#D7D7DC" : (backMouse.containsMouse ? "#E7E7EB" : "#FFFFFF")
        border.color: "#E3E3E8"
        Text { anchors.centerIn: parent; text: "‹"; color: "#1D1D1F"; font.pixelSize: 42; y: -2 }
        MouseArea {
            id: backMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor
            onClicked: { LetterTrainer.stop(); stackView.pop() }
        }
    }

    Column {
        anchors.centerIn: parent
        spacing: 18

        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: qsTr("Buchstabenmodus")
            color: "#6E6E73"; font.family: "SF Pro Text"; font.pixelSize: 20
        }

        Rectangle {
            anchors.horizontalCenter: parent.horizontalCenter
            width: Math.min(560, root.width * 0.52)
            height: Math.min(430, root.height * 0.55)
            radius: 38
            color: "#FFFFFF"
            border.color: failed ? "#FFB4AE" : "#E4E4E9"
            border.width: failed ? 2 : 1

            Column {
                anchors.centerIn: parent
                spacing: 26

                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: activeLetter.toUpperCase() + activeLetter.toLowerCase()
                    color: "#1D1D1F"; font.family: "SF Pro Display"; font.pixelSize: 150; font.weight: Font.DemiBold
                }

                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    visible: root.showMorseCode
                    text: LetterTrainer.morse.replaceAll("_", "—").replaceAll(".", "•")
                    color: "#007AFF"; font.family: "SF Pro Display"; font.pixelSize: 46; font.letterSpacing: 8
                }

                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: LetterTrainer.currentInput.length > 0
                          ? LetterTrainer.currentInput.replaceAll("_", "—").replaceAll(".", "•")
                          : qsTr("Warte auf Eingabe …")
                    color: LetterTrainer.currentInput.length > 0 ? "#6E6E73" : "#AEAEB2"
                    font.family: "SF Pro Text"; font.pixelSize: 18; font.letterSpacing: 4
                }
            }
        }

        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: qsTr("Ein Fehler beendet den Versuch sofort.")
            color: "#8E8E93"; font.family: "SF Pro Text"; font.pixelSize: 15
        }
    }

    Dialog {
        id: resultDialog
        anchors.centerIn: parent
        modal: true
        closePolicy: Popup.NoAutoClose
        width: 370
        padding: 0

        background: Rectangle { radius: 28; color: "#FFFFFF"; border.color: "#E4E4E9" }

        contentItem: Column {
            padding: 30; spacing: 16
            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: "✓"; color: "#34C759"; font.pixelSize: 54; font.weight: Font.DemiBold
            }
            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: qsTr("Richtig")
                color: "#1D1D1F"; font.family: "SF Pro Display"; font.pixelSize: 30; font.weight: Font.DemiBold
            }
            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: qsTr("Zeit: %1 s").arg(root.resultTime.toFixed(2))
                color: "#6E6E73"; font.family: "SF Pro Text"; font.pixelSize: 18
            }
            Button {
                anchors.horizontalCenter: parent.horizontalCenter
                text: qsTr("Nächster Buchstabe")
                onClicked: { resultDialog.close(); root.newLetter() }
            }
        }
    }

    Connections {
        target: LetterTrainer
        function onCorrect(elapsedSeconds) {
            root.resultTime = elapsedSeconds
            resultDialog.open()
        }
        function onMistake(entered, expected) {
            root.failed = true
        }
    }
}
