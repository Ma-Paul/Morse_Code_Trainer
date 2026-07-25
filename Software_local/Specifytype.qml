import QtQuick
import QtQuick.Controls
import "Globalvariables.js" as Globals

Page {
    id: root

    background: Rectangle {
        gradient: Gradient {
            GradientStop {
                position: 0.0
                color: "#FBFBFD"
            }

            GradientStop {
                position: 1.0
                color: "#EEF1F5"
            }
        }
    }

    Rectangle {
        x: 28
        y: 24
        width: 54
        height: 54
        radius: 27

        color: backMouse.pressed
               ? "#D7D7DC"
               : backMouse.containsMouse
                 ? "#E7E7EB"
                 : "#FFFFFF"

        border.color: "#E3E3E8"

        Text {
            anchors.centerIn: parent
            text: "‹"
            color: "#1D1D1F"
            font.pixelSize: 42
            y: -2
        }

        MouseArea {
            id: backMouse
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor

            onClicked: {
                stackView.pop()
            }
        }
    }

    Column {
        anchors.fill: parent
        anchors.margins: 54
        spacing: 28

        Column {
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: 8

            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: qsTr("Was sind die Einstellungen deiner Knöpfe?")
                color: "#1D1D1F"
                font.family: "SF Pro Display"
                font.pixelSize: 42
                font.weight: Font.DemiBold
            }

            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: qsTr("Lege fest, welche Funktion links und rechts ausgelöst wird.")
                color: "#6E6E73"
                font.family: "SF Pro Text"
                font.pixelSize: 17
            }
        }

        Row {
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: 28

            Repeater {
                model: [
                    {
                        title: qsTr("Links"),
                        side: "left"
                    },
                    {
                        title: qsTr("Rechts"),
                        side: "right"
                    }
                ]

                delegate: Rectangle {
                    id: sideCard

                    required property var modelData

                    property bool isLeft: modelData.side === "left"

                    width: Math.min(430, (root.width - 190) / 2)
                    height: Math.min(570, root.height - 245)
                    radius: 30
                    color: "#FFFFFF"
                    border.color: "#E4E4E9"
                    border.width: 1

                    Column {
                        anchors.fill: parent
                        anchors.margins: 26
                        spacing: 18

                        Text {
                            text: sideCard.modelData.title
                            color: "#1D1D1F"
                            font.family: "SF Pro Display"
                            font.pixelSize: 30
                            font.weight: Font.DemiBold
                        }

                        ComboBox {
                            id: chooser

                            width: parent.width
                            height: 48

                            model: [
                                "Pause",
                                "Lang",
                                "Kurz",
                                "Zeitgesteuert"
                            ]

                            font.pixelSize: 17

                            Component.onCompleted: {
                                const savedValue = sideCard.isLeft
                                                   ? Globals.lefttype
                                                   : Globals.righttype

                                const savedIndex = find(savedValue)

                                if (savedIndex >= 0) {
                                    currentIndex = savedIndex
                                } else {
                                    currentIndex = 3
                                }

                                saveSelection()
                            }

                            function saveSelection() {
                                if (sideCard.isLeft) {
                                    Globals.setLefttype(currentText)
                                } else {
                                    Globals.setRighttype(currentText)
                                }
                            }

                            onActivated: function(selectedIndex) {
                                chooser.currentIndex = selectedIndex
                                chooser.saveSelection()
                            }
                        }

                        Rectangle {
                            width: parent.width
                            height: parent.height - 110
                            radius: 22
                            color: "#F7F7F9"
                            clip: true

                            Column {
                                anchors.centerIn: parent
                                spacing: 18

                                Text {
                                    anchors.horizontalCenter: parent.horizontalCenter

                                    text: {
                                        switch (chooser.currentText) {
                                        case "Kurz":
                                            return "•"

                                        case "Lang":
                                            return "—"

                                        case "Zeitgesteuert":
                                            return "◷"

                                        default:
                                            return "Ⅱ"
                                        }
                                    }

                                    color: "#1D1D1F"
                                    font.pixelSize: 100
                                    font.weight: Font.DemiBold
                                }

                                Text {
                                    anchors.horizontalCenter: parent.horizontalCenter
                                    width: sideCard.width - 90

                                    horizontalAlignment: Text.AlignHCenter
                                    wrapMode: Text.WordWrap

                                    text: {
                                        switch (chooser.currentText) {
                                        case "Kurz":
                                            return qsTr("Dieser Knopf erzeugt immer einen kurzen Morsepunkt.")

                                        case "Lang":
                                            return qsTr("Dieser Knopf erzeugt immer einen langen Morsestrich.")

                                        case "Zeitgesteuert":
                                            return qsTr("Die Dauer des Tastendrucks entscheidet zwischen kurz und lang.")

                                        default:
                                            return qsTr("Die Dauer des Tastendrucks entscheidet zwischen einer Buchstaben- und Wortpause (nicht aktiv im Buchstabenmodus)")
                                        }
                                    }

                                    color: "#6E6E73"
                                    font.family: "SF Pro Text"
                                    font.pixelSize: 16
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    Rectangle {
        id: nextButton

        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.rightMargin: 34
        anchors.bottomMargin: 30

        width: 164
        height: 58
        radius: 20

        color: nextMouse.pressed
               ? "#0068D9"
               : nextMouse.containsMouse
                 ? "#1684FF"
                 : "#007AFF"

        scale: nextMouse.pressed ? 0.98 : 1.0

        Behavior on scale {
            NumberAnimation {
                duration: 120
            }
        }

        Row {
            anchors.centerIn: parent
            spacing: 10

            Text {
                text: qsTr("Weiter")
                color: "white"
                font.pixelSize: 20
                font.weight: Font.DemiBold
            }

            Text {
                text: "›"
                color: "white"
                font.pixelSize: 31
                y: -2
            }
        }

        MouseArea {
            id: nextMouse

            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor

            onClicked: {
                stackView.push("Mode.qml")
            }
        }
    }
}
