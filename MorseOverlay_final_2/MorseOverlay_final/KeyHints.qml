// KeyHints.qml
import QtQuick

Item {
    property var logic
    property color cAccent; property color cAmber
    property color cWhite;  property color cRed
    property color cGreen;  property color cLgray

    // Build hints dynamically so left/right reflects current config
    readonly property var hints: {
        var cfg = logic.currentConfig()
        return [
            { text: "LINKS  →  " + (cfg.left === "." ? "·" : "−"),  col: cAccent },
            { text: "RECHTS →  " + (cfg.right === "." ? "·" : "−"), col: cAmber  },
            { text: "SPACE  →  Buchstabe abschließen",               col: cWhite  },
            { text: "ENTER  →  Wort abschließen",                    col: cWhite  },
            { text: "BACK   →  Löschen",                             col: cRed    },
            { text: "TAB    →  Modus",                               col: cGreen  },
            { text: "C      →  Config",                              col: cLgray  },
            { text: "ESC    →  Beenden",                             col: cLgray  },
        ]
    }

    Grid {
        columns: 4
        rowSpacing: 6
        columnSpacing: 0

        Repeater {
            model: hints.length
            delegate: Text {
                width: 210
                text: hints[index].text
                font.family: "Courier New"; font.pixelSize: 13
                color: hints[index].col
            }
        }
    }

    // Status message
    Text {
        visible: logic.statusMsg.length > 0
        anchors.bottom: parent.bottom
        text: logic.statusMsg
        font.family: "Courier New"; font.pixelSize: 16
        color: cRed
    }
}
