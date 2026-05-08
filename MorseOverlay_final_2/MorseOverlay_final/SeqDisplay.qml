// SeqDisplay.qml
import QtQuick

Item {
    property var logic
    property color cPanel; property color cBorder
    property color cAccent; property color cAmber
    property color cGray;   property color cLgray

    Rectangle {
        anchors.fill: parent
        color: cPanel
        radius: 8
        border.color: cBorder; border.width: 1

        Text {
            x: 10; y: 6
            text: "AKTUELLE SEQUENZ"
            font.family: "Courier New"; font.pixelSize: 11
            color: cLgray
        }

        // Dots and dashes
        Row {
            x: 10
            anchors.verticalCenter: parent.verticalCenter
            anchors.verticalCenterOffset: 6
            spacing: 8

            Repeater {
                model: logic.currentSeq.length
                delegate: Item {
                    property string sig: logic.currentSeq[index]
                    width: sig === "." ? 26 : 46
                    height: 26

                    // Dot
                    Rectangle {
                        visible: sig === "."
                        anchors.centerIn: parent
                        width: 20; height: 20; radius: 10
                        color: cAccent
                    }

                    // Dash
                    Rectangle {
                        visible: sig === "-"
                        anchors.centerIn: parent
                        width: 40; height: 18; radius: 4
                        color: cAmber
                    }
                }
            }
        }

        // Placeholder
        Text {
            visible: logic.currentSeq.length === 0
            x: 10
            anchors.verticalCenter: parent.verticalCenter
            text: "warte auf Eingabe…"
            font.family: "Courier New"; font.pixelSize: 16
            color: cGray
        }
    }
}
