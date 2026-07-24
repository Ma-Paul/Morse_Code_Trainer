.pragma library

// Input configuration
var eingabeart = ""
var lefttype = "Dit"
var righttype = "Dah"

// Selected training mode
var mode = "letter"

// Letter-mode settings
var showLetterMorse = true


// Setter functions are required because QML must not write directly
// to properties of a JavaScript library import.

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


// Optional getters

function getEingabeart() {
    return eingabeart
}

function getLefttype() {
    return lefttype
}

function getRighttype() {
    return righttype
}

function getMode() {
    return mode
}

function getShowLetterMorse() {
    return showLetterMorse
}


// Restore default values

function reset() {
    eingabeart = ""
    lefttype = "Dit"
    righttype = "Dah"
    mode = "letter"
    showLetterMorse = true
}
