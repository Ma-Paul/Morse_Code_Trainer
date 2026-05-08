// ConfigPanel.qml
import QtQuick

Item {
    property var   logic
    property color panelColor
    property color accentColor
    property color greenColor
    property color grayColor
    property color whiteColor
    property color lgrayColor

    Rectangle {
        anchors.fill: parent
        color: "#b3000000"
    }

    Rectangle {
        x: 150; y: 100
        width: 600; height: 380
        color: panelColor
        radius: 12
        border.color: accentColor; border.width: 2

        Text {
            x: 20; y: 16
            text: "Moduswall — Eingabe-Konfiguration"
            font.family: "Courier New"; font.pixelSize: 22; font.bold: true
            color: accentColor
        }

        Column {
            x: 20; y: 60
            spacing: 10

            Repeater {
                model: logic.currentConfigs().length
                delegate: Rectangle {
                    required property int index
                    width: 560; height: 50
                    radius: 6
                    color: logic.keyConfigIdx === index ? greenColor : grayColor

                    Behavior on color { ColorAnimation { duration: 120 } }

                    Text {
                        x: 12
                        anchors.verticalCenter: parent.verticalCenter
                        text: "[" + (index + 1) + "]  " + logic.currentConfigs()[index].label
                        font.family: "Courier New"; font.pixelSize: 17
                        color: whiteColor
                    }

                    MouseArea {
                        anchors.fill: parent
                        onClicked: logic.keyConfigIdx = index
                    }
                }
            }
        }

        Text {
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 16
            x: 20
            text: "C oder ESC zum Schließen"
            font.family: "Courier New"; font.pixelSize: 15
            color: lgrayColor
        }
    }
}
