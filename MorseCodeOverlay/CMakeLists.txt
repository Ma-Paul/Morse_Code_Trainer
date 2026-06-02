cmake_minimum_required(VERSION 3.16)

project(MorseCodeOverlay VERSION 0.1 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Qt6 REQUIRED COMPONENTS Quick)

qt_standard_project_setup(REQUIRES 6.10)

qt_add_executable(appMorseCodeOverlay
    main.cpp
    appbridge.cpp
    appbridge.h
)

qt_add_qml_module(appMorseCodeOverlay
    URI MorseCodeOverlay
    QML_FILES
        Main.qml
        QML_FILES HomePage.qml
        QML_FILES Inputtype.qml
        QML_FILES Globalvariables.js
        QML_FILES Specifytype.qml
	QML_FILES Mode.qml
    RESOURCES
        Pause.jpg
        Long.png
        short.png
        Time.png
        Single.jpg
        Double.jpg
	Nextslide.png
	Previousslide.png
        RESOURCES main.py
        SOURCES appbridge.h
        SOURCES appbridge.cpp
        
)

# Qt for iOS sets MACOSX_BUNDLE_GUI_IDENTIFIER automatically since Qt 6.1.
# If you are developing for iOS or macOS you should consider setting an
# explicit, fixed bundle identifier manually though.
set_target_properties(appMorseCodeOverlay PROPERTIES
#    MACOSX_BUNDLE_GUI_IDENTIFIER com.example.appMorseCodeOverlay
    MACOSX_BUNDLE_BUNDLE_VERSION ${PROJECT_VERSION}
    MACOSX_BUNDLE_SHORT_VERSION_STRING ${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}
    MACOSX_BUNDLE TRUE
    WIN32_EXECUTABLE TRUE
)

target_link_libraries(appMorseCodeOverlay
    PRIVATE Qt6::Quick
)

install(TARGETS appMorseCodeOverlay
    BUNDLE DESTINATION .
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)
