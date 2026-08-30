import QtQuick
import QtQuick.Controls
import "../Globalvariables.js" as Globals

Page {
    id: root
    property int tournamentId: -1
    property var tournament: ({})

    function refreshWaitingRoom() {
        tournament = OnlineBridge.loadTournament(tournamentId)
        OnlineBridge.refresh()
    }

    Component.onCompleted: refreshWaitingRoom()

    Timer {
        interval: 1000
        repeat: true
        running: root.visible
        onTriggered: refreshWaitingRoom()
    }

    background: Rectangle {
        gradient: Gradient {
            GradientStop { position: 0; color: "#FBFBFD" }
            GradientStop { position: 1; color: "#EEF1F5" }
        }
    }

    Rectangle {
        x: 28; y: 24; width: 54; height: 54; radius: 27
        color: backMouse.pressed ? "#D7D7DC" : "#FFFFFF"
        border.color: "#E3E3E8"
        Text { anchors.centerIn: parent; text: "‹"; font.pixelSize: 42; y: -2 }
        MouseArea { id: backMouse; anchors.fill: parent; onClicked: stackView.pop() }
    }

    ScrollView {
        anchors.fill: parent
        anchors.margins: 54
        anchors.topMargin: 86

        Column {
            width: Math.min(850, root.width - 108)
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: 18

            Text {
                width: parent.width
                horizontalAlignment: Text.AlignHCenter
                text: tournament.name || qsTr("Tournament")
                font.pixelSize: 38
                font.weight: Font.DemiBold
                color: "#1D1D1F"
                wrapMode: Text.WordWrap
            }

            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: tournament.status === "scheduled"
                      ? qsTr("Waiting for the tournament to start …")
                      : tournament.status === "running"
                        ? qsTr("Tournament is running")
                        : qsTr("Tournament finished")
                color: tournament.status === "running" ? "#34C759" : "#6E6E73"
                font.pixelSize: 19
            }

            Rectangle {
                width: parent.width; height: 92; radius: 24
                color: "#FFFFFF"; border.color: "#E4E4E9"
                Row {
                    anchors.fill: parent; anchors.margins: 18; spacing: 28
                    Column { Text { text: qsTr("Mode"); color: "#8E8E93" } Text { text: tournament.mode || ""; font.pixelSize: 20; font.weight: Font.DemiBold } }
                    Column { Text { text: qsTr("Starts"); color: "#8E8E93" } Text { text: tournament.starts_at || ""; font.pixelSize: 16 } }
                    Column { Text { text: qsTr("Players"); color: "#8E8E93" } Text { text: tournament.players ? tournament.players.length : 0; font.pixelSize: 20; font.weight: Font.DemiBold } }
                }
            }

            Text { text: qsTr("Players"); font.pixelSize: 24; font.weight: Font.DemiBold }
            Flow {
                width: parent.width; spacing: 10
                Repeater {
                    model: tournament.players || []
                    delegate: Rectangle {
                        required property var modelData
                        width: playerText.implicitWidth + 28; height: 40; radius: 20
                        color: modelData.id === OnlineBridge.playerId ? "#E8F2FF" : "#FFFFFF"
                        border.color: modelData.id === OnlineBridge.playerId ? "#007AFF" : "#E4E4E9"
                        Text { id: playerText; anchors.centerIn: parent; text: modelData.display_name; color: "#1D1D1F" }
                    }
                }
            }

            Text { text: qsTr("Your matches"); font.pixelSize: 24; font.weight: Font.DemiBold }
            Repeater {
                model: OnlineBridge.matches.filter(function(m) { return m.tournament_id === root.tournamentId })
                delegate: Rectangle {
                    required property var modelData
                    width: parent.width; height: 96; radius: 22
                    color: "#FFFFFF"; border.color: "#E4E4E9"
                    property bool ready: tournament.status === "running" && new Date(modelData.scheduled_at).getTime() <= Date.now()
                    Row {
                        anchors.fill: parent; anchors.margins: 16; spacing: 12
                        Column {
                            width: parent.width - play.width - 12; spacing: 4
                            Text { text: qsTr("vs %1").arg(modelData.opponent); font.pixelSize: 18; font.weight: Font.DemiBold }
                            Text { text: modelData.scheduled_at; color: "#6E6E73" }
                            Text { text: modelData.status; color: "#8E8E93" }
                        }
                        Button {
                            id: play
                            text: modelData.status === "finished" ? qsTr("Finished") : ready ? qsTr("Play") : qsTr("Waiting")
                            enabled: ready && modelData.status !== "finished"
                            onClicked: stackView.push("TournamentMatch.qml", {
                                matchId: modelData.id,
                                inputType: Globals.eingabeart,
                                leftButtonType: Globals.lefttype,
                                rightButtonType: Globals.righttype
                            })
                        }
                    }
                }
            }

            Text {
                visible: tournament.status === "scheduled"
                width: parent.width
                horizontalAlignment: Text.AlignHCenter
                text: qsTr("You can leave this page; your registration stays active.")
                color: "#8E8E93"
            }
        }
    }
}
