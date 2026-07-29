import QtQuick
import QtQuick.Controls

Page {
    id: root

    focus: true
    activeFocusOnTab: true
    Keys.priority: Keys.BeforeItem

    property bool simulatedSingleButtonDown: false
    property bool simulatedLeftButtonDown: false
    property bool simulatedRightButtonDown: false

    property bool showMorseCode: true
    property string inputType: "1"
    property string leftButtonType: "Zeitgesteuert"
    property string rightButtonType: "Zeitgesteuert"

    function displaySymbol(symbol) {
        return symbol === "." ? "•" : "—"
    }

    function displayCode(code) {
        if (!code) {
            return ""
        }

        return code
            .split(".").join("•")
            .split("_").join("—")
    }

    function startNewSentence() {
        SentenceTrainer.startRandomSentence()
    }

    StackView.onStatusChanged: {
        if (StackView.status === StackView.Active) {
            Qt.callLater(function() {
                root.forceActiveFocus()
            })
        }
    }

    Component.onCompleted: {
        SentenceTrainer.configureInput(
            inputType,
            leftButtonType,
            rightButtonType
        )
        startNewSentence()

        Qt.callLater(function() {
            root.forceActiveFocus()
        })
    }

    Component.onDestruction: {
        SentenceTrainer.stop()
    }

    onVisibleChanged: {
        if (visible) {
            Qt.callLater(function() {
                root.forceActiveFocus()
            })
        }
    }

    Keys.onPressed: function(event) {
        if (!DevelopmentMode.enabled) {
            return
        }

        if (event.isAutoRepeat) {
            event.accepted = true
            return
        }

        if (event.key === Qt.Key_Space) {
            event.accepted = true
            if (!root.simulatedSingleButtonDown) {
                root.simulatedSingleButtonDown = true
                SentenceTrainer.buttonPressed("single")
            }
            return
        }

        if (event.key === Qt.Key_Left) {
            event.accepted = true
            if (!root.simulatedLeftButtonDown) {
                root.simulatedLeftButtonDown = true
                SentenceTrainer.buttonPressed("left")
            }
            return
        }

        if (event.key === Qt.Key_Right) {
            event.accepted = true
            if (!root.simulatedRightButtonDown) {
                root.simulatedRightButtonDown = true
                SentenceTrainer.buttonPressed("right")
            }
        }
    }

    Keys.onReleased: function(event) {
        if (!DevelopmentMode.enabled) {
            return
        }

        if (event.isAutoRepeat) {
            event.accepted = true
            return
        }

        if (event.key === Qt.Key_Space) {
            event.accepted = true
            if (root.simulatedSingleButtonDown) {
                root.simulatedSingleButtonDown = false
                SentenceTrainer.buttonReleased("single")
            }
            return
        }

        if (event.key === Qt.Key_Left) {
            event.accepted = true
            if (root.simulatedLeftButtonDown) {
                root.simulatedLeftButtonDown = false
                SentenceTrainer.buttonReleased("left")
            }
            return
        }

        if (event.key === Qt.Key_Right) {
            event.accepted = true
            if (root.simulatedRightButtonDown) {
                root.simulatedRightButtonDown = false
                SentenceTrainer.buttonReleased("right")
            }
        }
    }

    background: Rectangle {
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#FBFBFD" }
            GradientStop { position: 1.0; color: "#EEF1F5" }
        }
    }

    Rectangle {
        x: 28
        y: 24
        width: 54
        height: 54
        radius: 27
        color: backMouse.pressed
               ? "#D7D7DC"
               : backMouse.containsMouse
                 ? "#E7E7EB"
                 : "#FFFFFF"
        border.color: "#E3E3E8"

        Text {
            anchors.centerIn: parent
            text: "‹"
            color: "#1D1D1F"
            font.pixelSize: 42
            y: -2
        }

        MouseArea {
            id: backMouse
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor

            onClicked: {
                SentenceTrainer.stop()
                stackView.pop()
            }
        }
    }

    Rectangle {
        anchors.top: parent.top
        anchors.right: parent.right
        anchors.topMargin: 22
        anchors.rightMargin: 22
        visible: DevelopmentMode.enabled
        width: developmentText.width + 32
        height: 34
        radius: 17
        color: "#FFF4CE"
        border.color: "#E6C65C"

        Text {
            id: developmentText
            anchors.centerIn: parent
            text: qsTr("Development mode · Keyboard active")
            color: "#5C4A00"
            font.pixelSize: 13
        }
    }

    Column {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.top
        anchors.topMargin: 30
        width: Math.min(820, root.width - 90)
        spacing: 12

        // Complete sentence at the very top.
        Flow {
            anchors.horizontalCenter: parent.horizontalCenter
            width: Math.min(780, parent.width)
            spacing: 12

            Repeater {
                model: SentenceTrainer.words

                delegate: Text {
                    required property int index
                    required property string modelData

                    text: modelData.toUpperCase()
                    color: index < SentenceTrainer.completedWords
                           ? "#34C759"
                           : index === SentenceTrainer.wordIndex
                             ? "#007AFF"
                             : "#8E8E93"
                    font.pixelSize: 26
                    font.weight: Font.DemiBold
                    font.letterSpacing: 2
                }
            }
        }

        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: SentenceTrainer.currentWord.toUpperCase()
            color: "#1D1D1F"
            font.pixelSize: 48
            font.weight: Font.DemiBold
            font.letterSpacing: 5
        }

        Row {
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: 7

            Repeater {
                model: SentenceTrainer.currentWord.length

                delegate: Rectangle {
                    required property int index
                    width: 34
                    height: 5
                    radius: 2.5
                    color: index < SentenceTrainer.completedLetters
                           ? "#34C759"
                           : index === SentenceTrainer.letterIndex
                             ? "#007AFF"
                             : "#D1D1D6"
                }
            }
        }

        Rectangle {
            anchors.horizontalCenter: parent.horizontalCenter
            width: Math.min(620, parent.width)
            height: Math.min(450, root.height - 260)
            radius: 38
            color: "#FFFFFF"
            border.color: "#E4E4E9"

            Column {
                anchors.centerIn: parent
                spacing: 22

                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: SentenceTrainer.currentLetter.toUpperCase()
                          + SentenceTrainer.currentLetter.toLowerCase()
                    color: "#1D1D1F"
                    font.pixelSize: 112
                    font.weight: Font.DemiBold
                }

                Row {
                    anchors.horizontalCenter: parent.horizontalCenter
                    spacing: 14
                    visible: root.showMorseCode

                    Repeater {
                        model: SentenceTrainer.morse.length

                        delegate: Text {
                            required property int index

                            property string expectedSymbol:
                                SentenceTrainer.morse.charAt(index)

                            property bool correctSymbol:
                                index < SentenceTrainer.currentInput.length
                                && SentenceTrainer.currentInput.charAt(index)
                                   === expectedSymbol

                            text: root.displaySymbol(expectedSymbol)
                            color: correctSymbol ? "#34C759" : "#1D1D1F"
                            font.pixelSize: 58
                            font.weight: Font.DemiBold
                        }
                    }
                }

                Text {
                    anchors.horizontalCenter: parent.horizontalCenter

                    text: SentenceTrainer.waitingForWordGap
                          ? (
                              inputType === "2"
                              && (
                                  leftButtonType === "Pause"
                                  || rightButtonType === "Pause"
                              )
                              ? qsTr("Lange Pause-Taste drücken")
                              : qsTr("Wortpause …")
                            )
                          : SentenceTrainer.waitingForLetterGap
                            ? (
                                inputType === "2"
                                && (
                                    leftButtonType === "Pause"
                                    || rightButtonType === "Pause"
                                )
                                ? qsTr("Kurze Pause-Taste drücken")
                                : qsTr("Buchstabenpause …")
                              )
                            : SentenceTrainer.currentInput.length > 0
                              ? qsTr("Eingabe: %1").arg(
                                    root.displayCode(
                                        SentenceTrainer.currentInput
                                    )
                                )
                              : qsTr("Warte auf Eingabe …")

                    color: (
                               SentenceTrainer.waitingForLetterGap
                               || SentenceTrainer.waitingForWordGap
                           )
                           ? "#007AFF"
                           : "#8E8E93"
                    font.pixelSize: 18
                    font.letterSpacing: 2
                }
            }
        }

        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            visible: DevelopmentMode.enabled
            text: inputType === "2"
                  ? qsTr("Tastatur: ← linker Knopf · → rechter Knopf")
                  : qsTr("Tastatur: Leertaste simuliert den Knopf")
            color: "#8E8E93"
            font.pixelSize: 13
        }
    }

    TrainingResultDialog {
        id: resultDialog
        trainer: SentenceTrainer

        onContinueRequested: {
            SentenceTrainer.startRandomSentence()
            Qt.callLater(function() {
                root.forceActiveFocus()
            })
        }
    }

    Connections {
        target: SentenceTrainer

        function onSentenceCorrect(elapsedSeconds) {
            resultDialog.showCorrect(
                SentenceTrainer.sentence.toUpperCase(),
                qsTr("Satz vollständig eingegeben"),
                elapsedSeconds
            )
        }

        function onMistake() {
            resultDialog.showMistake(
                SentenceTrainer.sentence.toUpperCase(),
                qsTr("Wort: %1 · Buchstabe: %2")
                    .arg(SentenceTrainer.currentWord.toUpperCase())
                    .arg(SentenceTrainer.currentLetter.toUpperCase())
            )
        }
    }
}
