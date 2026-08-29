import QtQuick
import QtQuick.Controls
Page{id:root;property int matchId:-1;property string inputType:"1";property string leftButtonType:"Zeitgesteuert";property string rightButtonType:"Zeitgesteuert";property bool s:false;property bool l:false;property bool r:false;focus:true;Keys.priority:Keys.BeforeItem
Component.onCompleted:{OnlineGame.configureInput(inputType,leftButtonType,rightButtonType);if(!OnlineGame.start(matchId))stackView.pop();root.forceActiveFocus()}
Keys.onPressed:function(e){if(e.isAutoRepeat)return;if(e.key===Qt.Key_Space){s=true;OnlineGame.buttonPressed("single");e.accepted=true}else if(e.key===Qt.Key_Left){l=true;OnlineGame.buttonPressed("left");e.accepted=true}else if(e.key===Qt.Key_Right){r=true;OnlineGame.buttonPressed("right");e.accepted=true}}
Keys.onReleased:function(e){if(e.isAutoRepeat)return;if(e.key===Qt.Key_Space&&s){s=false;OnlineGame.buttonReleased("single");e.accepted=true}else if(e.key===Qt.Key_Left&&l){l=false;OnlineGame.buttonReleased("left");e.accepted=true}else if(e.key===Qt.Key_Right&&r){r=false;OnlineGame.buttonReleased("right");e.accepted=true}}
background:Rectangle{gradient:Gradient{GradientStop{position:0;color:"#FBFBFD"}GradientStop{position:1;color:"#EEF1F5"}}}
Column{anchors.centerIn:parent;spacing:20
Text{anchors.horizontalCenter:parent.horizontalCenter;text:OnlineGame.secondsLeft+" s";font.pixelSize:28;color:"#007AFF"}
Text{anchors.horizontalCenter:parent.horizontalCenter;text:OnlineGame.challenge.toUpperCase();font.pixelSize:64;font.weight:Font.DemiBold;color:"#1D1D1F"}
Text{anchors.horizontalCenter:parent.horizontalCenter;text:qsTr("Score: %1").arg(OnlineGame.score);font.pixelSize:26;color:"#6E6E73"}
Text{anchors.horizontalCenter:parent.horizontalCenter;text:qsTr("Both players receive the same challenge sequence.");color:"#8E8E93"}
}
Connections{target:OnlineGame;function onFinished(score,time){result.open()}}
Dialog{id:result;anchors.centerIn:parent;modal:true;closePolicy:Popup.NoAutoClose;title:qsTr("Match finished")
Column{spacing:12;Text{text:qsTr("Score: %1").arg(OnlineGame.score);font.pixelSize:24}Button{text:qsTr("Back to Online");onClicked:{result.close();stackView.pop()}}}}
}
