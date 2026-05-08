// TopBar.qml
import QtQuick

Item {
    property var logic
    property color cPanel; property color cBorder
    property color cAccent; property color cLgray

    Rectangle {
        anchors.fill: parent
        color: cPanel

        Rectangle {
            anchors.bottom: parent.bottom
            width: parent.width; height: 1
            color: cBorder
        }

        Text {
            x: 16; anchors.verticalCenter: parent.verticalCenter
            text: "BINÄREINGABE OVERLAY"
            font.family: "Courier New"; font.pixelSize: 16
            color: cAccent
        }

        Text {
            anchors.right: parent.right
            anchors.rightMargin: 16
            anchors.verticalCenter: parent.verticalCenter
            text: "Eingabe: " + (logic.inputMode === logic.input1key ? "1 Taste" : "2 Tasten")
                + "  |  Config #" + (logic.keyConfigIdx + 1)
            font.family: "Courier New"; font.pixelSize: 16
            color: cLgray
        }
    }
}
