import QtQuick
import QtQuick.Controls
import MorseCodeOverlay
import QtQuick.Window
import QtMultimedia
import "Globalvariables.js" as Globals
Item {

    visible: true
    anchors.fill: parent
    id: root
    Rectangle {
        anchors.fill: parent
        Rectangle {
            color: "#5865F2"
            x:  width / 1.25
            y: height
            width: 100
            height: 75
            radius: 50
            MouseArea {
                anchors.fill: parent
                onClicked: {
                stackView.pop()
                }
            }
            Image {
                anchors.centerIn: parent
                source: "Previousslide.png"
                width: parent.width
                height: parent.height
                fillMode: Image.PreserveAspectFit
            }
        }
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#131318" }
            GradientStop { position: 0.5; color: "#1C1D23" }
            GradientStop { position: 1.0; color: "#292B32" }
        }
        Text {
            text: qsTr("Wie möchtest du spielen?")
            font.pixelSize: 50
            color: "#7E818E"
            y: 3 * height
            x: root.width / 2 - width / 2
            id: frage
        }
        Rectangle {
            width: root.width / 5
            height: root.height - frage.y - frage.height - 80
            y: frage.y + frage.height + 40
            x: width / 8
            radius: 20
            Text {
                color: "#C9CDFB"
                x: parent.width / 2 - width / 2
                y: height
                text: qsTr("Buchstabe")
                font.pixelSize: 50
            }
            Text {
                anchors.centerIn: parent
                text: qsTr("H")
                font.pixelSize: 200
                rotation: 0
                font.bold: true
                color: "white"
                font.family: "Impact"
            }
            color: "#5865F2"
            MouseArea {
                anchors.fill: parent
                onClicked: {
                    Globals.mode = "Letter"
                    AppBridge.saveSettings(
                        Globals.eingabeart,
                        Globals.lefttype,
                        Globals.righttype,
                        Globals.mode

                    )
                }
            }
        }
        Rectangle {
            width: root.width / 5
            height: root.height - frage.y - frage.height - 80
            y: frage.y + frage.height + 40
            x: width / 8 + width / 4 + width
            radius: 20
            Text {
                color: "#C9CDFB"
                x: parent.width / 2 - width / 2
                y: height
                text: qsTr("Wort")
                font.pixelSize: 50
            }
            Text {
                anchors.centerIn: parent
                text: qsTr("Hello")
                font.pixelSize: 100
                rotation: 0
                font.bold: true
                color: "white"
                font.family: "Impact"
            }
            color: "#5865F2"
            MouseArea {
                anchors.fill: parent
                onClicked: {
                    Globals.mode = "Word"
                    AppBridge.saveSettings(
                        Globals.eingabeart,
                        Globals.lefttype,
                        Globals.righttype,
                        Globals.mode

                    )
                }
            }
        }
        Rectangle {
            width: root.width / 5
            height: root.height - frage.y - frage.height - 80
            y: frage.y + frage.height + 40
            x: width / 8 + width / 4 + width + width + width / 4
            radius: 20
            Text {
                color: "#C9CDFB"
                x: parent.width / 2 - width / 2
                y: height
                text: qsTr("Satz")
                font.pixelSize: 50
            }
            Text {
                anchors.centerIn: parent
                text: qsTr("Hello\nworld")
                font.pixelSize: 100
                rotation: 0
                font.bold: true
                color: "white"
                font.family: "Impact"
            }
        color: "#5865F2"
            MouseArea {
                anchors.fill: parent
                onClicked: {
                    Globals.mode = "Sentence"
                    AppBridge.saveSettings(
                        Globals.eingabeart,
                        Globals.lefttype,
                        Globals.righttype,
                        Globals.mode

                    )
                }
            }
        }
        Rectangle {
            width: root.width / 5
            height: root.height - frage.y - frage.height - 80
            y: frage.y + frage.height + 40
            radius: 20
            Text {
                color: "#C9CDFB"
                x: parent.width / 2 - width / 2
                y: height
                text: qsTr("Online (Zufall)")
                font.pixelSize: 49
            }
            Text {
                anchors.centerIn: parent
                text: qsTr("🌐")
                font.pixelSize: 200
                rotation: 0
                font.bold: true
                color: "white"
                font.family: "Impact"
            }
        color: "#5865F2"
            MouseArea {
                anchors.fill: parent
                onClicked: {
                    Globals.mode = "Online"
                    AppBridge.saveSettings(
                        Globals.eingabeart,
                        Globals.lefttype,
                        Globals.righttype,
                        Globals.mode

                    )
                }
            }
            x: width / 8 + width / 4 + width / 4 + width / 4 + width + width + width
        }
    }
}