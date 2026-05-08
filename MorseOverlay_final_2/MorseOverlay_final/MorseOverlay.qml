// MorseOverlay.qml — root UI, keyboard handler, layout
import QtQuick
import QtQuick.Controls

Item {
    id: root
    focus: true

    // ── Colours (matching Python constants) ───────────────────
    readonly property color C_BLACK:  "#0a0a19"
    readonly property color C_WHITE:  "#f0f0f0"
    readonly property color C_GRAY:   "#3c3c3c"
    readonly property color C_LGRAY:  "#787878"
    readonly property color C_ACCENT: "#50a0dc"
    readonly property color C_GREEN:  "#50c878"
    readonly property color C_AMBER:  "#dcaa32"
    readonly property color C_RED:    "#dc5050"
    readonly property color C_DARK:   "#14141a"
    readonly property color C_PANEL:  "#1c1c23"
    readonly property color C_BORDER: "#323241"

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
        case Qt.Key_Escape:   Qt.quit();               break
        case Qt.Key_C:        logic.showConfig = !logic.showConfig; break
        case Qt.Key_Tab:      logic.cycleMode();        break
        case Qt.Key_I:        logic.toggleInputMode();  break
        case Qt.Key_Space:    logic.commitChar();        break
        case Qt.Key_Return:
        case Qt.Key_Enter:    logic.commitChar(); logic.commitWord(); break
        case Qt.Key_Backspace: logic.backspace(); break
        case Qt.Key_Left:     logic.addSignal(cfg.left);  break
        case Qt.Key_Right:    logic.addSignal(cfg.right); break
        }
    }

    // ── Layout ────────────────────────────────────────────────
    Rectangle {
        anchors.fill: parent
        color: C_DARK

        // Top bar
        TopBar {
            id: topBar
            width: parent.width
            height: 44
            logic: logic
            cPanel: C_PANEL; cBorder: C_BORDER
            cAccent: C_ACCENT; cLgray: C_LGRAY
        }

        // Main output display
        MainDisplay {
            id: mainDisplay
            x: 30; y: 60
            width: 540; height: 280
            logic: logic
            cPanel: C_PANEL; cBorder: C_BORDER
            cWhite: C_WHITE; cGreen: C_GREEN
            cLgray: C_LGRAY; cAmber: C_AMBER
            flashAnim: flashAnim
        }

        // Mode selector panel (right)
        ModeBar {
            id: modeBar
            x: 590; y: 60
            width: 280; height: 280
            logic: logic
            cPanel: C_PANEL; cBorder: C_BORDER
            cAccent: C_ACCENT; cGreen: C_GREEN
            cAmber: C_AMBER;   cRed: C_RED
            cGray: C_GRAY;     cLgray: C_LGRAY
            cWhite: C_WHITE
        }

        // Current sequence display
        SeqDisplay {
            id: seqDisplay
            x: 30; y: 360
            width: 540; height: 80
            logic: logic
            cPanel: C_PANEL; cBorder: C_BORDER
            cAccent: C_ACCENT; cAmber: C_AMBER
            cGray: C_GRAY;     cLgray: C_LGRAY
        }

        // Key hints
        KeyHints {
            id: keyHints
            x: 30; y: 455
            width: 840; height: 120
            logic: logic
            cAccent: C_ACCENT; cAmber: C_AMBER
            cWhite: C_WHITE;   cRed: C_RED
            cGreen: C_GREEN;   cLgray: C_LGRAY
        }
    }

    // ── Flash animation (shared) ──────────────────────────────
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
        x: 30 + 540 - 70; y: 60 + 10
        width: 60; height: 60
        radius: 8
        color: root.C_GREEN
        opacity: 0

        Text {
            anchors.centerIn: parent
            text: logic.flashChar
            font.family: "Courier New"
            font.pixelSize: 24
            color: "white"
        }
    }

    // ── Config panel overlay ──────────────────────────────────
    ConfigPanel {
        anchors.fill: parent
        visible: logic.showConfig
        logic: logic
        cPanel: C_PANEL; cAccent: C_ACCENT
        cGreen: C_GREEN; cGray: C_GRAY
        cWhite: C_WHITE; cLgray: C_LGRAY
    }
}
