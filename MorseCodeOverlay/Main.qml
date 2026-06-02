import QtQuick
import QtQuick.Controls
import QtQuick.Window
ApplicationWindow {

    //width: Screen.desktopAvailableWidth
    //height: Screen.desktopAvailableHeight
    visible: true
    visibility: Window.FullScreen
    title: "Morse Code Trainer"

    StackView {
        id: stackView
        anchors.fill: parent
        initialItem: HomePage {}

    }
}