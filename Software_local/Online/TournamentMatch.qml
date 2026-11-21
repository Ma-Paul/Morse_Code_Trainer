import QtQuick
import QtQuick.Controls

Page {
    id: root

    property int matchId: -1
    property string inputType: "1"
    property string leftButtonType: "Zeitgesteuert"
    property string rightButtonType: "Zeitgesteuert"

    property bool singleDown: false
    property bool leftDown: false
    property bool rightDown: false

    focus: true
    Keys.priority: Keys.BeforeItem

    Component.onCompleted: {
        PhysicalInput.setActiveMode("Tournament")

        // Use the settings passed to this page. TournamentMatch.qml is in
        // Online/, so relying on an unimported Globals object prevented the
        // rest of onCompleted (including OnlineGame.start) from running.
        OnlineGame.configureInput(
            inputType,
            leftButtonType,
            rightButtonType
        )

        if (!OnlineGame.start(matchId)) {
            console.log("Could not start tournament match", matchId)
        }

        Qt.callLater(function() {
            root.forceActiveFocus()
        })
    }

    Component.onDestruction: {
        OnlineGame.stop()
        PhysicalInput.clearActiveMode()
    }

    Keys.onPressed: function(e) {
        if (e.isAutoRepeat || OnlineGame.showingCorrect || OnlineGame.showingMistake)
            return

        if (e.key === Qt.Key_Space) {
            singleDown = true
            OnlineGame.buttonPressed("single")
            e.accepted = true
        } else if (e.key === Qt.Key_Left) {
            leftDown = true
            OnlineGame.buttonPressed("left")
            e.accepted = true
        } else if (e.key === Qt.Key_Right) {
            rightDown = true
            OnlineGame.buttonPressed("right")
            e.accepted = true
        }
    }

    Keys.onReleased: function(e) {
        if (e.isAutoRepeat)
            return

        if (e.key === Qt.Key_Space && singleDown) {
            singleDown = false
            OnlineGame.buttonReleased("single")
            e.accepted = true
        } else if (e.key === Qt.Key_Left && leftDown) {
            leftDown = false
            OnlineGame.buttonReleased("left")
            e.accepted = true
        } else if (e.key === Qt.Key_Right && rightDown) {
            rightDown = false
            OnlineGame.buttonReleased("right")
            e.accepted = true
        }
    }

    background: Rectangle {
        gradient: Gradient {
            GradientStop { position: 0; color: "#FBFBFD" }
            GradientStop { position: 1; color: "#EEF1F5" }
        }
    }

    Column {
        anchors.centerIn: parent
        spacing: 20

        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: OnlineGame.secondsLeft + " s"
            font.pixelSize: 28
            color: "#007AFF"
        }

	Text {
	    anchors.horizontalCenter: parent.horizontalCenter

	    text: OnlineGame.mode === "Sentence"
		  ? OnlineGame.currentWord.toUpperCase()
		  : OnlineGame.mode === "Word"
		    ? OnlineGame.currentWord.toUpperCase()
		    : (
			OnlineGame.currentLetter.length > 0
			? OnlineGame.currentLetter.toUpperCase()
			  + OnlineGame.currentLetter.toLowerCase()
			: ""
		      )

	    font.pixelSize: 64
	    font.weight: Font.DemiBold
	    color: "#1D1D1F"
	}
        // Progressive Morse validation, matching the normal training modes.
        // The entire expected code remains green for one second after a
        // correct answer before OnlineGame advances to the next challenge.
	Row {
	    anchors.horizontalCenter: parent.horizontalCenter
	    spacing: 10

	    Repeater {
		model: OnlineGame.morse.length

		delegate: Text {
		    required property int index

		    property string expectedSymbol:
			OnlineGame.morse.charAt(index)

		    text:
			expectedSymbol === "."
			? "•"
			: "—"

		    font.pixelSize: 42
		    font.weight: Font.DemiBold

		    color: {
			if (OnlineGame.showingCorrect)
			    return "#34C759"

			if (OnlineGame.showingMistake) {
			    return index < OnlineGame.currentInput.length
				   ? "#FF3B30"
				   : "#1D1D1F"
			}

			return index < OnlineGame.currentInput.length
			       ? "#34C759"
			       : "#1D1D1F"
		    }
		}
	    }
	}
        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            visible: OnlineGame.showingCorrect || OnlineGame.showingMistake
            text: OnlineGame.showingCorrect ? qsTr("Correct") : qsTr("Incorrect")
            color: OnlineGame.showingCorrect ? "#34C759" : "#FF3B30"
            font.pixelSize: 20
            font.weight: Font.DemiBold
        }

        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: qsTr("Score: %1").arg(OnlineGame.score)
            font.pixelSize: 26
            color: "#6E6E73"
        }

        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: qsTr("Both players receive the same challenge sequence.")
            color: "#8E8E93"
        }
    }

    Connections {
        target: OnlineGame
        function onFinished(score, time) {
            result.open()
        }
    }

    Dialog {
        id: result
        anchors.centerIn: parent
        modal: true
        closePolicy: Popup.NoAutoClose
        title: qsTr("Match finished")

        Column {
            spacing: 12
            Text {
                text: qsTr("Score: %1").arg(OnlineGame.score)
                font.pixelSize: 24
            }
            Button {
                text: qsTr("Back to Online")
                onClicked: {
                    result.close()
                    stackView.pop()
                }
            }
        }
    }
}
