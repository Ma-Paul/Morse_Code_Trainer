import QtQuick
import QtQuick.Controls

Page {
    id:root
    property int challengeId:-1
    property string challengeMode:"Letter"
    property string challengeText:"e"
    property string inputType:"1"
    property string leftButtonType:"Zeitgesteuert"
    property string rightButtonType:"Zeitgesteuert"
    property var trainer: challengeMode==="Letter"?LetterTrainer:(challengeMode==="Word"?WordTrainer:SentenceTrainer)
    property bool singleDown:false; property bool leftDown:false; property bool rightDown:false
    focus:true; Keys.priority:Keys.BeforeItem

    function startChallenge(){
        trainer.configureInput(inputType, leftButtonType, rightButtonType)
        if(challengeMode==="Letter") LetterTrainer.startLetter(challengeText)
        else if(challengeMode==="Word") WordTrainer.startWord(challengeText)
        else SentenceTrainer.startSentence(challengeText)
        root.forceActiveFocus()
    }
    Component.onCompleted:startChallenge()

    Keys.onPressed:function(e){ if(e.isAutoRepeat)return; if(e.key===Qt.Key_Space){singleDown=true;trainer.buttonPressed("single");e.accepted=true}else if(e.key===Qt.Key_Left){leftDown=true;trainer.buttonPressed("left");e.accepted=true}else if(e.key===Qt.Key_Right){rightDown=true;trainer.buttonPressed("right");e.accepted=true} }
    Keys.onReleased:function(e){ if(e.isAutoRepeat)return; if(e.key===Qt.Key_Space&&singleDown){singleDown=false;trainer.buttonReleased("single");e.accepted=true}else if(e.key===Qt.Key_Left&&leftDown){leftDown=false;trainer.buttonReleased("left");e.accepted=true}else if(e.key===Qt.Key_Right&&rightDown){rightDown=false;trainer.buttonReleased("right");e.accepted=true} }

    background:Rectangle{gradient:Gradient{GradientStop{position:0;color:"#FBFBFD"}GradientStop{position:1;color:"#EEF1F5"}}}
    Column{anchors.centerIn:parent;spacing:20
        Text{anchors.horizontalCenter:parent.horizontalCenter;text:qsTr("Daily Challenge");font.pixelSize:24;color:"#6E6E73"}
        Text{anchors.horizontalCenter:parent.horizontalCenter;text:challengeText.toUpperCase();font.pixelSize:56;font.weight:Font.DemiBold;color:"#1D1D1F"}
        Text{anchors.horizontalCenter:parent.horizontalCenter;text:trainer.morse!==undefined?trainer.morse:"";font.pixelSize:34;color:"#1D1D1F"}
        Text{anchors.horizontalCenter:parent.horizontalCenter;text:qsTr("Complete it correctly to earn 1 point.");color:"#6E6E73"}
    }

    Connections{target:LetterTrainer; enabled:challengeMode==="Letter"; function onCorrect(t){ OnlineBridge.completeDaily(challengeId); stackView.pop() } function onMistake(){ startChallenge() }}
    Connections{target:WordTrainer; enabled:challengeMode==="Word"; function onWordCorrect(t){ OnlineBridge.completeDaily(challengeId); stackView.pop() } function onMistake(){ startChallenge() }}
    Connections{target:SentenceTrainer; enabled:challengeMode==="Sentence"; function onSentenceCorrect(t){ OnlineBridge.completeDaily(challengeId); stackView.pop() } function onMistake(){ startChallenge() }}
}
