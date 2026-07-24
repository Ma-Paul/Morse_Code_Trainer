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
        x: 28; y: 24; width: 54; height: 54; radius: 27
        color: backMouse.pressed ? "#D7D7DC" : (backMouse.containsMouse ? "#E7E7EB" : "#FFFFFF")
        border.color: "#E3E3E8"
        Text { anchors.centerIn: parent; text: "‹"; color: "#1D1D1F"; font.pixelSize: 42; y: -2 }
        MouseArea { id: backMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: stackView.pop() }
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
                model: [qsTr("Links"), qsTr("Rechts")]
                delegate: Rectangle {
                    required property int index
                    required property string modelData
                    width: Math.min(430, (root.width - 190) / 2)
                    height: Math.min(570, root.height - 245)
                    radius: 30
                    color: "#FFFFFF"
                    border.color: "#E4E4E9"

                    Column {
                        anchors.fill: parent
                        anchors.margins: 26
                        spacing: 18

                        Text {
                            text: modelData
                            color: "#1D1D1F"
                            font.family: "SF Pro Display"
                            font.pixelSize: 30
                            font.weight: Font.DemiBold
                        }

                        ComboBox {
                            id: chooser
                            width: parent.width
                            height: 48
                            model: ["Pause", "Lang", "Kurz", "Zeitgesteuert"]
                            font.pixelSize: 17
                            onActivated: {
                                if (index === 0)
                                    Globals.lefttype = currentText
                                else
                                    Globals.righttype = currentText
                            }
                            Component.onCompleted: {
                                if (index === 0) Globals.lefttype = currentText
                                else Globals.righttype = currentText
                            }
                        }

                        Rectangle {
                            width: parent.width
                            height: parent.height - 110
                            radius: 22
                            color: "#F7F7F9"
                            clip: true

                            Image {
                                anchors.fill: parent
                                anchors.margins: 34
                                source: chooser.currentText === "Lang" ? "Long.png"
                                      : chooser.currentText === "Kurz" ? "short.png"
                                      : chooser.currentText === "Zeitgesteuert" ? "Time.png"
                                      : "Pause.png"
                                fillMode: Image.PreserveAspectFit
                                smooth: true
                                mipmap: true
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
        color: nextMouse.pressed ? "#0068D9" : (nextMouse.containsMouse ? "#1684FF" : "#007AFF")
        scale: nextMouse.pressed ? 0.98 : 1
        Behavior on scale { NumberAnimation { duration: 120 } }

        Row {
            anchors.centerIn: parent
            spacing: 10
            Text { text: qsTr("Weiter"); color: "white"; font.pixelSize: 20; font.weight: Font.DemiBold }
            Text { text: "›"; color: "white"; font.pixelSize: 31; y: -2 }
        }

        MouseArea {
            id: nextMouse
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
            onClicked: stackView.push("Mode.qml")
        }
    }
}
