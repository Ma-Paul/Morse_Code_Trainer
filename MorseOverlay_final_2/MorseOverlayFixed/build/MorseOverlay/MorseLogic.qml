// MorseLogic.qml — mirrors the Python Overlay class
import QtQuick

QtObject {
    id: logic

    // ── Signals ───────────────────────────────────────────────
    signal charFlash(string ch)
    signal statusChanged(string msg)

    // ── Constants ─────────────────────────────────────────────
    readonly property int modeLetter:   0
    readonly property int modeWord:     1
    readonly property int modeSentence: 2
    readonly property int modeFile:     3

    readonly property int input1key: 0
    readonly property int input2key: 1

    readonly property real charTimeout: 1200
    readonly property real wordTimeout: 2500

    // ── State ─────────────────────────────────────────────────
    property int  mode:         modeLetter
    property int  inputMode:    input1key
    property int  keyConfigIdx: 0
    property bool showConfig:   false

    property string currentSeq:  ""
    property string currentWord: ""
    property string outputText:  ""
    property string decodedChar: ""
    property string statusMsg:   ""
    property string flashChar:   ""

    property real lastKeyTime: 0
    property real statusTime:  0

    // ── Morse table ───────────────────────────────────────────
    readonly property var morseMap: ({
        ".-":"A",    "-...":"B",  "-.-.":"C",  "-..":"D",   ".":"E",
        "..-.":"F",  "--.":"G",   "....":"H",  "..":"I",    ".---":"J",
        "-.-":"K",   ".-..":"L",  "--":"M",    "-.":"N",    "---":"O",
        ".--.":"P",  "--.-":"Q",  ".-.":"R",   "...":"S",   "-":"T",
        "..-":"U",   "...-":"V",  ".--":"W",   "-..-":"X",  "-.--":"Y",
        "--..":"Z",  "-----":"0", ".----":"1", "..---":"2", "...--":"3",
        "....-":"4", ".....":"5", "-....":"6", "--...":"7", "---..":"8",
        "----.":"9"
    })

    // ── Key configs ───────────────────────────────────────────
    readonly property var keyConfigs1: [
        { label: "Links lang / Rechts kurz", left: "-", right: "." },
        { label: "Links kurz / Rechts lang", left: ".",  right: "-" }
    ]
    readonly property var keyConfigs2: [
        { label: "Links lang / Rechts kurz", left: "-", right: "." },
        { label: "Links kurz / Rechts lang", left: ".",  right: "-" },
        { label: "Beide seltsam / Normal",   left: "-", right: "." }
    ]

    function currentConfigs() {
        return inputMode === input1key ? keyConfigs1 : keyConfigs2
    }

    function currentConfig() {
        var cfgs = currentConfigs()
        var idx  = Math.min(keyConfigIdx, cfgs.length - 1)
        return cfgs[idx]
    }

    // ── Core actions ──────────────────────────────────────────
    // NOTE: 'signal' is a reserved word in QML — parameter renamed to 'sig'
    function addSignal(sig) {
        currentSeq  += sig
        lastKeyTime  = Date.now()
        decodedChar  = morseMap[currentSeq] || "?"
    }

    function commitChar() {
        if (!currentSeq) return
        var ch = morseMap[currentSeq] || ""
        if (ch) {
            flashChar = ch
            charFlash(ch)
            if (mode === modeLetter) {
                outputText = ch
            } else {
                currentWord += ch
                outputText   = currentWord
            }
        } else {
            setStatus("?? unbekannte Sequenz: " + currentSeq)
        }
        currentSeq  = ""
        decodedChar = ""
    }

    function commitWord() {
        if (mode === modeSentence || mode === modeFile) {
            if (currentWord) {
                outputText += " "
                currentWord = ""
            }
        } else if (mode === modeWord) {
            currentWord = ""
            outputText  = ""
        }
    }

    function backspace() {
        if (currentSeq) {
            currentSeq  = currentSeq.slice(0, -1)
            decodedChar = currentSeq ? (morseMap[currentSeq] || "?") : ""
        } else if ((mode === modeWord || mode === modeSentence || mode === modeFile)
                   && currentWord) {
            currentWord = currentWord.slice(0, -1)
            outputText  = currentWord
        } else if (outputText) {
            outputText = outputText.slice(0, -1)
        }
    }

    function cycleMode() {
        commitChar()
        mode        = (mode + 1) % 4
        outputText  = ""
        currentWord = ""
    }

    function toggleInputMode() {
        commitChar()
        inputMode    = 1 - inputMode
        keyConfigIdx = 0
        setStatus("Eingabe: " + (inputMode === input1key ? "1 Taste" : "2 Tasten"))
    }

    function setStatus(msg) {
        statusMsg  = msg
        statusTime = Date.now()
    }

    // ── Timeout polling ───────────────────────────────────────
    function tick() {
        var now = Date.now()
        if (currentSeq && (now - lastKeyTime) > charTimeout)
            commitChar()
        if ((mode === modeSentence || mode === modeFile)
                && currentWord && !currentSeq
                && (now - lastKeyTime) > wordTimeout)
            commitWord()
        if (statusMsg && (now - statusTime) > 3000)
            statusMsg = ""
    }
}
