// ModeBar.qml
import QtQuick

Item {
    property var   logic
    property color panelColor
    property color borderColor
    property color accentColor
    property color greenColor
    property color amberColor
    property color redColor
    property color grayColor
    property color lgrayColor
    property color whiteColor

    readonly property var modeNames:  ["Buchstabe", "Wort", "Satz", "Datei"]
    readonly property var modeIcons:  ["A", "Hi", "Sa", "Da"]
    readonly property var modeColors: [accentColor, greenColor, amberColor, redColor]

    Rectangle {
        anchors.fill: parent
        color: panelColor
        radius: 10
        border.color: borderColor; border.width: 1

        Text {
            x: 12; y: 8
            text: "MODUSWALL"
            font.family: "Courier New"; font.pixelSize: 11
            color: lgrayColor
        }

        Row {
            x: 12; y: 30
            spacing: 8

            Repeater {
                model: 4
                delegate: Rectangle {
                    width: 56; height: 80
                    radius: 6
                    color: logic.mode === index ? modeColors[index] : grayColor
                    border.color: borderColor; border.width: 1

                    Behavior on color { ColorAnimation { duration: 150 } }

                    Column {
                        anchors.centerIn: parent
                        spacing: 6

                        Text {
                            anchors.horizontalCenter: parent.horizontalCenter
                            text: modeIcons[index]
                            font.family: "Courier New"; font.pixelSize: 22; font.bold: true
                            color: whiteColor
                        }
                        Text {
                            anchors.horizontalCenter: parent.horizontalCenter
                            text: modeNames[index]
                            font.family: "Courier New"; font.pixelSize: 11
                            color: whiteColor
                        }
                    }

                    MouseArea {
                        anchors.fill: parent
                        onClicked: {
                            logic.commitChar()
                            logic.mode        = index
                            logic.outputText  = ""
                            logic.currentWord = ""
                        }
                    }
                }
            }
        }

        Canvas {
            x: (parent.width - 24) / 2
            y: 125
            width: 24; height: 20
            onPaint: {
                var ctx = getContext("2d")
                ctx.clearRect(0, 0, width, height)
                ctx.fillStyle = accentColor
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
            color: lgrayColor
        }
    }
}
