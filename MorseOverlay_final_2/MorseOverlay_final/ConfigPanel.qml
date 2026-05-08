// ConfigPanel.qml
import QtQuick

Item {
    property var logic
    property color cPanel; property color cAccent
    property color cGreen; property color cGray
    property color cWhite; property color cLgray

    // Dim background
    Rectangle {
        anchors.fill: parent
        color: "#b3000000"
    }

    // Panel
    Rectangle {
        x: 150; y: 100
        width: 600; height: 380
        color: cPanel
        radius: 12
        border.color: cAccent; border.width: 2

        Text {
            x: 20; y: 16
            text: "Moduswall — Eingabe-Konfiguration"
            font.family: "Courier New"; font.pixelSize: 22; font.bold: true
            color: cAccent
        }

        Column {
            x: 20; y: 60
            spacing: 10

            Repeater {
                model: logic.currentConfigs().length
                delegate: Rectangle {
                    width: 560; height: 50
                    radius: 6
                    color: logic.keyConfigIdx === index ? cGreen : cGray

                    Behavior on color { ColorAnimation { duration: 120 } }

                    Text {
                        x: 12
                        anchors.verticalCenter: parent.verticalCenter
                        text: "[" + (index + 1) + "]  " + logic.currentConfigs()[index].label
                        font.family: "Courier New"; font.pixelSize: 17
                        color: cWhite
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
            color: cLgray
        }
    }
}
