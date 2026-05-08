// MainDisplay.qml
import QtQuick

Item {
    property var   logic
    property color panelColor
    property color borderColor
    property color whiteColor
    property color greenColor
    property color lgrayColor
    property color amberColor

    Rectangle {
        anchors.fill: parent
        color: panelColor
        radius: 10
        border.color: borderColor; border.width: 1

        Text {
            x: 12; y: 8
            text: "BILD / AUSGABE"
            font.family: "Courier New"; font.pixelSize: 11
            color: lgrayColor
        }

        // Letter mode — single big char
        Text {
            visible: logic.mode === logic.modeLetter
            anchors.centerIn: parent
            text: logic.outputText.length > 0 ? logic.outputText.slice(-1) : "—"
            font.family: "Courier New"; font.pixelSize: 72; font.bold: true
            color: whiteColor
        }

        // Other modes — wrapped text
        Text {
            visible: logic.mode !== logic.modeLetter
            x: 12; y: 40
            width: parent.width - 24
            wrapMode: Text.WordWrap
            text: logic.outputText.length > 0 ? logic.outputText : "—"
            font.family: "Courier New"; font.pixelSize: 26
            color: whiteColor
        }

        // Live decode hint
        Text {
            visible: logic.decodedChar.length > 0 && logic.decodedChar !== "?"
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 40
            x: 12
            text: "→ " + logic.decodedChar
            font.family: "Courier New"; font.pixelSize: 22
            color: greenColor
        }

        // Subtitle
        Text {
            anchors.bottom: parent.bottom
            anchors.bottomMargin: -20
            x: 12
            text: "Drücke Tasten  •  warte auf Timeout oder drücke SPACE"
            font.family: "Courier New"; font.pixelSize: 11
            color: lgrayColor
        }
    }
}
