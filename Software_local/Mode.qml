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
        stackView.push("LetterMode.qml", {
            showMorseCode: Globals.showLetterMorse
        })
    } else if (value === "Word") {
        console.log("Word mode is not implemented yet")
    } else if (value === "Sentence") {
        console.log("Sentence mode is not implemented yet")
    } else if (value === "Online") {
        console.log("Online mode is not implemented yet")
    }
}
    background: Rectangle {
        color: "#F5F5F7"
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#FBFBFD" }
            GradientStop { position: 1.0; color: "#EEF1F5" }
        }
    }

    Rectangle {
        x: 28; y: 24; width: 54; height: 54; radius: 27
        color: backMouse.pressed ? "#D7D7DC" : (backMouse.containsMouse ? "#E7E7EB" : "#FFFFFF")
        border.color: "#E3E3E8"
        Text { anchors.centerIn: parent; text: "‹"; color: "#1D1D1F"; font.pixelSize: 42; y: -2 }
        MouseArea { id: backMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: stackView.pop() }
    }

    Column {
        anchors.fill: parent
        anchors.margins: 54
        spacing: 34

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
                    { title: qsTr("Buchstabe"), symbol: "H", value: "Letter", size: 128 },
                    { title: qsTr("Wort"), symbol: "Hello", value: "Word", size: 58 },
                    { title: qsTr("Satz"), symbol: "Hello\nworld", value: "Sentence", size: 52 },
                    { title: qsTr("Online (Zufall)"), symbol: "⌁", value: "Online", size: 120 }
                ]

                delegate: Rectangle {
                    required property var modelData
                    width: Math.min(270, (root.width - 190) / 4)
                    height: Math.min(480, root.height - 250)
                    radius: 28
                    color: modeMouse.pressed ? "#F0F0F3" : "#FFFFFF"
                    border.color: modeMouse.containsMouse ? "#AFCFFF" : "#E4E4E9"
                    border.width: modeMouse.containsMouse ? 2 : 1
                    scale: modeMouse.pressed ? 0.985 : (modeMouse.containsMouse ? 1.015 : 1.0)
                    Behavior on scale { NumberAnimation { duration: 150; easing.type: Easing.OutCubic } }

                    Column {
                        anchors.fill: parent
                        anchors.margins: 24
                        spacing: 18

                        Text {
                            text: modelData.title
                            color: "#1D1D1F"
                            font.family: "SF Pro Display"
                            font.pixelSize: 24
                            font.weight: Font.DemiBold
                            wrapMode: Text.WordWrap
                        }

                        Rectangle {
                            width: parent.width
                            height: parent.height - 72
                            radius: 22
                            color: "#F7F7F9"

                            Text {
                                anchors.centerIn: parent
                                text: modelData.symbol
                                horizontalAlignment: Text.AlignHCenter
                                color: "#1D1D1F"
                                font.family: "SF Pro Display"
                                font.pixelSize: modelData.size
                                font.weight: Font.DemiBold
                            }
                        }
                    }

                    MouseArea {
                        id: modeMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: root.selectMode(modelData.value)
                    }
                }
            }
        }
    }
}
