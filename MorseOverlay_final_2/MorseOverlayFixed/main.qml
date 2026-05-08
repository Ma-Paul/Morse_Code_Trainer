import QtQuick
import QtQuick.Controls
import QtQuick.Window

ApplicationWindow {
    id: window
    width: 900
    height: 600
    minimumWidth: 900
    minimumHeight: 600
    visible: true
    title: "Binäreingabe Overlay"
    color: "#0a0a0f"

    MorseOverlay {
        anchors.fill: parent
    }
}
