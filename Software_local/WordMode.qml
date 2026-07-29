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

    property real resultTime: 0

    function displaySymbol(symbol) {
        return symbol === "." ? "•" : "—"
    }

    function displayCode(code) {
        return code
            .split(".").join("•")
            .split("_").join("—")
    }

    function startNewWord() {
        WordTrainer.startRandomWord()
    }

    StackView.onStatusChanged: {
	if (StackView.status === StackView.Active) {
	    Qt.callLater(function() {
		root.forceActiveFocus()
		console.log(
		    "WordMode active focus:",
		    root.activeFocus
		)
	    })
	}
    }
    Component.onCompleted: {
        WordTrainer.configureInput(
            inputType,
            leftButtonType,
            rightButtonType
        )

        startNewWord()

        Qt.callLater(function() {
            root.forceActiveFocus()
        })
    }

    Component.onDestruction: {
        WordTrainer.stop()
    }

    onVisibleChanged: {
        if (visible) {
            Qt.callLater(function() {
                root.forceActiveFocus()
            })
        }
    }


    Keys.onPressed: function(event) {
	console.log(
	    "WordMode PRESS:",
	    event.key,
	    "autoRepeat:",
	    event.isAutoRepeat,
	    "focus:",
	    root.activeFocus
	)

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
		WordTrainer.buttonPressed("single")
	    }

	    return
	}

	if (event.key === Qt.Key_Left) {
	    event.accepted = true

	    if (!root.simulatedLeftButtonDown) {
		root.simulatedLeftButtonDown = true
		WordTrainer.buttonPressed("left")
	    }

	    return
	}

	if (event.key === Qt.Key_Right) {
	    event.accepted = true

	    if (!root.simulatedRightButtonDown) {
		root.simulatedRightButtonDown = true
		WordTrainer.buttonPressed("right")
	    }
	}
    }

    Keys.onReleased: function(event) {
	console.log(
	    "WordMode RELEASE:",
	    event.key,
	    "autoRepeat:",
	    event.isAutoRepeat,
	    "focus:",
	    root.activeFocus
	)

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
		WordTrainer.buttonReleased("single")
	    }

	    return
	}

	if (event.key === Qt.Key_Left) {
	    event.accepted = true

	    if (root.simulatedLeftButtonDown) {
		root.simulatedLeftButtonDown = false
		WordTrainer.buttonReleased("left")
	    }

	    return
	}

	if (event.key === Qt.Key_Right) {
	    event.accepted = true

	    if (root.simulatedRightButtonDown) {
		root.simulatedRightButtonDown = false
		WordTrainer.buttonReleased("right")
	    }
	}
    }
    background: Rectangle {
        gradient: Gradient {
            GradientStop {
                position: 0.0
                color: "#FBFBFD"
            }

            GradientStop {
                position: 1.0
                color: "#EEF1F5"
            }
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
                WordTrainer.stop()
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
        anchors.topMargin: 36

        width: Math.min(720, root.width - 80)
        spacing: 18

        Text {
            anchors.horizontalCenter: parent.horizontalCenter

            text: WordTrainer.word.toUpperCase()

            color: "#1D1D1F"
            font.pixelSize: 52
            font.weight: Font.DemiBold
            font.letterSpacing: 5
        }

        Row {
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: 7

            Repeater {
                model: WordTrainer.word.length

                delegate: Rectangle {
                    required property int index

                    width: 34
                    height: 5
                    radius: 2.5

                    color: index < WordTrainer.completedLetters
                           ? "#34C759"
                           : index === WordTrainer.letterIndex
                             ? "#007AFF"
                             : "#D1D1D6"
                }
            }
        }

        Rectangle {
            anchors.horizontalCenter: parent.horizontalCenter

            width: Math.min(620, parent.width)
            height: Math.min(500, root.height - 220)
            radius: 38

            color: "#FFFFFF"
            border.color: "#E4E4E9"

            Column {
                anchors.centerIn: parent
                spacing: 24

                Text {
                    anchors.horizontalCenter: parent.horizontalCenter

                    text: WordTrainer.currentLetter.toUpperCase()
                          + WordTrainer.currentLetter.toLowerCase()

                    color: "#1D1D1F"
                    font.pixelSize: 118
                    font.weight: Font.DemiBold
                }

                Row {
                    anchors.horizontalCenter: parent.horizontalCenter
                    spacing: 14

                    visible: root.showMorseCode

                    Repeater {
                        model: WordTrainer.morse.length

                        delegate: Text {
                            required property int index

                            property string expectedSymbol:
                                WordTrainer.morse.charAt(index)

                            property bool correctSymbol:
                                index < WordTrainer.currentInput.length
                                && WordTrainer.currentInput.charAt(index)
                                   === expectedSymbol

                            text: root.displaySymbol(expectedSymbol)

                            color: correctSymbol
                                   ? "#34C759"
                                   : "#1D1D1F"

                            font.pixelSize: 58
                            font.weight: Font.DemiBold
                        }
                    }
                }

                Text {
                    anchors.horizontalCenter: parent.horizontalCenter

                    text: WordTrainer.waitingForLetterGap
                          ? (
                              inputType === "2"
                              && (
                                  leftButtonType === "Pause"
                                  || rightButtonType === "Pause"
                              )
                              ? qsTr("Pause-Taste drücken")
                              : qsTr("Buchstabenpause …")
                            )
                          : WordTrainer.currentInput.length > 0
                            ? qsTr("Eingabe: %1").arg(
                                  root.displayCode(
                                      WordTrainer.currentInput
                                  )
                              )
                            : qsTr("Warte auf Eingabe …")

                    color: WordTrainer.waitingForLetterGap
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
                  ? qsTr(
                        "Tastatur: ← linker Knopf · "
                        + "→ rechter Knopf"
                    )
                  : qsTr(
                        "Tastatur: Leertaste simuliert den Knopf"
                    )

            color: "#8E8E93"
            font.pixelSize: 13
        }
    }

    TrainingResultDialog {
	id: resultDialog

	trainer: WordTrainer

	onContinueRequested: {
	    WordTrainer.startRandomWord()

	    Qt.callLater(function() {
		root.forceActiveFocus()
	    })
	}
    }
    Connections {
	target: WordTrainer

	function onWordCorrect(elapsedSeconds) {
	    resultDialog.showCorrect(
		WordTrainer.word.toUpperCase(),
		qsTr("Wort vollständig eingegeben"),
		elapsedSeconds
	    )
	}

	function onMistake() {
	    resultDialog.showMistake(
		WordTrainer.word.toUpperCase(),
		qsTr("Buchstabe: %1").arg(
		    WordTrainer.currentLetter.toUpperCase()
		)
	    )
	}
    }
}
