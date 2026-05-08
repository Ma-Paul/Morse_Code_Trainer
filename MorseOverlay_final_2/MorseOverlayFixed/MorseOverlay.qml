// MorseOverlay.qml — root UI, keyboard handler, layout
import QtQuick
import QtQuick.Controls

Item {
    id: root
    focus: true

    // ── Colours ───────────────────────────────────────────────
    readonly property color cBlack:  "#0a0a19"
    readonly property color cWhite:  "#f0f0f0"
    readonly property color cGray:   "#3c3c3c"
    readonly property color cLgray:  "#787878"
    readonly property color cAccent: "#50a0dc"
    readonly property color cGreen:  "#50c878"
    readonly property color cAmber:  "#dcaa32"
    readonly property color cRed:    "#dc5050"
    readonly property color cDark:   "#14141a"
    readonly property color cPanel:  "#1c1c23"
    readonly property color cBorder: "#323241"

    // ── Logic ─────────────────────────────────────────────────
    MorseLogic {
        id: logic
        onCharFlash: (ch) => flashAnim.restart()
    }

    Timer {
        interval: 100
        running: true
        repeat: true
        onTriggered: logic.tick()
    }

    // ── Keyboard input ────────────────────────────────────────
    Keys.onPressed: (event) => {
        event.accepted = true
        var cfg = logic.currentConfig()

        if (logic.showConfig) {
            if (event.key === Qt.Key_C || event.key === Qt.Key_Escape)
                logic.showConfig = false
            else if (event.key === Qt.Key_1) logic.keyConfigIdx = 0
            else if (event.key === Qt.Key_2) logic.keyConfigIdx = 1
            else if (event.key === Qt.Key_3 && logic.inputMode === logic.input2key)
                logic.keyConfigIdx = 2
            return
        }

        switch (event.key) {
        case Qt.Key_Escape:    Qt.quit();                          break
        case Qt.Key_C:         logic.showConfig = !logic.showConfig; break
        case Qt.Key_Tab:       logic.cycleMode();                  break
        case Qt.Key_I:         logic.toggleInputMode();            break
        case Qt.Key_Space:     logic.commitChar();                 break
        case Qt.Key_Return:
        case Qt.Key_Enter:     logic.commitChar(); logic.commitWord(); break
        case Qt.Key_Backspace: logic.backspace();                  break
        case Qt.Key_Left:      logic.addSignal(cfg.left);         break
        case Qt.Key_Right:     logic.addSignal(cfg.right);        break
        }
    }

    // ── Background ────────────────────────────────────────────
    Rectangle {
        anchors.fill: parent
        color: cDark

        TopBar {
            width: parent.width
            height: 44
            logic: logic
            panelColor: cPanel
            borderColor: cBorder
            accentColor: cAccent
            lgrayColor: cLgray
        }

        MainDisplay {
            x: 30; y: 60
            width: 540; height: 280
            logic: logic
            panelColor: cPanel
            borderColor: cBorder
            whiteColor: cWhite
            greenColor: cGreen
            lgrayColor: cLgray
            amberColor: cAmber
        }

        ModeBar {
            x: 590; y: 60
            width: 280; height: 280
            logic: logic
            panelColor: cPanel
            borderColor: cBorder
            accentColor: cAccent
            greenColor: cGreen
            amberColor: cAmber
            redColor: cRed
            grayColor: cGray
            lgrayColor: cLgray
            whiteColor: cWhite
        }

        SeqDisplay {
            x: 30; y: 360
            width: 540; height: 80
            logic: logic
            panelColor: cPanel
            borderColor: cBorder
            accentColor: cAccent
            amberColor: cAmber
            grayColor: cGray
            lgrayColor: cLgray
        }

        KeyHints {
            x: 30; y: 455
            width: 840; height: 120
            logic: logic
            accentColor: cAccent
            amberColor: cAmber
            whiteColor: cWhite
            redColor: cRed
            greenColor: cGreen
            lgrayColor: cLgray
        }
    }

    // ── Flash animation ───────────────────────────────────────
    SequentialAnimation {
        id: flashAnim
        PropertyAnimation {
            target: flashRect
            property: "opacity"
            from: 1; to: 0
            duration: 600
            easing.type: Easing.OutQuad
        }
    }

    Rectangle {
        id: flashRect
        x: 500; y: 70
        width: 60; height: 60
        radius: 8
        color: cGreen
        opacity: 0

        Text {
            anchors.centerIn: parent
            text: logic.flashChar
            font.family: "Courier New"
            font.pixelSize: 24
            color: "white"
        }
    }

    // ── Config overlay ────────────────────────────────────────
    ConfigPanel {
        anchors.fill: parent
        visible: logic.showConfig
        logic: logic
        panelColor: cPanel
        accentColor: cAccent
        greenColor: cGreen
        grayColor: cGray
        whiteColor: cWhite
        lgrayColor: cLgray
    }
}
