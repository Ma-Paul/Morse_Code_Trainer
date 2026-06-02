//TODO: Fix Sources for Images
import QtQuick
import QtQuick.Controls
import MorseCodeOverlay
import QtQuick.Window
import "Globalvariables.js" as Globals
Page {
    Item {
        id: root
        width: Screen.desktopAvailableWidth
        height: Screen.desktopAvailableHeight
        Rectangle {
            anchors.fill: parent
            gradient: Gradient {

                GradientStop {
                    position: 0.0
                    color: "#000000"
                }
                GradientStop {
                    position: 0.25
                    color: "#000000"
                }
                GradientStop {
                    position: 1.0
                    color: "#ffffff"
                }
            }
            Rectangle {
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
            Text {
                id: frage
                x: parent.width / 2 - width / 2
                y: 3 * height

                text: qsTr("Welche Art der Eingabe besitzt du?")
                font.pixelSize: 50
                color: "white"
            }
            Rectangle {
                radius: 20
                width: root.width / 3
                height: root.height - frage.x - 20
                //y: frage.y + frage.height + (root.height / 2 - frage.y) - height / 2
                y: frage.y + frage.height + (root.height - frage.y - frage.height) / 2 - height / 2
                x: root.width / 4 - width / 2

                Text {
                    x: parent.width / 2 - width / 2
                    y: 1.5 * height
                    text: qsTr("Eine Taste")
                    font.pixelSize: 50
                }
                Image {
                    x: parent.width / 2 - width / 2
                    y: 181
                    width: 238
                    height: 238
                    source: "Single.jpg"
                }
                MouseArea {
                    anchors.fill: parent
                    onClicked: {
                        Globals.eingabeart = "1"
                        stackView.push("Mode.qml")
                    }

                }
            }

            Rectangle {
                radius: 20
                width: root.width / 3
                height: root.height - frage.x - 20
                y: frage.y + frage.height + (root.height - frage.y - frage.height) / 2 - height / 2
                x: root.width / 4 - width / 2 + root.width / 2
                Text {
                    x: parent.width / 2 - width / 2
                    y: 1.5 * height
                    text: qsTr("Zwei Tasten")
                    font.pixelSize: 50
                }
                Image {

                    width: 238

                    height: 238
                    x: parent.width / 2 - width / 2
                    y: 181
                    source: "Double.jpg"
                }
                MouseArea {
                    anchors.fill: parent
                    onClicked: {
                        Globals.eingabeart = "2"
                        stackView.push("Specifytype.qml")
                    }
                }
            }
        }
    }

}
