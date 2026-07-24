import QtQuick
import QtQuick.Controls
import QtQuick.Window

ApplicationWindow {
    visible: true
    visibility: Window.FullScreen
    title: "Morse Code Trainer"
    color: "#F5F5F7"

    StackView {
        id: stackView
        anchors.fill: parent
        initialItem: HomePage {}

        pushEnter: Transition {
            ParallelAnimation {
                NumberAnimation { property: "opacity"; from: 0; to: 1; duration: 220; easing.type: Easing.OutCubic }
                NumberAnimation { property: "x"; from: stackView.width * 0.035; to: 0; duration: 220; easing.type: Easing.OutCubic }
            }
        }
        pushExit: Transition { NumberAnimation { property: "opacity"; from: 1; to: 0.82; duration: 180 } }
        popEnter: Transition { NumberAnimation { property: "opacity"; from: 0.82; to: 1; duration: 180 } }
        popExit: Transition {
            ParallelAnimation {
                NumberAnimation { property: "opacity"; from: 1; to: 0; duration: 200; easing.type: Easing.InCubic }
                NumberAnimation { property: "x"; from: 0; to: stackView.width * 0.035; duration: 200; easing.type: Easing.InCubic }
            }
        }
    }
}
