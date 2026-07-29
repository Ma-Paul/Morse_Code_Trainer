import QtQuick
import QtQuick.Controls
import "Globalvariables.js" as Globals

Page {
    id: root

    function selectMode(value) {
        Globals.setMode(value)

        AppBridge.saveSettings(
            Globals.eingabeart,
            Globals.lefttype,
            Globals.righttype,
            Globals.mode
        )

        if (value === "Letter") {
            stackView.push("Letter/LetterMode.qml", {
                showMorseCode: Globals.showLetterMorse,
                inputType: Globals.eingabeart,
                leftButtonType: Globals.lefttype,
                rightButtonType: Globals.righttype
            })
	} else if (value === "Word") {
	    stackView.push("Word/WordMode.qml", {
		showMorseCode: Globals.showLetterMorse,
		inputType: Globals.eingabeart,
		leftButtonType: Globals.lefttype,
		rightButtonType: Globals.righttype

	    })
    } else if (value === "Sentence") {
        stackView.push("Sentence/SentenceMode.qml", {
            showMorseCode: Globals.showLetterMorse,
            inputType: Globals.eingabeart,
            leftButtonType: Globals.lefttype,
            rightButtonType: Globals.righttype
        })
    } else {
        console.log(value + " mode is not implemented yet")
    }
    }

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
        spacing: 26

        Column {
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: 8

            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: qsTr("Wie möchtest du spielen?")
                color: "#1D1D1F"
                font.family: "SF Pro Display"
                font.pixelSize: 44
                font.weight: Font.DemiBold
            }

            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: qsTr("Wähle einen Trainingsmodus.")
                color: "#6E6E73"
                font.family: "SF Pro Text"
                font.pixelSize: 18
            }
        }

        Row {
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: 22

            Repeater {
                model: [
                    {
                        title: qsTr("Buchstabe"),
                        symbol: "H",
                        value: "Letter",
                        size: 128
                    },
                    {
                        title: qsTr("Wort"),
                        symbol: "Hello",
                        value: "Word",
                        size: 58
                    },
                    {
                        title: qsTr("Satz"),
                        symbol: "Hello\nworld",
                        value: "Sentence",
                        size: 52
                    },
                    {
                        title: qsTr("Online"),
                        symbol: "⌁",
                        value: "Online",
                        size: 120
                    }
                ]

                delegate: Rectangle {
                    id: modeCard

                    required property var modelData

                    width: Math.min(270, (root.width - 190) / 4)
                    height: Math.min(410, root.height - 310)
                    radius: 28

                    color: modeMouse.pressed
                           ? "#F0F0F3"
                           : "#FFFFFF"

                    border.color: modeMouse.containsMouse
                                  ? "#AFCFFF"
                                  : "#E4E4E9"

                    border.width: modeMouse.containsMouse ? 2 : 1

                    scale: modeMouse.pressed
                           ? 0.985
                           : modeMouse.containsMouse
                             ? 1.015
                             : 1.0

                    Behavior on scale {
                        NumberAnimation {
                            duration: 150
                            easing.type: Easing.OutCubic
                        }
                    }

                    Column {
                        anchors.fill: parent
                        anchors.margins: 24
                        spacing: 18

                        Text {
                            text: modeCard.modelData.title
                            color: "#1D1D1F"
                            font.family: "SF Pro Display"
                            font.pixelSize: 24
                            font.weight: Font.DemiBold
                        }

                        Rectangle {
                            width: parent.width
                            height: parent.height - 72
                            radius: 22
                            color: "#F7F7F9"

                            Text {
                                anchors.centerIn: parent

                                text: modeCard.modelData.symbol
                                horizontalAlignment: Text.AlignHCenter

                                color: "#1D1D1F"
                                font.family: "SF Pro Display"
                                font.pixelSize: modeCard.modelData.size
                                font.weight: Font.DemiBold
                            }
                        }
                    }

                    MouseArea {
                        id: modeMouse

                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor

                        onClicked: {
                            root.selectMode(modeCard.modelData.value)
                        }
                    }
                }
            }
        }

        Rectangle {
            anchors.horizontalCenter: parent.horizontalCenter

            width: Math.min(600, root.width - 120)
            height: 82
            radius: 24
            color: "#FFFFFF"

            border.color: "#E4E4E9"
            border.width: 1

            Row {
                anchors.fill: parent
                anchors.leftMargin: 24
                anchors.rightMargin: 24
                spacing: 18

                Column {
                    anchors.verticalCenter: parent.verticalCenter
                    width: parent.width - morseSwitch.width - 18
                    spacing: 4

                    Text {
                        text: qsTr("Morsecode anzeigen")
                        color: "#1D1D1F"
                        font.family: "SF Pro Text"
                        font.pixelSize: 18
                        font.weight: Font.DemiBold
                    }

                    Text {
                        text: qsTr("Zeigt die Punkte und Striche an, die eingegeben werden müssen.")
                        color: "#6E6E73"
                        font.family: "SF Pro Text"
                        font.pixelSize: 14
                    }
                }

                Switch {
                    id: morseSwitch

                    anchors.verticalCenter: parent.verticalCenter
                    checked: Globals.showLetterMorse

                    onToggled: {
                        Globals.setShowLetterMorse(checked)
                    }
                }
            }
        }
    }
}
