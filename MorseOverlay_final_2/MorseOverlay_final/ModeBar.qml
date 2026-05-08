// ModeBar.qml
import QtQuick

Item {
    property var logic
    property color cPanel; property color cBorder
    property color cAccent; property color cGreen
    property color cAmber;  property color cRed
    property color cGray;   property color cLgray
    property color cWhite

    readonly property var modeNames:  ["Buchstabe", "Wort", "Satz", "Datei"]
    readonly property var modeIcons:  ["A", "Hi", "Sa", "Da"]
    readonly property var modeColors: [cAccent, cGreen, cAmber, cRed]

    Rectangle {
        anchors.fill: parent
        color: cPanel
        radius: 10
        border.color: cBorder; border.width: 1

        Text {
            x: 12; y: 8
            text: "MODUSWALL"
            font.family: "Courier New"; font.pixelSize: 11
            color: cLgray
        }

        // Mode buttons row
        Row {
            x: 12; y: 30
            spacing: 8

            Repeater {
                model: 4
                delegate: Rectangle {
                    width: 56; height: 80
                    radius: 6
                    color: logic.mode === index ? modeColors[index] : cGray
                    border.color: cBorder; border.width: 1

                    Behavior on color { ColorAnimation { duration: 150 } }

                    Column {
                        anchors.centerIn: parent
                        spacing: 6
                        Text {
                            anchors.horizontalCenter: parent.horizontalCenter
                            text: modeIcons[index]
                            font.family: "Courier New"; font.pixelSize: 22; font.bold: true
                            color: cWhite
                        }
                        Text {
                            anchors.horizontalCenter: parent.horizontalCenter
                            text: modeNames[index]
                            font.family: "Courier New"; font.pixelSize: 11
                            color: cWhite
                        }
                    }

                    MouseArea {
                        anchors.fill: parent
                        onClicked: {
                            logic.commitChar()
                            logic.mode = index
                            logic.outputText = ""
                            logic.currentWord = ""
                        }
                    }
                }
            }
        }

        // Down arrow indicator
        Canvas {
            x: (parent.width - 24) / 2
            y: 125
            width: 24; height: 20
            onPaint: {
                var ctx = getContext("2d")
                ctx.clearRect(0, 0, width, height)
                ctx.fillStyle = cAccent
                ctx.beginPath()
                ctx.moveTo(0, 0); ctx.lineTo(24, 0); ctx.lineTo(12, 20)
                ctx.closePath(); ctx.fill()
            }
        }

        Text {
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 10
            x: 12
            text: "TAB = Modus wechseln"
            font.family: "Courier New"; font.pixelSize: 11
            color: cLgray
        }
    }
}
