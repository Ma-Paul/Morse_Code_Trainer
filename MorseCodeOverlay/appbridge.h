#ifndef APPBRIDGE_H
#define APPBRIDGE_H

#include <QObject>

class AppBridge : public QObject
{
    Q_OBJECT

  public:
    explicit AppBridge(QObject *parent = nullptr);

    Q_INVOKABLE void saveSettings(
	const QString &eingabeart,
	const QString &lefttype,
	const QString &righttype,
	const QString &mode
	);
};

#endif