import QtQuick
import QtQuick.Controls
import "../Globalvariables.js" as Globals

Page {
    id: root
    Component.onCompleted: { OnlineBridge.refresh(); if (OnlineBridge.playerId.length === 0) identityDialog.open() }
    background: Rectangle { gradient: Gradient { GradientStop { position:0; color:"#FBFBFD" } GradientStop { position:1; color:"#EEF1F5" } } }

    Rectangle { x:28; y:24; width:54; height:54; radius:27; color:"#FFFFFF"; border.color:"#E3E3E8"
        Text { anchors.centerIn:parent; text:"‹"; font.pixelSize:42; color:"#1D1D1F"; y:-2 }
        MouseArea { anchors.fill:parent; onClicked:stackView.pop() }
    }

    ScrollView { anchors.fill:parent; anchors.margins:54; anchors.topMargin:92
        Column { width:Math.min(900,root.width-108); anchors.horizontalCenter:parent.horizontalCenter; spacing:22
            Row { width:parent.width
                Column { width:parent.width-changeId.width; spacing:4
                    Text { text:qsTr("Online"); font.pixelSize:44; font.weight:Font.DemiBold; color:"#1D1D1F" }
                    Text { text:OnlineBridge.playerId.length?qsTr("Playing as %1").arg(OnlineBridge.playerId):qsTr("Choose your player ID"); color:"#6E6E73"; font.pixelSize:17 }
                }
                Button { id:changeId; text:qsTr("Change ID"); onClicked:identityDialog.open() }
            }

            Rectangle { width:parent.width; height:Math.max(170,leaderCol.implicitHeight+36); radius:28; color:"white"; border.color:"#E4E4E9"
                Column { id:leaderCol; anchors.fill:parent; anchors.margins:20; spacing:9
                    Text { text:qsTr("Daily Challenge Leaderboard"); font.pixelSize:23; font.weight:Font.DemiBold }
                    Repeater { model:OnlineBridge.leaderboard.slice(0,10)
                        delegate:Row { required property var modelData; width:parent.width; spacing:8
                            Text { width:30; text:(index+1)+"."; color:"#6E6E73" }
                            Text { width:parent.width-130; text:(modelData.tournament_place?"★ ":"")+modelData.display_name; color:modelData.tournament_place===1?"#B8860B":modelData.tournament_place===2?"#8E8E93":modelData.tournament_place===3?"#A5673F":"#1D1D1F"; font.weight:Font.Medium }
                            Text { width:80; horizontalAlignment:Text.AlignRight; text:modelData.daily_points }
                        }
                    }
                }
            }

            Text { text:qsTr("Today's challenges"); font.pixelSize:27; font.weight:Font.DemiBold }
            Repeater { model:OnlineBridge.dailyChallenges
                delegate:Rectangle { required property var modelData; width:parent.width; height:96; radius:22; color:"white"; border.color:"#E4E4E9"
                    Row { anchors.fill:parent; anchors.margins:16; spacing:12
                        Column { width:parent.width-startDaily.width-12; spacing:4
                            Text { text:modelData.mode; font.weight:Font.DemiBold; font.pixelSize:18 }
                            Text { text:modelData.challenge_text; color:"#6E6E73" }
                        }
                        Button { id:startDaily; text:modelData.completed?qsTr("Done"):qsTr("Start"); enabled:!modelData.completed
                            onClicked:stackView.push("DailyChallengeMode.qml", {
                                challengeId:modelData.id, challengeMode:modelData.mode, challengeText:modelData.challenge_text,
                                inputType:Globals.eingabeart, leftButtonType:Globals.lefttype, rightButtonType:Globals.righttype
                            }) }
                    }
                }
            }

            Row { width:parent.width; spacing:10
                TextField { id:invite; width:parent.width-joinCode.width-10; placeholderText:qsTr("Invite code") }
                Button { id:joinCode; text:qsTr("Join"); onClicked:{
                    var tournamentId = OnlineBridge.joinWithCode(invite.text)
                    invite.clear()
                    if (tournamentId >= 0) {
                        stackView.push("WaitingRoom.qml", { tournamentId: tournamentId })
                    }
                } }
            }

            Text { text:qsTr("My matches"); font.pixelSize:27; font.weight:Font.DemiBold }
            Repeater { model:OnlineBridge.matches
                delegate:Rectangle { required property var modelData; width:parent.width; height:100; radius:22; color:"white"; border.color:"#E4E4E9"
                    Row { anchors.fill:parent; anchors.margins:16
                        Column { width:parent.width-playButton.width; spacing:3
                            Text { text:modelData.tournament_name+" · "+modelData.mode; font.weight:Font.DemiBold; font.pixelSize:18 }
                            Text { text:qsTr("vs %1").arg(modelData.opponent); color:"#6E6E73" }
                            Text { text:modelData.scheduled_at+" · "+modelData.status; color:"#8E8E93"; font.pixelSize:13 }
                        }
                        Button { id:playButton; text:qsTr("Play"); enabled:modelData.status!=="finished"; onClicked:stackView.push("TournamentMatch.qml", {
                                matchId:modelData.id, inputType:Globals.eingabeart, leftButtonType:Globals.lefttype, rightButtonType:Globals.righttype
                            }) }
                    }
                }
            }

            Text { text:qsTr("Tournaments"); font.pixelSize:27; font.weight:Font.DemiBold }
            Repeater { model:OnlineBridge.tournaments
                delegate:Rectangle { required property var modelData; width:parent.width; height:108; radius:22; color:"white"; border.color:"#E4E4E9"
                    Row { anchors.fill:parent; anchors.margins:16
                        Column { width:parent.width-joinOpen.width; spacing:4
                            Text { text:modelData.name; font.pixelSize:19; font.weight:Font.DemiBold }
                            Text { text:modelData.mode+" · "+modelData.visibility+" · "+modelData.recurrence; color:"#6E6E73" }
                            Text { text:modelData.starts_at+" · "+modelData.status; color:"#8E8E93"; font.pixelSize:13 }
                        }
                        Button { id:joinOpen; visible:modelData.visibility==="open"; text:qsTr("Join"); onClicked:{
                            var tournamentId = OnlineBridge.joinTournament(modelData.id)
                            if (tournamentId >= 0) {
                                stackView.push("WaitingRoom.qml", { tournamentId: tournamentId })
                            }
                        } }
                    }
                }
            }
            Text { visible:OnlineBridge.error.length>0; width:parent.width; text:OnlineBridge.error; color:"#FF3B30"; wrapMode:Text.WordWrap }
            Item { width:1; height:30 }
        }
    }

    Dialog { id:identityDialog; anchors.centerIn:parent; modal:true; closePolicy:OnlineBridge.playerId.length===0?Popup.NoAutoClose:Popup.CloseOnEscape; title:qsTr("Wie möchtest du heißen?")
        Column { spacing:14
            Text { width:340; text:qsTr("This ID is your name in tournaments and leaderboards."); color:"#6E6E73"; wrapMode:Text.WordWrap }
            TextField { id:idField; width:340; text:OnlineBridge.playerId; placeholderText:qsTr("Player ID"); maximumLength:32 }
            Button { text:qsTr("Continue"); enabled:idField.text.trim().length>0; onClicked:if(OnlineBridge.setPlayerId(idField.text))identityDialog.close() }
        }
    }
}
