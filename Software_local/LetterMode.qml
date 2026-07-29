import QtQuick
import QtQuick.Controls

Page {
    id: root

    focus: true

    property bool simulatedSingleButtonDown: false
    property bool simulatedLeftButtonDown: false
    property bool simulatedRightButtonDown: false

    property bool showMorseCode: true

    property string inputType: "1"
    property string leftButtonType: "Zeitgesteuert"
    property string rightButtonType: "Zeitgesteuert"

    property string activeLetter: "l"


    function displaySymbol(symbol) {
        return symbol === "." ? "•" : "—"
    }

    function displayCode(code) {
	if (!code) {
	    return ""
	}
        return code
            .replaceAll("_", "—")
            .replaceAll(".", "•")
    }

    function newLetter() {
        const alphabet = "abcdefghijklmnopqrstuvwxyz"

        activeLetter = alphabet[
            Math.floor(Math.random() * alphabet.length)
        ]

        LetterTrainer.startLetter(activeLetter)
    }
    onVisibleChanged: {
	if (visible) {
	    Qt.callLater(function() {
		root.forceActiveFocus()
	    })
	}
    }
    Component.onCompleted: {
	LetterTrainer.configureInput(
	    inputType,
	    leftButtonType,
	    rightButtonType
	)

	newLetter()

	Qt.callLater(function() {
	    root.forceActiveFocus()
	    console.log(
		"LetterMode keyboard focus:",
		root.activeFocus
	    )
	})
    }
    Component.onDestruction: {
        LetterTrainer.stop()
    }

    /*
        Keyboard simulation is active only in development mode.

        One-button mode:
            Space = single button

        Two-button mode:
            Left arrow  = left button
            Right arrow = right button
    */

    Keys.onPressed: function(event) {
        if (!DevelopmentMode.enabled
                || !DevelopmentMode.keyboardSimulationEnabled) {
            return
        }

        if (event.isAutoRepeat) {
            event.accepted = true
            return
        }

        switch (event.key) {
        case Qt.Key_Space:
            if (!root.simulatedSingleButtonDown) {
                root.simulatedSingleButtonDown = true
                LetterTrainer.buttonPressed("single")
            }

            event.accepted = true
            break

        case Qt.Key_Left:
            if (!root.simulatedLeftButtonDown) {
                root.simulatedLeftButtonDown = true
                LetterTrainer.buttonPressed("left")
            }

            event.accepted = true
            break

        case Qt.Key_Right:
            if (!root.simulatedRightButtonDown) {
                root.simulatedRightButtonDown = true
                LetterTrainer.buttonPressed("right")
            }

            event.accepted = true
            break
        }
    }

    Keys.onReleased: function(event) {
        if (!DevelopmentMode.enabled
                || !DevelopmentMode.keyboardSimulationEnabled) {
            return
        }

        if (event.isAutoRepeat) {
            event.accepted = true
            return
        }

        switch (event.key) {
        case Qt.Key_Space:
            if (root.simulatedSingleButtonDown) {
                root.simulatedSingleButtonDown = false
                LetterTrainer.buttonReleased("single")
            }

            event.accepted = true
            break

        case Qt.Key_Left:
            if (root.simulatedLeftButtonDown) {
                root.simulatedLeftButtonDown = false
                LetterTrainer.buttonReleased("left")
            }

            event.accepted = true
            break

        case Qt.Key_Right:
            if (root.simulatedRightButtonDown) {
                root.simulatedRightButtonDown = false
                LetterTrainer.buttonReleased("right")
            }

            event.accepted = true
            break
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
                LetterTrainer.stop()
                stackView.pop()
            }
        }
    }

    Rectangle {
        id: developmentModeNotice

        anchors.top: parent.top
        anchors.right: parent.right
        anchors.topMargin: 22
        anchors.rightMargin: 22

        visible: DevelopmentMode.enabled

        width: developmentModeText.width + 32
        height: 34
        radius: 17

        color: "#FFF4CE"
        border.color: "#E6C65C"
        border.width: 1

        Row {
            anchors.centerIn: parent
            spacing: 8

            Rectangle {
                width: 8
                height: 8
                radius: 4
                color: "#E5A900"
            }

            Text {
                id: developmentModeText

                text: qsTr("Development mode · Keyboard active")
                color: "#5C4A00"
                font.pixelSize: 13
                font.weight: Font.Medium
            }
        }
    }

    Column {
        anchors.centerIn: parent
        spacing: 18

        Text {
            anchors.horizontalCenter: parent.horizontalCenter

            text: qsTr("Buchstabenmodus")
            color: "#6E6E73"
            font.pixelSize: 20
        }

        Rectangle {
            anchors.horizontalCenter: parent.horizontalCenter

            width: Math.min(620, root.width * 0.58)
            height: Math.min(470, root.height * 0.60)
            radius: 38

            color: "#FFFFFF"
            border.color: "#E4E4E9"
            border.width: 1

            Column {
                anchors.centerIn: parent
                spacing: 30

                Text {
                    anchors.horizontalCenter: parent.horizontalCenter

                    text: root.activeLetter.toUpperCase()

                    color: "#1D1D1F"
                    font.pixelSize: 150
                    font.weight: Font.DemiBold
                }

                Row {
                    anchors.horizontalCenter: parent.horizontalCenter
                    spacing: 14

                    visible: root.showMorseCode

                    Repeater {
                        model: LetterTrainer.morse.length

                        delegate: Text {
                            required property int index

                            property string targetSymbol:
                                LetterTrainer.morse.charAt(index)

                            property bool alreadyEntered:
                                index < LetterTrainer.currentInput.length

                            property bool enteredCorrectly:
                                alreadyEntered
                                && LetterTrainer.currentInput.charAt(index)
                                   === targetSymbol

                            text: root.displaySymbol(targetSymbol)

                            color: enteredCorrectly
                                   ? "#34C759"
                                   : "#1D1D1F"

                            font.pixelSize: 58
                            font.weight: Font.DemiBold

                            Behavior on color {
                                ColorAnimation {
                                    duration: 160
                                }
                            }

                            scale: enteredCorrectly ? 1.08 : 1.0

                            Behavior on scale {
                                NumberAnimation {
                                    duration: 160
                                    easing.type: Easing.OutBack
                                }
                            }
                        }
                    }
                }

                Text {
                    anchors.horizontalCenter: parent.horizontalCenter

                    text: LetterTrainer.currentInput.length > 0
                          ? qsTr("Eingabe: %1").arg(
                                root.displayCode(
                                    LetterTrainer.currentInput
                                )
                            )
                          : qsTr("Warte auf Eingabe …")

                    color: LetterTrainer.currentInput.length > 0
                           ? "#6E6E73"
                           : "#AEAEB2"

                    font.pixelSize: 18
                    font.letterSpacing: 3
                }
            }
        }

        Text {
            anchors.horizontalCenter: parent.horizontalCenter

            text: inputType === "2"
                  ? qsTr(
                        "Links: %1 · Rechts: %2"
                    ).arg(leftButtonType).arg(rightButtonType)
                  : qsTr(
                        "Kurzer Tastendruck: Punkt · Langer Tastendruck: Strich"
                    )

            color: "#8E8E93"
            font.pixelSize: 15
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
	trainer: LetterTrainer
	onContinueRequested: {
	    root.newLetter()
	    Qt.callLater(function() {
		root.forceActiveFocus()
	    })
	}
    } 
    Connections {
	target: LetterTrainer

	function onCorrect(elapsedSeconds) {
	    resultDialog.showCorrect(
		root.activeLetter.toUpperCase()
		    + root.activeLetter.toLowerCase(),
		"",
		elapsedSeconds
	    )
	}

	function onMistake() {
	    resultDialog.showMistake(
		root.activeLetter.toUpperCase()
		    + root.activeLetter.toLowerCase(),
		""
	    )
	}
    }
}
