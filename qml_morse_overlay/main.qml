import QtQuick 2.15
import QtQuick.Controls 2.15

ApplicationWindow {
    id: root
    width: 1280
    height: 720
    visible: true
    flags: Qt.FramelessWindowHint | Qt.Window
    color: dark
    title: "Binäreingabe Overlay"

    readonly property color dark: "#0e0e12"
    readonly property color panel: "#181820"
    readonly property color panel2: "#20202c"
    readonly property color borderColor: "#37374b"
    readonly property color accent: "#5aa0e6"
    readonly property color green: "#50cd78"
    readonly property color amber: "#dcaf37"
    readonly property color red: "#d75550"
    readonly property color white: "#ebebf0"
    readonly property color lgray: "#828296"
    readonly property color gray: "#414150"

    property int panelIndex: 0
    property int numKeys: 1
    property int keyConfig: 0
    property int mode: 0
    property string seq: ""
    property string word: ""
    property string output: ""
    property string decoded: ""
    property double lastT: 0
    readonly property double charTo: 1.3
    readonly property double wordTo: 2.5
    property string flashCh: ""
    property double flashA: 0
    property string status: ""
    property double statusT: 0
    property double slideX: 0
    property int slideDir: 1
    property bool sliding: false

    property string testSeq: ""
    property bool testDone: false
    property bool testError: false
    property double testErrorT: 0
    property double testSuccessT: 0

    property bool leftHeld: false
    property bool rightHeld: false
    property double chordPressT: 0
    property bool chordActive: false
    readonly property double chordLongT: 0.4

    readonly property var morseTable: ({
        ".-":"A", "-...":"B", "-.-.":"C", "-..":"D", ".":"E",
        "..-.":"F", "--.":"G", "....":"H", "..":"I", ".---":"J",
        "-.-":"K", ".-..":"L", "--":"M", "-.":"N", "---":"O",
        ".--.":"P", "--.-":"Q", ".-.":"R", "...":"S", "-":"T",
        "..-":"U", "...-":"V", ".--":"W", "-..-":"X", "-.--":"Y",
        "--..":"Z", "-----":"0", "----":"1", "..---":"2", "...--":"3",
        "....-":"4", ".....":"5", "-....":"6", "--...":"7", "---..":"8", "----.":"9",
        ".-.-.-":".", "--..--":",", "..--..":"?"
    })
    readonly property var modeNames: ["Buchstabe", "Wort", "Satz", "Online"]
    readonly property var modeDescs: ["Ein Zeichen\npro Schritt", "Ein Wort\naufbauen", "Vollstaendige\nSaetze", "Online-\nModus"]
    readonly property var modeColors: [accent, green, amber, red]
    readonly property var keyConfigNames: ["Links lang / Rechts kurz", "Links kurz / Rechts lang", "Beide: normale Eingabe"]
    readonly property var refs: [["A",".-"],["E","."],["I",".."],["M","--"],["N","-."],["O","---"],["S","..."],["T","-"],["U","..-"],["R",".-."]]

    function nowSec() { return Date.now() / 1000.0 }
    function leftSig() { return keyConfig === 0 ? "-" : "." }
    function rightSig() { return keyConfig === 0 ? "." : "-" }
    function lookup(s) { return morseTable[s] !== undefined ? morseTable[s] : "?" }
    function nextPanel(current) {
        if (current === 0) return numKeys === 1 ? 2 : 1
        if (current === 1) return 2
        if (current === 2) return 3
        if (current === 3) return 4
        return current
    }
    function prevPanel(current) {
        if (current === 4) return 3
        if (current === 3) return 2
        if (current === 2) return numKeys === 1 ? 0 : 1
        if (current === 1) return 0
        return current
    }
    function go(target) {
        if (target < 0 || target > 4) return
        if (target === 0) numKeys = 1
        if (target === 2) {
            testSeq = ""; testDone = false; testError = false
            leftHeld = false; rightHeld = false; chordActive = false
        }
        slideDir = target > panelIndex ? 1 : -1
        panelIndex = target
        slideX = width * slideDir
        sliding = true
    }
    function goNext() { go(nextPanel(panelIndex)) }
    function goBack() { go(prevPanel(panelIndex)) }
    function targetSeq() { return ".-" }
    function addSig(s) { seq += s; lastT = nowSec(); decoded = lookup(seq) }
    function commitChar() {
        if (seq.length === 0) return
        var ch = morseTable[seq] !== undefined ? morseTable[seq] : ""
        if (ch.length > 0) {
            flashCh = ch; flashA = 255
            if (mode === 0) output = ch
            else { word += ch; output = word }
        } else {
            status = "Unbekannt: " + seq; statusT = nowSec()
        }
        seq = ""; decoded = ""
    }
    function commitWord() {
        if (mode >= 2) { output = word + " "; word = "" }
        else if (mode === 1) { output = word; word = "" }
    }
    function backspace() {
        if (seq.length > 0) { seq = seq.slice(0, -1); decoded = seq.length ? lookup(seq) : "" }
        else if (word.length > 0) { word = word.slice(0, -1); output = word }
        else if (output.length > 0) output = output.slice(0, -1)
    }
    function testKey(sig) {
        if (testDone) return
        var target = targetSeq()
        var expected = testSeq.length < target.length ? target[testSeq.length] : null
        if (expected === null) return
        if (sig === expected) {
            testSeq += sig; testError = false
            if (testSeq === target) { testDone = true; testSuccessT = nowSec() }
        } else { testError = true; testErrorT = nowSec(); testSeq = "" }
    }
    function testChordDown(key) {
        if (testDone) return
        if (key !== Qt.Key_Left && key !== Qt.Key_Right) return
        if (!chordActive) { chordActive = true; chordPressT = nowSec() }
        if (key === Qt.Key_Left) leftHeld = true
        if (key === Qt.Key_Right) rightHeld = true
    }
    function testChordUp(key) {
        if (testDone || !chordActive) return
        if (key !== Qt.Key_Left && key !== Qt.Key_Right) return
        if (key === Qt.Key_Left) leftHeld = false
        if (key === Qt.Key_Right) rightHeld = false
        if (!leftHeld && !rightHeld) {
            var duration = nowSec() - chordPressT
            var sig = duration >= chordLongT ? "-" : "."
            chordActive = false
            testKey(sig)
        }
    }
    function modeColor(i) { return modeColors[i] }

    Timer {
        interval: 16; running: true; repeat: true
        property double prev: Date.now() / 1000.0
        onTriggered: {
            var n = nowSec(); var dt = n - prev; prev = n
            if (seq.length > 0 && (n - lastT) > charTo) commitChar()
            if (mode >= 2 && word.length > 0 && seq.length === 0 && (n - lastT) > wordTo) commitWord()
            if (flashA > 0) flashA = Math.max(0, flashA - dt * 220)
            if (status.length > 0 && (n - statusT) > 3) status = ""
            if (testError && (n - testErrorT) > 0.8) testError = false
            if (testDone && !sliding && (n - testSuccessT) > 1.2) { goNext(); testDone = false }
            if (sliding) {
                var speed = width * dt * 7
                if (slideDir === 1) slideX = Math.max(0, slideX - speed)
                else slideX = Math.min(0, slideX + speed)
                if (Math.abs(slideX) < 2) { slideX = 0; sliding = false }
            }
            iconCanvas.requestPaint(); seqCanvas.requestPaint(); inputCanvas.requestPaint()
        }
    }

    Item {
        id: stage
        anchors.fill: parent
        focus: true
        Keys.onPressed: function(event) {
            if (sliding) return
            if (event.key === Qt.Key_Q && (event.modifiers & Qt.ControlModifier)) Qt.quit()
            if (panelIndex === 4) {
                if (event.key === Qt.Key_Escape) goBack()
                else if (event.key === Qt.Key_Space) commitChar()
                else if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter) { commitChar(); commitWord() }
                else if (event.key === Qt.Key_Backspace) backspace()
                else if (event.key === Qt.Key_Left) addSig(leftSig())
                else if (event.key === Qt.Key_Right) addSig(rightSig())
            } else if (panelIndex === 2) {
                if (event.key === Qt.Key_Escape) goBack()
                else if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter) goNext()
                else if (numKeys === 1) testChordDown(event.key)
                else if (event.key === Qt.Key_Left) testKey(leftSig())
                else if (event.key === Qt.Key_Right) testKey(rightSig())
            } else {
                if (event.key === Qt.Key_Escape) { if (panelIndex > 0) goBack(); else Qt.quit() }
                else if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter) goNext()
            }
            event.accepted = true
        }
        Keys.onReleased: function(event) {
            if (sliding) return
            if (panelIndex === 2 && numKeys === 1) testChordUp(event.key)
            event.accepted = true
        }

        MouseArea { anchors.fill: parent; onClicked: stage.forceActiveFocus() }

        Item { id: clipper; x: 60; y: 55; width: root.width - 120; height: root.height - 65; clip: true
            Item { id: panelContent; x: slideX; anchors.top: parent.top; width: root.width - 120; height: root.height - 65
                Loader { anchors.fill: parent; sourceComponent: [p0,p1,p2,p3,p4][panelIndex] }
            }
        }

        Component { id: p0
            Item {
                property real cx: root.width/2 - 60
                AppText { text: "Wie viele Tasten?"; size: 32; bold: true; color: white; x: cx-width/2; y: 72 }
                AppText { text: "Wähle deine Eingabemethode"; size: 16; color: lgray; x: cx-width/2; y: 115 }
                Repeater { model: 2
                    Rectangle { width: 200; height: 100; radius: 12; x: cx-230+index*260; y: 145; color: numKeys === index+1 ? accent : (ma.containsMouse ? gray : panel2); border.color: accent; border.width: numKeys === index+1 ? 2 : 1
                        MouseArea { id: ma; anchors.fill: parent; hoverEnabled: true; onClicked: { numKeys=index+1; goNext() } }
                        IconCanvas { anchors.horizontalCenter: parent.horizontalCenter; y: 14; w: 36; h: 36; iconMode: index; iconColor: numKeys === index+1 ? white : accent }
                        AppText { text: index===0 ? "1 Taste" : "2 Tasten"; size: 16; color: white; anchors.horizontalCenter: parent.horizontalCenter; y: 50 }
                        AppText { text: index===0 ? "← oder →" : "← und →"; size: 13; color: numKeys === index+1 ? white : lgray; anchors.horizontalCenter: parent.horizontalCenter; y: 74 }
                    }
                }
                AppText { text: "Klicke eine Option an oder drücke Weiter →"; size: 13; color: lgray; x: cx-width/2; y: 288 }
            }
        }

        Component { id: p1
            Item { property real cx: root.width/2 - 60
                AppText { text: "Tastenbelegung"; size: 32; bold: true; color: white; x: cx-width/2; y: 32 }
                AppText { text: "Wie ist Links/Rechts belegt?"; size: 16; color: lgray; x: cx-width/2; y: 75 }
                Repeater { model: 3
                    Rectangle { width: 640; height: 82; radius: 8; x: cx-320; y: 115+index*100; color: keyConfig===index ? accent : (ma.containsMouse ? gray : panel2); border.color: keyConfig===index ? accent : borderColor; border.width: keyConfig===index ? 2 : 1
                        property string lv: index===0 ? "-" : "."; property string rv: index===0 ? "." : "-"
                        MouseArea { id: ma; anchors.fill: parent; hoverEnabled: true; onClicked: { keyConfig=index; goNext() } }
                        AppText { text: "←  " + (lv==="-" ? "LANG (−)" : "KURZ (.)") + "     |     →  " + (rv==="-" ? "LANG (−)" : "KURZ (.)"); size: 16; color: white; anchors.horizontalCenter: parent.horizontalCenter; y: 20 }
                        AppText { text: keyConfigNames[index]; size: 13; color: keyConfig===index ? white : lgray; anchors.horizontalCenter: parent.horizontalCenter; y: 46 }
                    }
                }
                AppText { text: "Klicke eine Belegung oder drücke Weiter →"; size: 13; color: lgray; x: cx-width/2; y: 418 }
            }
        }

        Component { id: p2
            FunctionTestPanel { panelXOffset: 0 }
        }

        Component { id: p3
            Item { property real cx: root.width/2 - 60
                AppText { text: "Modus wählen"; size: 32; bold: true; color: white; x: cx-width/2; y: 32 }
                AppText { text: "Was möchtest du eingeben?"; size: 16; color: lgray; x: cx-width/2; y: 75 }
                Repeater { model: 4
                    Rectangle { width: 200; height: 190; radius: 12; x: cx - (4*200+3*26)/2 + index*226; y: 125; color: mode===index ? modeColor(index) : (ma.containsMouse ? gray : panel2); border.color: modeColor(index); border.width: mode===index ? 2 : 1
                        MouseArea { id: ma; anchors.fill: parent; hoverEnabled: true; onClicked: { mode=index; goNext() } }
                        IconCanvas { anchors.horizontalCenter: parent.horizontalCenter; y: 38; w: 60; h: 60; iconMode: index; iconColor: mode===index ? white : modeColor(index) }
                        AppText { text: modeNames[index]; size: 16; color: white; anchors.horizontalCenter: parent.horizontalCenter; y: 109 }
                        AppText { text: modeDescs[index]; size: 13; color: mode===index ? white : lgray; horizontalAlignment: Text.AlignHCenter; anchors.horizontalCenter: parent.horizontalCenter; y: 134 }
                    }
                }
                AppText { text: "Klicke einen Modus oder drücke Weiter →"; size: 13; color: lgray; x: cx-width/2; y: 348 }
            }
        }

        Component { id: p4
            InputPanel {}
        }

        ProgressBarCustom { anchors.top: parent.top; anchors.horizontalCenter: parent.horizontalCenter; y: 12 }
        ArrowButton { visible: !sliding && panelIndex > 0; x: 14; y: root.height/2-32; direction: -1; onClicked: goBack() }
        ArrowButton { visible: !sliding && panelIndex < 4; x: root.width-58; y: root.height/2-32; direction: 1; onClicked: goNext() }
        AppText { visible: status.length > 0; text: status; size: 16; color: red; anchors.horizontalCenter: parent.horizontalCenter; y: root.height-32 }
    }

    component AppText: Text { font.family: "Menlo, Monaco, monospace"; font.pixelSize: size; property int size: 16; property bool bold: false; font.bold: bold; color: white; renderType: Text.NativeRendering }

    component ArrowButton: Rectangle { signal clicked(); property int direction: 1; width: 44; height: 64; radius: 6; color: ma.containsMouse ? accent : panel2; border.color: ma.containsMouse ? white : accent; border.width: 1
        Canvas { anchors.fill: parent; onPaint: { var ctx=getContext('2d'); ctx.clearRect(0,0,width,height); ctx.fillStyle = ma.containsMouse ? white : accent; ctx.beginPath(); if (direction>0) { ctx.moveTo(width/2-9,height/2-9); ctx.lineTo(width/2+9,height/2); ctx.lineTo(width/2-9,height/2+9) } else { ctx.moveTo(width/2+9,height/2-9); ctx.lineTo(width/2-9,height/2); ctx.lineTo(width/2+9,height/2+9) } ctx.closePath(); ctx.fill() } }
        MouseArea { id: ma; anchors.fill: parent; hoverEnabled: true; onClicked: parent.clicked() }
    }

    component ProgressBarCustom: Item { id: prog; width: root.width; height: 48
        property var steps: numKeys === 1 ? [[0,"Start"],[2,"Test"],[3,"Modus"],[4,"Eingabe"]] : [[0,"Start"],[1,"Belegung"],[2,"Test"],[3,"Modus"],[4,"Eingabe"]]
        Repeater { model: prog.steps.length
            Item { property var step: prog.steps[index]; x: root.width/2 - ((prog.steps.length-1)*180)/2 + index*180 - 90; y: 0; width: 180; height: 48
                Rectangle { visible: index < prog.steps.length-1; x: 99; y: 15; width: 160; height: 2; color: step[0] < panelIndex ? green : gray }
                Rectangle { width: step[0]===panelIndex ? 18 : 12; height: width; radius: width/2; x: 90-width/2; y: 15-height/2; color: step[0]===panelIndex ? accent : (step[0] < panelIndex ? green : gray)
                    Rectangle { visible: step[0]===panelIndex; width: 8; height: 8; radius: 4; anchors.centerIn: parent; color: white }
                }
                AppText { text: step[1]; size: 13; color: step[0]===panelIndex ? white : (step[0] < panelIndex ? lgray : gray); anchors.horizontalCenter: parent.horizontalCenter; y: 27 }
            }
        }
    }

    component IconCanvas: Canvas { id: c; property int iconMode: 0; property color iconColor: accent; property int w: 80; property int h: 80; width: w; height: h
        onIconColorChanged: requestPaint(); onIconModeChanged: requestPaint()
        onPaint: { var ctx=getContext('2d'); ctx.clearRect(0,0,width,height); drawModeIcon(ctx, iconMode, width/2, height/2, Math.min(width,height), iconColor) }
    }
    Canvas { id: iconCanvas; visible: false }
    Canvas { id: seqCanvas; visible: false }
    Canvas { id: inputCanvas; visible: false }

    function seqOffset(count) { var x = 0; for (var i = 0; i < count; i++) x += (seq[i] === "." ? 34 : 56); return x }

    function css(c) { return c.toString() }
    function drawModeIcon(ctx, m, cx, cy, s, col) {
        ctx.strokeStyle = css(col); ctx.fillStyle = css(col); ctx.lineCap = "round"; ctx.lineJoin = "round"
        if (m === 0) { ctx.lineWidth = Math.max(3, s/14); ctx.beginPath(); ctx.moveTo(cx-s/3,cy+s/2); ctx.lineTo(cx,cy-s/2); ctx.lineTo(cx+s/3,cy+s/2); ctx.moveTo(cx-s/5,cy+s/8); ctx.lineTo(cx+s/5,cy+s/8); ctx.stroke() }
        else if (m === 1) { ctx.lineWidth = Math.max(2, s/18); var gap=s/5; var lens=[s*2/3,s/2,s*3/5]; for (var i=0;i<3;i++){ var y=cy-s/3+i*gap; ctx.beginPath(); ctx.moveTo(cx-s/2,y); ctx.lineTo(cx-s/2+lens[i],y); ctx.stroke() } }
        else if (m === 2) { ctx.lineWidth = Math.max(2, s/18); ctx.strokeRect(cx-s/2, cy-s/2, s, s); for (var j=0;j<3;j++){ var yy=cy-s/4+j*(s/5); var fw=j<2?s*2/3:s/3; ctx.beginPath(); ctx.moveTo(cx-s/3,yy); ctx.lineTo(cx-s/3+fw,yy); ctx.stroke() } }
        else { ctx.lineWidth = Math.max(2, s/18); var r=s/2; ctx.beginPath(); ctx.arc(cx,cy,r,0,Math.PI*2); ctx.stroke(); ctx.beginPath(); ctx.moveTo(cx-r,cy); ctx.lineTo(cx+r,cy); ctx.moveTo(cx,cy-r); ctx.lineTo(cx,cy+r); ctx.stroke(); }
    }
    function drawKeySymbol(ctx, cx, cy, sym, lit, size) { ctx.fillStyle = lit ? css(accent) : css(gray); if (sym === ".") { ctx.beginPath(); ctx.arc(cx, cy, size/2, 0, Math.PI*2); ctx.fill() } else { roundRect(ctx, cx-size, cy-size/6, size*2, size/3, size/6, true, false) } }
    function roundRect(ctx, x, y, w, h, r, fill, stroke) { ctx.beginPath(); ctx.moveTo(x+r,y); ctx.lineTo(x+w-r,y); ctx.quadraticCurveTo(x+w,y,x+w,y+r); ctx.lineTo(x+w,y+h-r); ctx.quadraticCurveTo(x+w,y+h,x+w-r,y+h); ctx.lineTo(x+r,y+h); ctx.quadraticCurveTo(x,y+h,x,y+h-r); ctx.lineTo(x,y+r); ctx.quadraticCurveTo(x,y,x+r,y); ctx.closePath(); if (fill) ctx.fill(); if (stroke) ctx.stroke() }

    component FunctionTestPanel: Item { property real panelXOffset: 0; property real cx: root.width/2 - 60
        AppText { text: "Funktionstest"; size: 32; bold: true; color: white; x: cx-width/2; y: 14 }
        Rectangle { id: vis; x: cx-420; y: 50; width: 840; height: 280; radius: 14; color: testDone ? "#14371e" : (testError ? "#371414" : panel); border.color: testDone ? green : (testError ? red : borderColor); border.width: testDone || testError ? 2 : 1
            Canvas { anchors.fill: parent; onPaint: { var ctx=getContext('2d'); ctx.clearRect(0,0,width,height); if (!testDone && !testError) { var target=targetSeq(); var visCx=width/2; var visCy= numKeys===1 ? height/2-10 : height/2-20; if (numKeys===1) { ctx.fillStyle=css(chordActive?accent:gray); ctx.font='32px Menlo'; ctx.fillText('← + →', visCx-215, visCy+10); ctx.fillStyle=css(lgray); ctx.fillText('→', visCx+60, visCy+10); for (var i=0;i<target.length;i++){ drawKeySymbol(ctx, visCx+120+i*130, visCy, target[i], i<testSeq.length, 34) } } else { var slotW=160; var total=target.length*slotW; var x0=visCx-total/2; for (var j=0;j<target.length;j++){ var sx=x0+j*slotW+slotW/2; drawKeySymbol(ctx, sx, visCy, target[j], j<testSeq.length, 44) } } } } }
            AppText { visible: testDone; text: "A"; size: 72; bold: true; color: green; x: parent.width/2-width/2-60; y: parent.height/2-height/2-6 }
            AppText { visible: testDone; text: ".-"; size: 48; bold: true; color: green; x: parent.width/2+20; y: parent.height/2-height/2 }
            AppText { visible: testDone; text: "✓  Erfolgreich!"; size: 22; color: green; anchors.horizontalCenter: parent.horizontalCenter; y: parent.height-48 }
            AppText { visible: testError; text: "Falsche Taste — nochmal!"; size: 32; bold: true; color: red; anchors.centerIn: parent }
            AppText { visible: !testDone && !testError; text: testSeq.length + " / " + targetSeq().length; size: 16; color: lgray; x: parent.width-width-14; y: parent.height-30 }
        }
        Item { id: instr; x: 0; y: 354; width: parent.width; height: 200
            AppText { visible: !testDone && numKeys===1; text: "Drücke ← und → gleichzeitig:"; size: 22; color: white; x: cx-width/2; y: 0 }
            Rectangle { visible: !testDone && numKeys===1; x: cx-200; y: 28; width: 400; height: 10; radius: 5; color: panel2; border.color: chordActive ? "transparent" : borderColor
                Rectangle { visible: chordActive; width: Math.min(400, 400*((nowSec()-chordPressT)/chordLongT)); height: 10; radius: 5; color: width>=400 ? red : (width>200 ? amber : accent) }
                Rectangle { x: 266; y: -5; width: 2; height: 20; color: amber }
            }
            AppText { visible: !testDone && numKeys===1; text: "LANG"; size: 13; color: amber; x: cx+74; y: 25 }
            Rectangle { visible: !testDone && numKeys===1; x: cx-320; y: 72; width: 280; height: 72; radius: 10; color: panel2; border.width: 2; border.color: testSeq.length>=1 ? green : accent
                AppText { text: (testSeq.length>=1 ? "✓" : "▶") + "  ← + →  kurz  →  KURZ (.)"; size: 22; color: testSeq.length>=1 ? green : accent; anchors.centerIn: parent }
            }
            Rectangle { visible: !testDone && numKeys===1; x: cx+40; y: 72; width: 280; height: 72; radius: 10; color: panel2; border.width: 2; border.color: testSeq.length>=2 ? green : (testSeq.length===1 ? accent : lgray)
                AppText { text: (testSeq.length>=2 ? "✓" : (testSeq.length===1 ? "▶" : " ")) + "  ← + →  lang  →  LANG (−)"; size: 22; color: testSeq.length>=2 ? green : (testSeq.length===1 ? accent : lgray); anchors.centerIn: parent }
            }
            AppText { visible: !testDone && numKeys===1; text: "Kurz = loslassen vor dem Balken  |  Lang = halten bis Balken voll  (400 ms)"; size: 13; color: lgray; x: cx-width/2; y: 158 }

            AppText { visible: !testDone && numKeys!==1; text: "Drücke die Tasten nacheinander:"; size: 22; color: white; x: cx-width/2; y: 0 }
            Rectangle { visible: !testDone && numKeys!==1; x: cx-310; y: 32; width: 270; height: 68; radius: 10; color: panel2; border.width: 2; border.color: testSeq.length>=1 ? green : accent
                AppText { text: "1.  " + (leftSig()==='.' ? '←' : '→') + "  →  KURZ (.)"; size: 22; color: testSeq.length>=1 ? green : accent; anchors.centerIn: parent }
            }
            AppText { visible: !testDone && numKeys!==1; text: "▶"; size: 32; color: gray; x: cx-18; y: 47 }
            Rectangle { visible: !testDone && numKeys!==1; x: cx+40; y: 32; width: 270; height: 68; radius: 10; color: panel2; border.width: 2; border.color: testSeq.length>=2 ? green : (testSeq.length===1 ? accent : lgray)
                AppText { text: "2.  " + (leftSig()==='-' ? '←' : '→') + "  →  LANG (−)"; size: 22; color: testSeq.length>=2 ? green : (testSeq.length===1 ? accent : lgray); anchors.centerIn: parent }
            }
            AppText { visible: !testDone && numKeys!==1; text: "Ziel-Zeichen:  A  =  .-  (kurz, dann lang)"; size: 13; color: lgray; x: cx-width/2; y: 120 }
            AppText { visible: testDone; text: "Weiter mit ENTER oder warte kurz…"; size: 22; color: lgray; x: cx-width/2; y: 40 }
        }
    }

    component InputPanel: Item { property real cx: root.width/2 - 60; property color col: modeColor(mode)
        AppText { text: "Modus: " + modeNames[mode]; size: 22; color: col; x: cx-width/2; y: 4 }
        AppText { text: "←=" + (leftSig()==="-" ? "LANG" : "KURZ") + "   →=" + (rightSig()==="-" ? "LANG" : "KURZ") + "   SPACE=Zeichen abschließen   ENTER=Wort   BACK=löschen"; size: 13; color: lgray; x: cx-width/2; y: 35 }
        Rectangle { id: out; x: cx-460; y: 60; width: 920; height: 210; radius: 12; color: panel; border.color: col
            AppText { text: "AUSGABE"; size: 13; color: lgray; x: 12; y: 8 }
            IconCanvas { x: mode===2 ? 38 : (mode===0 ? width/2-140 : width/2-180); y: 74; w: mode===0 ? 100 : 80; h: mode===0 ? 100 : 80; iconMode: mode; iconColor: col }
            AppText { visible: mode===0; text: (output || word) ? (output || word).slice(-1) : "?"; size: (output || word) ? 72 : 32; bold: true; color: (output || word) ? white : gray; x: width/2+20; y: 69 }
            AppText { visible: mode===1 || mode===3; text: (output || word) ? (output || word) : "—"; size: mode===1 ? 32 : 22; bold: mode===1; color: white; x: width/2-40; y: 88 }
            AppText { visible: mode===2; text: (output || word) ? (output || word) : "—"; size: 22; color: white; wrapMode: Text.WordWrap; x: 160; y: 44; width: parent.width-180; height: parent.height-64 }
            Rectangle { visible: flashA > 0; width: 80; height: 80; radius: 10; x: parent.width-90; y: 10; color: Qt.rgba(0.313,0.804,0.47, flashA/255) }
        }
        Rectangle { id: seqR; x: cx-460; y: 283; width: 920; height: 72; radius: 8; color: panel; border.color: borderColor
            AppText { text: "AKTUELLE SEQUENZ"; size: 13; color: lgray; x: 12; y: 6 }
            Repeater { model: seq.length
                Rectangle { x: 16 + seqOffset(index); y: seqR.height/2 + (seq[index]==='.' ? -8 : -8); width: seq[index]==='.' ? 24 : 40; height: seq[index]==='.' ? 24 : 22; radius: seq[index]==='.' ? 12 : 4; color: seq[index]==='.' ? accent : amber }
            }
            AppText { visible: decoded.length>0 && decoded!=="?"; text: "→ " + decoded; size: 22; color: green; x: parent.width-width-14; y: parent.height/2-15 }
            AppText { visible: seq.length===0; text: "warte auf Eingabe…"; size: 16; color: gray; x: 16; y: parent.height/2-12 }
        }
        Rectangle { visible: seq.length>0; x: cx-460; y: 360; width: 920; height: 7; radius: 3; color: gray
            Rectangle { width: 920*Math.min((nowSec()-lastT)/charTo,1); height: 7; radius: 3; color: width < 552 ? green : (width < 782 ? amber : red) }
        }
        AppText { text: "REFERENZ:"; size: 13; color: lgray; x: cx-460; y: 377 }
        Repeater { model: refs.length
            AppText { text: refs[index][0]+":"+refs[index][1]; size: 13; color: lgray; x: cx-360+index*80; y: 377 }
        }
    }
}
