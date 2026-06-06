import QtQuick
import QtQuick.Controls
import MorseCodeOverlay
import QtQuick.Window
Page {
    title: "HomePage"
    //width: Screen.desktopAvailableWidth
   // height: Screen.desktopAvailableHeight
    visible: true
    anchors.fill: parent
    Rectangle {
        id: bekguaund
        visible: true
        width: parent.width
        height: parent.height
        gradient: Gradient {

                GradientStop { position: 0.0; color: "#7A8B8B" }
                GradientStop { position: 0.25; color: "#7A8B8B" }
                GradientStop { position: 1.0; color: "#68838B" }

            }




        Text {
            id: text1
            x: parent.width / 2 - width / 2
            y: 3 * height
            text: qsTr("Morse Code Trainer")
            font.pixelSize: 50
            color: "white"


        }

        Text {
            id: text2
            x: 15
            y: parent.height - (15 + height)
            text: qsTr("Made by Paul M. and Benjamin G. under Supervision of Falko S.")
            font.pixelSize: 12
        }

        Rectangle {
            id: rectangle
            x: parent.width / 2 - width / 2
            y: parent.height / 2 - height / 2
            width: 200
            height: 100
	    color: "4169E1"                
            radius: 20
            MouseArea {
                anchors.fill: parent
                onClicked: stackView.push("Inputtype.qml")
            }
            Text {
                        id: starttext
                        x: parent.width / 2 - width / 2
                        y: parent.height / 2 - height / 2
                        text: qsTr("Start")
                        font.pixelSize: 50
                    }
        }
    }
}
