// TopBar.qml
import QtQuick

Item {
    property var   logic
    property color panelColor
    property color borderColor
    property color accentColor
    property color lgrayColor

    Rectangle {
        anchors.fill: parent
        color: panelColor

        Rectangle {
            anchors.bottom: parent.bottom
            width: parent.width; height: 1
            color: borderColor
        }

        Text {
            x: 16
            anchors.verticalCenter: parent.verticalCenter
            text: "BINÄREINGABE OVERLAY"
            font.family: "Courier New"; font.pixelSize: 16
            color: accentColor
        }

        Text {
            anchors.right: parent.right
            anchors.rightMargin: 16
            anchors.verticalCenter: parent.verticalCenter
            text: "Eingabe: " + (logic.inputMode === logic.input1key ? "1 Taste" : "2 Tasten")
                  + "  |  Config #" + (logic.keyConfigIdx + 1)
            font.family: "Courier New"; font.pixelSize: 16
            color: lgrayColor
        }
    }
}
