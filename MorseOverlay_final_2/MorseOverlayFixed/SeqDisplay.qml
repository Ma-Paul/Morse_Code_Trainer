// SeqDisplay.qml
import QtQuick

Item {
    property var   logic
    property color panelColor
    property color borderColor
    property color accentColor
    property color amberColor
    property color grayColor
    property color lgrayColor

    Rectangle {
        anchors.fill: parent
        color: panelColor
        radius: 8
        border.color: borderColor; border.width: 1

        Text {
            x: 10; y: 6
            text: "AKTUELLE SEQUENZ"
            font.family: "Courier New"; font.pixelSize: 11
            color: lgrayColor
        }

        Row {
            x: 10
            anchors.verticalCenter: parent.verticalCenter
            anchors.verticalCenterOffset: 6
            spacing: 8

            Repeater {
                model: logic.currentSeq.length
                delegate: Item {
                    required property int index
                    readonly property string sig: logic.currentSeq[index]
                    width: sig === "." ? 26 : 46
                    height: 26

                    Rectangle {
                        visible: sig === "."
                        anchors.centerIn: parent
                        width: 20; height: 20; radius: 10
                        color: accentColor
                    }

                    Rectangle {
                        visible: sig === "-"
                        anchors.centerIn: parent
                        width: 40; height: 18; radius: 4
                        color: amberColor
                    }
                }
            }
        }

        Text {
            visible: logic.currentSeq.length === 0
            x: 10
            anchors.verticalCenter: parent.verticalCenter
            text: "warte auf Eingabe…"
            font.family: "Courier New"; font.pixelSize: 16
            color: grayColor
        }
    }
}
