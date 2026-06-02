#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QQmlContext>
#include "appbridge.h"
int
main(int argc, char *argv[])
{
    qputenv("QT_IM_MODULE", QByteArray("qtvirtualkeyboard"));

    QGuiApplication app(argc, argv);

    QQmlApplicationEngine engine;
    QObject::connect(
	&engine, &QQmlApplicationEngine::objectCreationFailed, &app,
	[]() { QCoreApplication::exit(-1); }, Qt::QueuedConnection);
    AppBridge appBridge;

    engine.rootContext()->setContextProperty("AppBridge", &appBridge);
    engine.loadFromModule("MorseCodeOverlay", "Main");

    return QCoreApplication::exec();
}
