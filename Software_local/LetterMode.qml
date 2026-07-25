import QtQuick
import QtQuick.Controls

Page {
    id: root
    property bool simulatedSingleButtonDown: false
    property bool simulatedLeftButtonDown: false
    property bool simulatedRightButtonDown: false
    property bool showMorseCode: true

    property string inputType: "1"
    property string leftButtonType: "Zeitgesteuert"
    property string rightButtonType: "Zeitgesteuert"

    property string activeLetter: "l"

    property real resultTime: 0

    property string wrongEntered: ""
    property string wrongExpected: ""
    property string wrongExplanation: ""

    function displaySymbol(symbol) {
        return symbol === "." ? "•" : "—"
    }

    function displayCode(code) {
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

    Component.onCompleted: {
        LetterTrainer.configureInput(
            inputType,
            leftButtonType,
            rightButtonType
        )

        newLetter()
        forceActiveFocus()
    }

    Component.onDestruction: {
        LetterTrainer.stop()
    }
    focus: true

    Keys.onPressed: function(event) {
	if (!DevelopmentMode.enabled
		|| !DevelopmentMode.keyboardSimulationEnabled) {
	    return
	}

	// Ignore automatic key-repeat events.
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

    focus: true

    Keys.onPressed: function(event) {
        if (event.key === Qt.Key_Period) {
            LetterTrainer.submitSymbol(".")
            event.accepted = true

        } else if (event.key === Qt.Key_Minus) {
            LetterTrainer.submitSymbol("_")
            event.accepted = true

        } else if (
            event.key === Qt.Key_Return
            || event.key === Qt.Key_Enter
            || event.key === Qt.Key_Space
        ) {
            LetterTrainer.finishLetter()
            event.accepted = true
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

    Column {
        anchors.centerIn: parent
        spacing: 18

        Text {
            anchors.horizontalCenter: parent.horizontalCenter

            text: qsTr("Buchstabenmodus")
            color: "#6E6E73"
            font.family: "SF Pro Text"
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
                    font.family: "Serif"
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

                            font.family: "SF Pro Display"
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

                    font.family: "SF Pro Text"
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
            font.family: "SF Pro Text"
            font.pixelSize: 15
        }
    }

    Dialog {
        id: correctDialog

        anchors.centerIn: parent
        modal: true
        closePolicy: Popup.NoAutoClose

        width: 390
        padding: 0

        background: Rectangle {
            radius: 28
            color: "#FFFFFF"
            border.color: "#E4E4E9"
        }

        contentItem: Column {
            padding: 30
            spacing: 16

            Text {
                anchors.horizontalCenter: parent.horizontalCenter

                text: "✓"
                color: "#34C759"
                font.pixelSize: 54
                font.weight: Font.DemiBold
            }

            Text {
                anchors.horizontalCenter: parent.horizontalCenter

                text: qsTr("Richtig")
                color: "#1D1D1F"
                font.family: "SF Pro Display"
                font.pixelSize: 30
                font.weight: Font.DemiBold
            }

            Text {
                anchors.horizontalCenter: parent.horizontalCenter

                text: qsTr(
                    "Zeit: %1 s"
                ).arg(root.resultTime.toFixed(2))

                color: "#6E6E73"
                font.family: "SF Pro Text"
                font.pixelSize: 18
            }

            Button {
                anchors.horizontalCenter: parent.horizontalCenter
                text: qsTr("Weiter")

                onClicked: {
                    correctDialog.close()
                    root.newLetter()
                    root.forceActiveFocus()
                }
            }
        }
    }

    Dialog {
        id: mistakeDialog

        anchors.centerIn: parent
        modal: true
        closePolicy: Popup.NoAutoClose

        width: 470
        padding: 0

        background: Rectangle {
            radius: 28
            color: "#FFFFFF"
            border.color: "#E4E4E9"
        }

        contentItem: Column {
            padding: 30
            spacing: 16

            Text {
                anchors.horizontalCenter: parent.horizontalCenter

                text: "!"
                color: "#FF3B30"
                font.pixelSize: 54
                font.weight: Font.DemiBold
            }

            Text {
                anchors.horizontalCenter: parent.horizontalCenter

                text: qsTr("Nicht ganz richtig")
                color: "#1D1D1F"
                font.family: "SF Pro Display"
                font.pixelSize: 28
                font.weight: Font.DemiBold
            }

            Text {
                width: parent.width
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.WordWrap

                text: root.wrongExplanation

                color: "#6E6E73"
                font.family: "SF Pro Text"
                font.pixelSize: 17
            }

            Rectangle {
                width: parent.width
                height: codeInformation.height + 28
                radius: 18
                color: "#F7F7F9"

                Column {
                    id: codeInformation

                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.leftMargin: 18
                    anchors.rightMargin: 18

                    spacing: 10

                    Text {
                        width: parent.width

                        text: qsTr(
                            "Deine Eingabe: %1"
                        ).arg(
                            root.wrongEntered.length > 0
                            ? root.displayCode(root.wrongEntered)
                            : qsTr("keine Eingabe")
                        )

                        color: "#FF3B30"
                        font.family: "SF Pro Text"
                        font.pixelSize: 17
                        wrapMode: Text.WordWrap
                    }

                    Text {
                        width: parent.width

                        text: qsTr(
                            "Richtiger Code: %1"
                        ).arg(
                            root.displayCode(root.wrongExpected)
                        )

                        color: "#1D1D1F"
                        font.family: "SF Pro Text"
                        font.pixelSize: 17
                        font.weight: Font.DemiBold
                        wrapMode: Text.WordWrap
                    }
                }
            }

            Button {
                anchors.horizontalCenter: parent.horizontalCenter
                text: qsTr("Weiter")

                onClicked: {
                    mistakeDialog.close()
                    root.newLetter()
                    root.forceActiveFocus()
                }
            }
        }
    }

    Connections {
        target: LetterTrainer

        function onCorrect(elapsedSeconds) {
            root.resultTime = elapsedSeconds
            correctDialog.open()
        }

        function onMistake(
            entered,
            expected,
            explanation
        ) {
            root.wrongEntered = entered
            root.wrongExpected = expected
            root.wrongExplanation = explanation

            mistakeDialog.open()
        }
    }
}
