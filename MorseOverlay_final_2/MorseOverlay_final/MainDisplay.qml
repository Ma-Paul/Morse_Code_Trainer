// MainDisplay.qml
import QtQuick

Item {
    property var logic
    property var flashAnim
    property color cPanel; property color cBorder
    property color cWhite; property color cGreen
    property color cLgray; property color cAmber

    Rectangle {
        anchors.fill: parent
        color: cPanel
        radius: 10
        border.color: cBorder; border.width: 1

        Text {
            x: 12; y: 8
            text: "BILD / AUSGABE"
            font.family: "Courier New"; font.pixelSize: 11
            color: cLgray
        }

        // ── Letter mode: single big char ──────────────────────
        Text {
            visible: logic.mode === logic.modeLetter
            anchors.centerIn: parent
            text: (logic.outputText || "—").slice(-1)
            font.family: "Courier New"; font.pixelSize: 72; font.bold: true
            color: cWhite
        }

        // ── Other modes: wrapped text ─────────────────────────
        Text {
            visible: logic.mode !== logic.modeLetter
            x: 12; y: 40
            width: parent.width - 24
            wrapMode: Text.WordWrap
            text: logic.outputText || "—"
            font.family: "Courier New"; font.pixelSize: 26
            color: cWhite
        }

        // ── Live decode hint ──────────────────────────────────
        Text {
            visible: logic.decodedChar && logic.decodedChar !== "?"
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 40
            x: 12
            text: "→ " + logic.decodedChar
            font.family: "Courier New"; font.pixelSize: 22
            color: cGreen
        }

        // ── Subtitle ──────────────────────────────────────────
        Text {
            anchors.bottom: parent.bottom
            anchors.bottomMargin: -20
            x: 0
            text: "Drücke Tasten  •  warte auf Timeout oder drücke SPACE"
            font.family: "Courier New"; font.pixelSize: 11
            color: cLgray
        }
    }
}
