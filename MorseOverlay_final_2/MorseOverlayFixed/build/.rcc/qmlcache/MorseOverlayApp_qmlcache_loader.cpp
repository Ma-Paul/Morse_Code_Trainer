#include <QtQml/qqmlprivate.h>
#include <QtCore/qdir.h>
#include <QtCore/qurl.h>
#include <QtCore/qhash.h>
#include <QtCore/qstring.h>

namespace QmlCacheGeneratedCode {
namespace _0x5f_MorseOverlay_main_qml { 
    extern const unsigned char qmlData[];
    extern const QQmlPrivate::AOTCompiledFunction aotBuiltFunctions[];
    const QQmlPrivate::CachedQmlUnit unit = {
        reinterpret_cast<const QV4::CompiledData::Unit*>(&qmlData), &aotBuiltFunctions[0], nullptr
    };
}
namespace _0x5f_MorseOverlay_MorseOverlay_qml { 
    extern const unsigned char qmlData[];
    extern const QQmlPrivate::AOTCompiledFunction aotBuiltFunctions[];
    const QQmlPrivate::CachedQmlUnit unit = {
        reinterpret_cast<const QV4::CompiledData::Unit*>(&qmlData), &aotBuiltFunctions[0], nullptr
    };
}
namespace _0x5f_MorseOverlay_MorseLogic_qml { 
    extern const unsigned char qmlData[];
    extern const QQmlPrivate::AOTCompiledFunction aotBuiltFunctions[];
    const QQmlPrivate::CachedQmlUnit unit = {
        reinterpret_cast<const QV4::CompiledData::Unit*>(&qmlData), &aotBuiltFunctions[0], nullptr
    };
}
namespace _0x5f_MorseOverlay_TopBar_qml { 
    extern const unsigned char qmlData[];
    extern const QQmlPrivate::AOTCompiledFunction aotBuiltFunctions[];
    const QQmlPrivate::CachedQmlUnit unit = {
        reinterpret_cast<const QV4::CompiledData::Unit*>(&qmlData), &aotBuiltFunctions[0], nullptr
    };
}
namespace _0x5f_MorseOverlay_MainDisplay_qml { 
    extern const unsigned char qmlData[];
    extern const QQmlPrivate::AOTCompiledFunction aotBuiltFunctions[];
    const QQmlPrivate::CachedQmlUnit unit = {
        reinterpret_cast<const QV4::CompiledData::Unit*>(&qmlData), &aotBuiltFunctions[0], nullptr
    };
}
namespace _0x5f_MorseOverlay_ModeBar_qml { 
    extern const unsigned char qmlData[];
    extern const QQmlPrivate::AOTCompiledFunction aotBuiltFunctions[];
    const QQmlPrivate::CachedQmlUnit unit = {
        reinterpret_cast<const QV4::CompiledData::Unit*>(&qmlData), &aotBuiltFunctions[0], nullptr
    };
}
namespace _0x5f_MorseOverlay_SeqDisplay_qml { 
    extern const unsigned char qmlData[];
    extern const QQmlPrivate::AOTCompiledFunction aotBuiltFunctions[];
    const QQmlPrivate::CachedQmlUnit unit = {
        reinterpret_cast<const QV4::CompiledData::Unit*>(&qmlData), &aotBuiltFunctions[0], nullptr
    };
}
namespace _0x5f_MorseOverlay_KeyHints_qml { 
    extern const unsigned char qmlData[];
    extern const QQmlPrivate::AOTCompiledFunction aotBuiltFunctions[];
    const QQmlPrivate::CachedQmlUnit unit = {
        reinterpret_cast<const QV4::CompiledData::Unit*>(&qmlData), &aotBuiltFunctions[0], nullptr
    };
}
namespace _0x5f_MorseOverlay_ConfigPanel_qml { 
    extern const unsigned char qmlData[];
    extern const QQmlPrivate::AOTCompiledFunction aotBuiltFunctions[];
    const QQmlPrivate::CachedQmlUnit unit = {
        reinterpret_cast<const QV4::CompiledData::Unit*>(&qmlData), &aotBuiltFunctions[0], nullptr
    };
}

}
namespace {
struct Registry {
    Registry();
    ~Registry();
    QHash<QString, const QQmlPrivate::CachedQmlUnit*> resourcePathToCachedUnit;
    static const QQmlPrivate::CachedQmlUnit *lookupCachedUnit(const QUrl &url);
};

Q_GLOBAL_STATIC(Registry, unitRegistry)


Registry::Registry() {
    resourcePathToCachedUnit.insert(QStringLiteral("/MorseOverlay/main.qml"), &QmlCacheGeneratedCode::_0x5f_MorseOverlay_main_qml::unit);
    resourcePathToCachedUnit.insert(QStringLiteral("/MorseOverlay/MorseOverlay.qml"), &QmlCacheGeneratedCode::_0x5f_MorseOverlay_MorseOverlay_qml::unit);
    resourcePathToCachedUnit.insert(QStringLiteral("/MorseOverlay/MorseLogic.qml"), &QmlCacheGeneratedCode::_0x5f_MorseOverlay_MorseLogic_qml::unit);
    resourcePathToCachedUnit.insert(QStringLiteral("/MorseOverlay/TopBar.qml"), &QmlCacheGeneratedCode::_0x5f_MorseOverlay_TopBar_qml::unit);
    resourcePathToCachedUnit.insert(QStringLiteral("/MorseOverlay/MainDisplay.qml"), &QmlCacheGeneratedCode::_0x5f_MorseOverlay_MainDisplay_qml::unit);
    resourcePathToCachedUnit.insert(QStringLiteral("/MorseOverlay/ModeBar.qml"), &QmlCacheGeneratedCode::_0x5f_MorseOverlay_ModeBar_qml::unit);
    resourcePathToCachedUnit.insert(QStringLiteral("/MorseOverlay/SeqDisplay.qml"), &QmlCacheGeneratedCode::_0x5f_MorseOverlay_SeqDisplay_qml::unit);
    resourcePathToCachedUnit.insert(QStringLiteral("/MorseOverlay/KeyHints.qml"), &QmlCacheGeneratedCode::_0x5f_MorseOverlay_KeyHints_qml::unit);
    resourcePathToCachedUnit.insert(QStringLiteral("/MorseOverlay/ConfigPanel.qml"), &QmlCacheGeneratedCode::_0x5f_MorseOverlay_ConfigPanel_qml::unit);
    QQmlPrivate::RegisterQmlUnitCacheHook registration;
    registration.structVersion = 0;
    registration.lookupCachedQmlUnit = &lookupCachedUnit;
    QQmlPrivate::qmlregister(QQmlPrivate::QmlUnitCacheHookRegistration, &registration);
}

Registry::~Registry() {
    QQmlPrivate::qmlunregister(QQmlPrivate::QmlUnitCacheHookRegistration, quintptr(&lookupCachedUnit));
}

const QQmlPrivate::CachedQmlUnit *Registry::lookupCachedUnit(const QUrl &url) {
    if (url.scheme() != QLatin1String("qrc"))
        return nullptr;
    QString resourcePath = QDir::cleanPath(url.path());
    if (resourcePath.isEmpty())
        return nullptr;
    if (!resourcePath.startsWith(QLatin1Char('/')))
        resourcePath.prepend(QLatin1Char('/'));
    return unitRegistry()->resourcePathToCachedUnit.value(resourcePath, nullptr);
}
}
int QT_MANGLE_NAMESPACE(qInitResources_qmlcache_MorseOverlayApp)() {
    ::unitRegistry();
    return 1;
}
Q_CONSTRUCTOR_FUNCTION(QT_MANGLE_NAMESPACE(qInitResources_qmlcache_MorseOverlayApp))
int QT_MANGLE_NAMESPACE(qCleanupResources_qmlcache_MorseOverlayApp)() {
    return 1;
}
