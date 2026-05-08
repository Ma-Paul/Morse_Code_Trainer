cmake_minimum_required(VERSION 3.16)
project(MorseOverlay VERSION 1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Qt6 6.4 REQUIRED COMPONENTS Quick)

qt_standard_project_setup(REQUIRES 6.4)

qt_add_executable(MorseOverlayApp
    main.cpp
)

qt_add_qml_module(MorseOverlayApp
    URI MorseOverlay
    VERSION 1.0
    QML_FILES
        main.qml
        MorseOverlay.qml
        MorseLogic.qml
        TopBar.qml
        MainDisplay.qml
        ModeBar.qml
        SeqDisplay.qml
        KeyHints.qml
        ConfigPanel.qml
)

target_link_libraries(MorseOverlayApp PRIVATE Qt6::Quick)
