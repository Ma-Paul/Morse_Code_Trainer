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
                text: qsTr("Configure your buttons")
                color: "#1D1D1F"
                font.family: "SF Pro Display"
                font.pixelSize: 42
                font.weight: Font.DemiBold
            }

            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: qsTr("Choose the function of the left and right buttons.")
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
                        title: qsTr("Left"),
                        side: "left"
                    },
                    {
                        title: qsTr("Right"),
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

                            textRole: "label"
                            valueRole: "value"
                            model: [
                                { label: qsTr("Gap"), value: "Pause" },
                                { label: qsTr("Dash"), value: "Lang" },
                                { label: qsTr("Dot"), value: "Kurz" },
                                { label: qsTr("Timed"), value: "Zeitgesteuert" }
                            ]

                            font.pixelSize: 17

                            Component.onCompleted: {
                                const savedValue = sideCard.isLeft
                                                   ? Globals.lefttype
                                                   : Globals.righttype

                                const savedIndex = indexOfValue(savedValue)

                                if (savedIndex >= 0) {
                                    currentIndex = savedIndex
                                } else {
                                    currentIndex = 3
                                }

                                saveSelection()
                            }

                            function saveSelection() {
                                if (sideCard.isLeft) {
                                    Globals.setLefttype(currentValue)
                                } else {
                                    Globals.setRighttype(currentValue)
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
                                        switch (chooser.currentValue) {
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
                                        switch (chooser.currentValue) {
                                        case "Kurz":
                                            return qsTr("This button always enters a dot.")

                                        case "Lang":
                                            return qsTr("This button always enters a dash.")

                                        case "Zeitgesteuert":
                                            return qsTr("Press duration determines whether a dot or a dash is entered.")

                                        default:
                                            return qsTr("Press duration determines the gap between letters or words (unused in letter mode).")
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
                text: qsTr("Continue")
                color: "white"
                font.pixelSize: 20
                font.weight: Font.DemiBold
		y: 8
            }

            Text {
                text: "›"
                color: "white"
                font.pixelSize: 31
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
