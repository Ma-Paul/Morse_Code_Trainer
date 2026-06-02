import QtQuick
import QtQuick.Controls
import MorseCodeOverlay
import QtQuick.Window
import QtMultimedia
import "Globalvariables.js" as Globals
Item {
    id: root
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
            font.pixelSize: 50
            x: root.width / 2 - width / 2
            y: 3 * height
            text: qsTr("Was sind die Einstellungen deiner Knöpfe?")
            color: "white"
        }
        Rectangle {
            id: links
            x: root.width / 12
            y: frage.y + frage.height + (root.height - frage.height - frage.y) / 2 - height / 2
            width: root.width / 3
            height: root.height - frage.y - frage.height * 3
            radius: 20
            Text {
                x: links.width / 2 - width / 2
                y: height / 5
                text: qsTr("Links")
                font.pixelSize: 60
                id: textforlinks
            }
            ComboBox {
                id: choose
                x: parent.width / 2 - width / 2
                y: textforlinks.height + 10 + textforlinks.y
                width: links.width - 2 * 30
                model: ["Pause", "Lang", "Kurz", "Zeitgesteuert"]
                onActivated: {
                    Globals.lefttype = currentText

                }
            Image {
                source: choose.currentText === "Lang"
                    ? "Long.png"
                    : choose.currentText === "Kurz"
                    ? "short.png"
                    : choose.currentText === "Zeitgesteuert"
                    ? "Time.png"
                    : "Pause.jpg"

                x: 10
                y: choose.height * 2
                width: parent.width - 20
                height: width
                }
            }
        }

        Rectangle {
            id: rechts
            x: root.width / 12 + root.width / 2
            y: frage.y + frage.height + (root.height - frage.height - frage.y) / 2 - height / 2
            width: root.width / 3
            height: root.height - frage.y - frage.height * 3
            radius: 20
            Text {
                x: rechts.width / 2 - width / 2
                y: height / 5
                text: qsTr("Rechts")
                font.pixelSize: 60
                id: textforrechts
            }
            ComboBox {
                id: choose2
                x: parent.width / 2 - width / 2
                y: textforrechts.height + 10 + textforlinks.y
                width: rechts.width - 2 * 30
                model: ["Pause", "Lang", "Kurz", "Zeitgesteuert"]
                onActivated: {
                    Globals.righttype = currentText

                }
            Image {
                source: choose2.currentText === "Lang"
                    ? "Long.png"
                    : choose2.currentText === "Kurz"
                    ? "short.png"
                    : choose2.currentText === "Zeitgesteuert"
                    ? "Time.png"
                    : "Pause.jpg"

                x: 10
                y: choose2.height * 2
                width: parent.width - 20
                height: width
                }
            }
        }

        Rectangle {
            x: rechts.x - root.width / 12 - width / 2
            y: rechts.height / 2 - height / 2 + rechts.y
            width: rechts.x - links.width - links.x - 30
            height: width
            color: "Blue"
            radius: 20
            id: weiter
            MouseArea {
                anchors.fill: parent
                onClicked: {
                    stackView.push("Mode.qml")
                }
            }
            Image {
                anchors.centerIn: parent
                source: "Nextslide.png"
                width: weiter.width
                height: weiter.height
                fillMode: Image.PreserveAspectFit
            }
        }
    }
}