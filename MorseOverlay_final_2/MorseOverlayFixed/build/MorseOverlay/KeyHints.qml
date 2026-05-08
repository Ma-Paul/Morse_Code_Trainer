// KeyHints.qml
import QtQuick

Item {
    property var   logic
    property color accentColor
    property color amberColor
    property color whiteColor
    property color redColor
    property color greenColor
    property color lgrayColor

    readonly property var hints: {
        var cfg = logic.currentConfig()
        if (!cfg) return []
        return [
            { text: "LINKS  →  " + (cfg.left  === "." ? "·" : "−"), col: accentColor },
            { text: "RECHTS →  " + (cfg.right === "." ? "·" : "−"), col: amberColor  },
            { text: "SPACE  →  Buchstabe abschließen",               col: whiteColor  },
            { text: "ENTER  →  Wort abschließen",                    col: whiteColor  },
            { text: "BACK   →  Löschen",                             col: redColor    },
            { text: "TAB    →  Modus",                               col: greenColor  },
            { text: "C      →  Config",                              col: lgrayColor  },
            { text: "ESC    →  Beenden",                             col: lgrayColor  },
        ]
    }

    Grid {
        columns: 4
        rowSpacing: 6
        columnSpacing: 0

        Repeater {
            model: hints.length
            delegate: Text {
                required property int index
                width: 210
                text: hints[index].text
                font.family: "Courier New"; font.pixelSize: 13
                color: hints[index].col
            }
        }
    }

    Text {
        visible: logic.statusMsg.length > 0
        anchors.bottom: parent.bottom
        text: logic.statusMsg
        font.family: "Courier New"; font.pixelSize: 16
        color: redColor
    }
}
