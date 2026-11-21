.pragma library
// "1" = one button
// "2" = two buttons
var eingabeart = "1"

// Two-button configuration:
// "Pause", "Lang", "Kurz", "Zeitgesteuert"
var lefttype = "Zeitgesteuert"
var righttype = "Zeitgesteuert"

var mode = "Letter"

// Show the target Morse code during training
var showLetterMorse = true


function setEingabeart(value) {
    eingabeart = value
}

function setLefttype(value) {
    lefttype = value
}

function setRighttype(value) {
    righttype = value
}

function setMode(value) {
    mode = value
}

function setShowLetterMorse(value) {
    showLetterMorse = value
}


// Display labels are separate from the stored button-function identifiers.
function buttonLabel(value) {
    switch (value) {
    case "Pause": return qsTr("Gap")
    case "Lang": return qsTr("Dash")
    case "Kurz": return qsTr("Dot")
    case "Zeitgesteuert": return qsTr("Timed")
    default: return value
    }
}
