/****************************************************************************
** Meta object code from reading C++ file 'viewer.h'
**
** Created by: The Qt Meta Object Compiler version 67 (Qt 5.15.10)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include <memory>
#include "../../../../../qt5/demos/viewer.h"
#include <QtCore/qbytearray.h>
#include <QtCore/qmetatype.h>
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'viewer.h' doesn't include <QObject>."
#elif Q_MOC_OUTPUT_REVISION != 67
#error "This file was generated using the moc from 5.15.10. It"
#error "cannot be used with the include files from this version of Qt."
#error "(The moc has changed too much.)"
#endif

QT_BEGIN_MOC_NAMESPACE
QT_WARNING_PUSH
QT_WARNING_DISABLE_DEPRECATED
struct qt_meta_stringdata_PdfViewer_t {
    QByteArrayData data[12];
    char stringdata0[129];
};
#define QT_MOC_LITERAL(idx, ofs, len) \
    Q_STATIC_BYTE_ARRAY_DATA_HEADER_INITIALIZER_WITH_OFFSET(len, \
    qptrdiff(offsetof(qt_meta_stringdata_PdfViewer_t, stringdata0) + ofs \
        - idx * sizeof(QByteArrayData)) \
    )
static const qt_meta_stringdata_PdfViewer_t qt_meta_stringdata_PdfViewer = {
    {
QT_MOC_LITERAL(0, 0, 9), // "PdfViewer"
QT_MOC_LITERAL(1, 10, 12), // "slotOpenFile"
QT_MOC_LITERAL(2, 23, 0), // ""
QT_MOC_LITERAL(3, 24, 12), // "slotSaveCopy"
QT_MOC_LITERAL(4, 37, 9), // "slotAbout"
QT_MOC_LITERAL(5, 47, 11), // "slotAboutQt"
QT_MOC_LITERAL(6, 59, 16), // "slotToggleTextAA"
QT_MOC_LITERAL(7, 76, 5), // "value"
QT_MOC_LITERAL(8, 82, 15), // "slotToggleGfxAA"
QT_MOC_LITERAL(9, 98, 17), // "slotRenderBackend"
QT_MOC_LITERAL(10, 116, 8), // "QAction*"
QT_MOC_LITERAL(11, 125, 3) // "act"

    },
    "PdfViewer\0slotOpenFile\0\0slotSaveCopy\0"
    "slotAbout\0slotAboutQt\0slotToggleTextAA\0"
    "value\0slotToggleGfxAA\0slotRenderBackend\0"
    "QAction*\0act"
};
#undef QT_MOC_LITERAL

static const uint qt_meta_data_PdfViewer[] = {

 // content:
       8,       // revision
       0,       // classname
       0,    0, // classinfo
       7,   14, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       0,       // signalCount

 // slots: name, argc, parameters, tag, flags
       1,    0,   49,    2, 0x08 /* Private */,
       3,    0,   50,    2, 0x08 /* Private */,
       4,    0,   51,    2, 0x08 /* Private */,
       5,    0,   52,    2, 0x08 /* Private */,
       6,    1,   53,    2, 0x08 /* Private */,
       8,    1,   56,    2, 0x08 /* Private */,
       9,    1,   59,    2, 0x08 /* Private */,

 // slots: parameters
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void, QMetaType::Bool,    7,
    QMetaType::Void, QMetaType::Bool,    7,
    QMetaType::Void, 0x80000000 | 10,   11,

       0        // eod
};

void PdfViewer::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    if (_c == QMetaObject::InvokeMetaMethod) {
        auto *_t = static_cast<PdfViewer *>(_o);
        (void)_t;
        switch (_id) {
        case 0: _t->slotOpenFile(); break;
        case 1: _t->slotSaveCopy(); break;
        case 2: _t->slotAbout(); break;
        case 3: _t->slotAboutQt(); break;
        case 4: _t->slotToggleTextAA((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 5: _t->slotToggleGfxAA((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 6: _t->slotRenderBackend((*reinterpret_cast< QAction*(*)>(_a[1]))); break;
        default: ;
        }
    }
}

QT_INIT_METAOBJECT const QMetaObject PdfViewer::staticMetaObject = { {
    QMetaObject::SuperData::link<QMainWindow::staticMetaObject>(),
    qt_meta_stringdata_PdfViewer.data,
    qt_meta_data_PdfViewer,
    qt_static_metacall,
    nullptr,
    nullptr
} };


const QMetaObject *PdfViewer::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->dynamicMetaObject() : &staticMetaObject;
}

void *PdfViewer::qt_metacast(const char *_clname)
{
    if (!_clname) return nullptr;
    if (!strcmp(_clname, qt_meta_stringdata_PdfViewer.stringdata0))
        return static_cast<void*>(this);
    return QMainWindow::qt_metacast(_clname);
}

int PdfViewer::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = QMainWindow::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        if (_id < 7)
            qt_static_metacall(this, _c, _id, _a);
        _id -= 7;
    } else if (_c == QMetaObject::RegisterMethodArgumentMetaType) {
        if (_id < 7)
            *reinterpret_cast<int*>(_a[0]) = -1;
        _id -= 7;
    }
    return _id;
}
QT_WARNING_POP
QT_END_MOC_NAMESPACE
