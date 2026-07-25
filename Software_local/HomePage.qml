import QtQuick
import QtQuick.Controls

Page {
    id: root
    title: "HomePage"

    Rectangle {
    id: developmentModeNotice

    anchors.left: parent.left
    anchors.bottom: parent.bottom
    anchors.leftMargin: 22
    anchors.bottomMargin: 18

    visible: DevelopmentMode.enabled

    width: developmentModeText.width + 28
    height: 34
    radius: 17

    color: "#FFF4CE"
    border.color: "#E6C65C"
    border.width: 1

    opacity: visible ? 1.0 : 0.0

    Behavior on opacity {
        NumberAnimation {
            duration: 180
        }
    }

    Row {
        anchors.centerIn: parent
        spacing: 8

        Rectangle {
            width: 8
            height: 8
            radius: 4
            color: "#E5A900"
        }

        Text {
            id: developmentModeText

            text: qsTr("In development mode · F10 to exit")
            color: "#5C4A00"
            font.family: "SF Pro Text"
            font.pixelSize: 13
            font.weight: Font.Medium
        }
    }
}
    background: Rectangle {
        color: "#F5F5F7"
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#FBFBFD" }
            GradientStop { position: 1.0; color: "#EEF1F5" }
        }
    }
    Shortcut {
	sequence: "F10"
	context: Qt.ApplicationShortcut

	onActivated: {
	    DevelopmentMode.toggle()
	}
    }
    Column {
        anchors.centerIn: parent
        spacing: 32

        Column {
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: 10

            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: qsTr("Morse Code Trainer")
                color: "#1D1D1F"
                font.family: "SF Pro Display"
                font.pixelSize: 54
                font.weight: Font.DemiBold
            }

            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: qsTr("Train precision, timing, and rhythm.")
                color: "#6E6E73"
                font.family: "SF Pro Text"
                font.pixelSize: 20
            }
        }

        Rectangle {
            id: startCard
            anchors.horizontalCenter: parent.horizontalCenter
            width: 360
            height: 104
            radius: 26
            color: startMouse.pressed ? "#0068D9" : (startMouse.containsMouse ? "#1684FF" : "#007AFF")

            Behavior on color { ColorAnimation { duration: 140 } }
            scale: startMouse.pressed ? 0.98 : 1.0
            Behavior on scale { NumberAnimation { duration: 120; easing.type: Easing.OutCubic } }

            Row {
                anchors.centerIn: parent
                spacing: 14

                Text {
                    text: qsTr("Start")
                    color: "white"
                    font.family: "SF Pro Display"
                    font.pixelSize: 34
                    font.weight: Font.DemiBold
                }

                Text {
                    text: "›"
                    color: "white"
                    font.family: "SF Pro Display"
                    font.pixelSize: 46
                    y: -3
                }
            }

            MouseArea {
                id: startMouse
                anchors.fill: parent
                hoverEnabled: true
                cursorShape: Qt.PointingHandCursor
                onClicked: stackView.push("Inputtype.qml")
            }
        }
    }

    Text {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 24
        text: qsTr("Made by Paul M. and Benjamin G. under supervision of Falko S.")
        color: "#8E8E93"
        font.family: "SF Pro Text"
        font.pixelSize: 13
    }
}
