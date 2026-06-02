#include "appbridge.h"

#include <QFile>
#include <QJsonDocument>
#include <QJsonObject>
#include <QStandardPaths>
#include <QDir>
#include <QDebug>

AppBridge::AppBridge(QObject *parent)
    : QObject(parent)
{
}

void AppBridge::saveSettings(
    const QString &eingabeart,
    const QString &lefttype,
    const QString &righttype,
    const QString &mode
    ) {
    QJsonObject data;
    data["eingabeart"] = eingabeart;
    data["lefttype"] = lefttype;
    data["righttype"] = righttype;
    data["mode"] = mode;

    QString folder = QStandardPaths::writableLocation(QStandardPaths::AppDataLocation);
    QDir().mkpath(folder);

    QString path = folder + "/settings.json";

    QFile file(path);
    if (!file.open(QIODevice::WriteOnly)) {
	qWarning() << "Could not open settings file:" << path;
	return;
    }

    file.write(QJsonDocument(data).toJson(QJsonDocument::Indented));
    file.close();

    qDebug() << "Saved settings to:" << path;
}