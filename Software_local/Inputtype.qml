import QtQuick
import QtQuick.Controls
import "Globalvariables.js" as Globals

Page {
    id: root

    background: Rectangle {
        color: "#F5F5F7"
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#FBFBFD" }
            GradientStop { position: 1.0; color: "#EEF1F5" }
        }
    }

    Rectangle {
        id: backButton
        x: 28
        y: 24
        width: 54
        height: 54
        radius: 27
        color: backMouse.pressed ? "#D7D7DC" : (backMouse.containsMouse ? "#E7E7EB" : "#FFFFFF")
        border.color: "#E3E3E8"
        border.width: 1

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
            onClicked: stackView.pop()
        }
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
                text: qsTr("Welche Art der Eingabe besitzt du?")
                color: "#1D1D1F"
                font.family: "SF Pro Display"
                font.pixelSize: 44
                font.weight: Font.DemiBold
            }

            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: qsTr("Wähle dein Morse-Eingabegerät.")
                color: "#6E6E73"
                font.family: "SF Pro Text"
                font.pixelSize: 18
            }
        }

        Row {
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: 34

            Repeater {
                model: [
                    { title: qsTr("Eine Taste"), subtitle: qsTr("Klassische Handtaste"), image: "Single.png", value: "1", target: "Mode.qml" },
                    { title: qsTr("Zwei Tasten"), subtitle: qsTr("Doppel- oder Paddle-Taste"), image: "Double.png", value: "2", target: "Specifytype.qml" }
                ]

                delegate: Rectangle {
                    required property var modelData
                    width: Math.min(470, (root.width - 150) / 2)
                    height: Math.min(560, root.height - 240)
                    radius: 30
                    color: cardMouse.pressed ? "#F0F0F3" : "#FFFFFF"
                    border.color: cardMouse.containsMouse ? "#AFCFFF" : "#E4E4E9"
                    border.width: cardMouse.containsMouse ? 2 : 1
                    scale: cardMouse.pressed ? 0.985 : (cardMouse.containsMouse ? 1.01 : 1.0)

                    Behavior on scale { NumberAnimation { duration: 150; easing.type: Easing.OutCubic } }
                    Behavior on border.color { ColorAnimation { duration: 150 } }

                    Column {
                        anchors.fill: parent
                        anchors.margins: 28
                        spacing: 18

                        Text {
                            text: modelData.title
                            color: "#1D1D1F"
                            font.family: "SF Pro Display"
                            font.pixelSize: 30
                            font.weight: Font.DemiBold
                        }

                        Text {
                            text: modelData.subtitle
                            color: "#6E6E73"
                            font.family: "SF Pro Text"
                            font.pixelSize: 16
                        }

                        Rectangle {
                            width: parent.width
                            height: parent.height - 112
                            radius: 22
                            color: "#F7F7F9"
                            clip: true

                            Image {
                                anchors.fill: parent
                                anchors.margins: 20
                                source: modelData.image
                                fillMode: Image.PreserveAspectFit
                                smooth: true
                                mipmap: true
                            }
                        }
                    }

                    MouseArea {
                        id: cardMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            Globals.eingabeart = modelData.value
                            stackView.push(modelData.target)
                        }
                    }
                }
            }
        }
    }
}
