import QtQuick
import QtQuick.Controls

Dialog {
    id: root

    property var trainer: null

    property string displayTitle: ""
    property string displaySubtitle: ""

    property string resultType: "mistake"
    property real elapsedSeconds: 0

    property string enteredCode:
        trainer ? trainer.lastMistakeEntered : ""

    property string expectedCode:
        trainer ? trainer.lastMistakeExpected : ""

    property string explanation:
        trainer ? trainer.lastMistakeExplanation : ""

    signal continueRequested()

    readonly property bool isCorrect:
        resultType === "correct"

    anchors.centerIn: parent
    modal: true
    closePolicy: Popup.NoAutoClose

    width: Math.min(
        520,
        parent ? parent.width - 40 : 520
    )

    padding: 0

    function displaySymbol(symbol) {
        return symbol === "." ? "•" : "—"
    }

    function displayCode(code) {
        if (!code) {
            return ""
        }

        return code
            .split("_").join("—")
            .split(".").join("•")
    }

    function showCorrect(
        title,
        subtitle,
        seconds
    ) {
        displayTitle = title || ""
        displaySubtitle = subtitle || ""
        elapsedSeconds = Number(seconds) || 0
        resultType = "correct"
        open()
    }

    function showMistake(
        title,
        subtitle
    ) {
        displayTitle = title || ""
        displaySubtitle = subtitle || ""
        resultType = "mistake"
        open()
    }

    background: Rectangle {
        radius: 28
        color: "#FFFFFF"

        border.color: "#E4E4E9"
        border.width: 1
    }

    contentItem: Item {
        implicitWidth:
            resultContent.implicitWidth + 60

        implicitHeight:
            resultContent.implicitHeight + 60

        Column {
            id: resultContent

            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.margins: 30

            spacing: 14

            Text {
                anchors.horizontalCenter:
                    parent.horizontalCenter

                text: root.isCorrect ? "✓" : "!"

                color:
                    root.isCorrect
                    ? "#34C759"
                    : "#FF3B30"

                font.pixelSize: 54
                font.weight: Font.DemiBold
            }

            Text {
                anchors.horizontalCenter:
                    parent.horizontalCenter

                text:
                    root.isCorrect
                    ? qsTr("Richtig")
                    : qsTr("Nicht ganz richtig")

                color: "#1D1D1F"
                font.pixelSize: 28
                font.weight: Font.DemiBold
            }

            Text {
                width: parent.width

                visible:
                    root.displayTitle.length > 0

                horizontalAlignment:
                    Text.AlignHCenter

                wrapMode: Text.WordWrap

                text: root.displayTitle

                color: "#1D1D1F"
                font.pixelSize: 54
                font.weight: Font.DemiBold
            }

            Text {
                width: parent.width

                visible:
                    root.displaySubtitle.length > 0

                horizontalAlignment:
                    Text.AlignHCenter

                wrapMode: Text.WordWrap

                text: root.displaySubtitle

                color: "#6E6E73"
                font.pixelSize: 18
            }

            Row {
                anchors.horizontalCenter:
                    parent.horizontalCenter

                visible:
                    root.expectedCode.length > 0

                spacing: 12

                Repeater {
                    model:
                        root.expectedCode.length

                    delegate: Text {
                        required property int index

                        text: root.displaySymbol(
                            root.expectedCode.charAt(index)
                        )

                        color: "#34C759"
                        font.pixelSize: 42
                        font.weight: Font.DemiBold
                    }
                }
            }

            Text {
                width: parent.width

                visible:
                    !root.isCorrect
                    && root.explanation.length > 0

                horizontalAlignment:
                    Text.AlignHCenter

                wrapMode: Text.WordWrap

                text: root.explanation

                color: "#6E6E73"
                font.pixelSize: 17
            }

            Rectangle {
                width: parent.width

                visible: !root.isCorrect

                height:
                    mistakeInformation.implicitHeight + 28

                radius: 18
                color: "#F7F7F9"
                clip: true

                Column {
                    id: mistakeInformation

                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.top: parent.top

                    anchors.leftMargin: 18
                    anchors.rightMargin: 18
                    anchors.topMargin: 14

                    spacing: 10

                    Text {
                        width: parent.width

                        text: qsTr("Deine Eingabe:")

                        color: "#6E6E73"
                        font.pixelSize: 15
                    }

                    Text {
                        width: parent.width

                        text:
                            root.enteredCode.length > 0
                            ? root.displayCode(
                                  root.enteredCode
                              )
                            : qsTr("keine Eingabe")

                        color: "#FF3B30"
                        font.pixelSize: 24
                        font.weight: Font.DemiBold
                        font.letterSpacing: 4

                        wrapMode: Text.WrapAnywhere
                    }

                    Text {
                        width: parent.width

                        text: qsTr("Erwartet:")

                        color: "#6E6E73"
                        font.pixelSize: 15
                    }

                    Text {
                        width: parent.width

                        text: root.displayCode(
                            root.expectedCode
                        )

                        color: "#34C759"
                        font.pixelSize: 24
                        font.weight: Font.DemiBold
                        font.letterSpacing: 4

                        wrapMode: Text.WrapAnywhere
                    }
                }
            }

            Text {
                anchors.horizontalCenter:
                    parent.horizontalCenter

                visible: root.isCorrect

                text: qsTr(
                    "Zeit: %1 s"
                ).arg(
                    root.elapsedSeconds.toFixed(2)
                )

                color: "#6E6E73"
                font.pixelSize: 18
            }

            Item {
                width: 1
                height: 4
            }

            Button {
                anchors.horizontalCenter:
                    parent.horizontalCenter

                text: qsTr("Weiter")

                onClicked: {
                    root.close()
                    root.continueRequested()
                }
            }
        }
    }
}
