import QtQuick
import QtQuick.Controls

Page {
    id: root

    property int challengeId: -1
    property string challengeMode: "Letter"
    property string challengeText: "e"
    property string inputType: "1"
    property string leftButtonType: "Zeitgesteuert"
    property string rightButtonType: "Zeitgesteuert"

    property var trainer: challengeMode === "Letter"
                          ? LetterTrainer
                          : (challengeMode === "Word" ? WordTrainer : SentenceTrainer)

    // Keep the finished code visible for one second. This is deliberately
    // independent of currentInput because some trainers clear their input
    // immediately after emitting their correct signal.
    property bool showingCorrect: false
    property bool showingMistake: false

    property bool singleDown: false
    property bool leftDown: false
    property bool rightDown: false

    focus: true
    Keys.priority: Keys.BeforeItem

    function startChallenge() {
        showingCorrect = false
        showingMistake = false
        trainer.configureInput(inputType, leftButtonType, rightButtonType)

        if (challengeMode === "Letter")
            LetterTrainer.startLetter(challengeText)
        else if (challengeMode === "Word")
            WordTrainer.startWord(challengeText)
        else
            SentenceTrainer.startSentence(challengeText)

        root.forceActiveFocus()
    }

    function handleCorrect() {
        if (showingCorrect)
            return
        showingCorrect = true
        showingMistake = false
        correctTimer.restart()
    }

    function handleMistake() {
        if (showingMistake)
            return
        showingMistake = true
        showingCorrect = false
        mistakeTimer.restart()
    }

    Component.onCompleted: startChallenge()

    Timer {
        id: correctTimer
        interval: 1000
        repeat: false
        onTriggered: {
            OnlineBridge.completeDaily(challengeId)
            stackView.pop()
        }
    }

    Timer {
        id: mistakeTimer
        interval: 1000
        repeat: false
        onTriggered: startChallenge()
    }

    Keys.onPressed: function(e) {
        if (e.isAutoRepeat || showingCorrect || showingMistake)
            return

        if (e.key === Qt.Key_Space) {
            singleDown = true
            trainer.buttonPressed("single")
            e.accepted = true
        } else if (e.key === Qt.Key_Left) {
            leftDown = true
            trainer.buttonPressed("left")
            e.accepted = true
        } else if (e.key === Qt.Key_Right) {
            rightDown = true
            trainer.buttonPressed("right")
            e.accepted = true
        }
    }

    Keys.onReleased: function(e) {
        if (e.isAutoRepeat)
            return

        if (e.key === Qt.Key_Space && singleDown) {
            singleDown = false
            trainer.buttonReleased("single")
            e.accepted = true
        } else if (e.key === Qt.Key_Left && leftDown) {
            leftDown = false
            trainer.buttonReleased("left")
            e.accepted = true
        } else if (e.key === Qt.Key_Right && rightDown) {
            rightDown = false
            trainer.buttonReleased("right")
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
            text: qsTr("Daily Challenge")
            font.pixelSize: 24
            color: "#6E6E73"
        }

        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: challengeText.toUpperCase()
            font.pixelSize: 56
            font.weight: Font.DemiBold
            color: "#1D1D1F"
        }

        // Same progressive validation as the normal training modes:
        // every correctly entered symbol turns green immediately.
        Row {
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: 10

            Repeater {
                model: trainer && trainer.morse !== undefined ? trainer.morse.length : 0

                delegate: Text {
                    required property int index
                    text: trainer.morse[index] === "." ? "•" : "—"
                    font.pixelSize: 42
                    font.weight: Font.Medium
                    color: {
                        if (root.showingCorrect)
                            return "#34C759"
                        if (root.showingMistake)
                            return index < (trainer.currentInput !== undefined ? trainer.currentInput.length : 0)
                                   ? "#FF3B30" : "#1D1D1F"
                        return index < (trainer.currentInput !== undefined ? trainer.currentInput.length : 0)
                               ? "#34C759" : "#1D1D1F"
                    }
                }
            }
        }

        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: root.showingCorrect
                  ? qsTr("Correct")
                  : (root.showingMistake
                     ? qsTr("Incorrect")
                     : qsTr("Complete it correctly to earn 1 point."))
            color: root.showingCorrect ? "#34C759"
                   : (root.showingMistake ? "#FF3B30" : "#6E6E73")
            font.weight: (root.showingCorrect || root.showingMistake) ? Font.DemiBold : Font.Normal
        }
    }

    Connections {
        target: LetterTrainer
        enabled: challengeMode === "Letter"
        function onCorrect(t) { root.handleCorrect() }
        function onMistake() { root.handleMistake() }
    }

    Connections {
        target: WordTrainer
        enabled: challengeMode === "Word"
        function onWordCorrect(t) { root.handleCorrect() }
        function onMistake() { root.handleMistake() }
    }

    Connections {
        target: SentenceTrainer
        enabled: challengeMode === "Sentence"
        function onSentenceCorrect(t) { root.handleCorrect() }
        function onMistake() { root.handleMistake() }
    }
}
