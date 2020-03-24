/********************************************************************************
** Form generated from reading UI file 'mainwindow.ui'
**
** Created by: Qt User Interface Compiler version 5.9.5
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef UI_MAINWINDOW_H
#define UI_MAINWINDOW_H

#include <QtCore/QVariant>
#include <QtWidgets/QAction>
#include <QtWidgets/QApplication>
#include <QtWidgets/QButtonGroup>
#include <QtWidgets/QComboBox>
#include <QtWidgets/QDockWidget>
#include <QtWidgets/QGridLayout>
#include <QtWidgets/QHBoxLayout>
#include <QtWidgets/QHeaderView>
#include <QtWidgets/QLabel>
#include <QtWidgets/QLineEdit>
#include <QtWidgets/QListWidget>
#include <QtWidgets/QMainWindow>
#include <QtWidgets/QMenu>
#include <QtWidgets/QMenuBar>
#include <QtWidgets/QPushButton>
#include <QtWidgets/QSpacerItem>
#include <QtWidgets/QSplitter>
#include <QtWidgets/QStatusBar>
#include <QtWidgets/QTabWidget>
#include <QtWidgets/QToolBar>
#include <QtWidgets/QTreeWidget>
#include <QtWidgets/QVBoxLayout>
#include <QtWidgets/QWidget>

QT_BEGIN_NAMESPACE

class Ui_MainWindow
{
public:
    QAction *actionOpen;
    QAction *actionExit;
    QAction *actionAbout;
    QAction *actionPrevious;
    QAction *actionNext;
    QAction *actionSetIDB;
    QAction *actionSave;
    QAction *actionLog;
    QAction *actionPlot;
    QAction *actionPaste;
    QAction *actionLoadMongodb;
    QAction *actionCopy;
    QAction *actionConnectTSC;
    QAction *actionPacketFilter;
    QAction *actionPlugins;
    QAction *actionOnlineHelp;
    QAction *actionViewBinary;
    QWidget *centralwidget;
    QHBoxLayout *horizontalLayout;
    QTabWidget *tabWidget;
    QWidget *packetTab;
    QHBoxLayout *horizontalLayout_2;
    QSplitter *splitter_3;
    QSplitter *splitter_2;
    QTreeWidget *packetTreeWidget;
    QSplitter *splitter;
    QTreeWidget *paramTreeWidget;
    QWidget *plotTab;
    QVBoxLayout *verticalLayout;
    QGridLayout *gridLayout;
    QComboBox *xaxisComboBox;
    QLabel *label;
    QLabel *label_2;
    QLineEdit *styleEdit;
    QSpacerItem *horizontalSpacer;
    QLabel *label_4;
    QLineEdit *paramNameEdit;
    QComboBox *comboBox;
    QLabel *descLabel;
    QLabel *label_3;
    QPushButton *plotButton;
    QPushButton *savePlotButton;
    QComboBox *dataTypeComboBox;
    QPushButton *exportButton;
    QMenuBar *menubar;
    QMenu *menu_File;
    QMenu *menu_Help;
    QMenu *menuSetting;
    QMenu *menu_Tools;
    QMenu *menuAction;
    QMenu *menuEdit;
    QStatusBar *statusbar;
    QToolBar *toolBar;
    QDockWidget *dockWidget;
    QWidget *dockWidgetContents_2;
    QHBoxLayout *horizontalLayout_3;
    QListWidget *statusListWidget;

    void setupUi(QMainWindow *MainWindow)
    {
        if (MainWindow->objectName().isEmpty())
            MainWindow->setObjectName(QStringLiteral("MainWindow"));
        MainWindow->setWindowModality(Qt::WindowModal);
        MainWindow->resize(1376, 1044);
        MainWindow->setMaximumSize(QSize(323232, 323232));
        QIcon icon;
        icon.addFile(QStringLiteral(":/Icons/images/app.svg"), QSize(), QIcon::Normal, QIcon::Off);
        MainWindow->setWindowIcon(icon);
        actionOpen = new QAction(MainWindow);
        actionOpen->setObjectName(QStringLiteral("actionOpen"));
        actionExit = new QAction(MainWindow);
        actionExit->setObjectName(QStringLiteral("actionExit"));
        actionAbout = new QAction(MainWindow);
        actionAbout->setObjectName(QStringLiteral("actionAbout"));
        actionPrevious = new QAction(MainWindow);
        actionPrevious->setObjectName(QStringLiteral("actionPrevious"));
        actionPrevious->setMenuRole(QAction::AboutQtRole);
        actionNext = new QAction(MainWindow);
        actionNext->setObjectName(QStringLiteral("actionNext"));
        actionSetIDB = new QAction(MainWindow);
        actionSetIDB->setObjectName(QStringLiteral("actionSetIDB"));
        actionSave = new QAction(MainWindow);
        actionSave->setObjectName(QStringLiteral("actionSave"));
        actionLog = new QAction(MainWindow);
        actionLog->setObjectName(QStringLiteral("actionLog"));
        actionPlot = new QAction(MainWindow);
        actionPlot->setObjectName(QStringLiteral("actionPlot"));
        QIcon icon1;
        icon1.addFile(QStringLiteral(":/Icons/images/graph.svg"), QSize(), QIcon::Normal, QIcon::Off);
        actionPlot->setIcon(icon1);
        actionPaste = new QAction(MainWindow);
        actionPaste->setObjectName(QStringLiteral("actionPaste"));
        QIcon icon2;
        icon2.addFile(QStringLiteral(":/Icons/images/paste.svg"), QSize(), QIcon::Normal, QIcon::Off);
        actionPaste->setIcon(icon2);
        actionLoadMongodb = new QAction(MainWindow);
        actionLoadMongodb->setObjectName(QStringLiteral("actionLoadMongodb"));
        QIcon icon3;
        icon3.addFile(QStringLiteral(":/Icons/images/mongodb.svg"), QSize(), QIcon::Normal, QIcon::Off);
        actionLoadMongodb->setIcon(icon3);
        actionCopy = new QAction(MainWindow);
        actionCopy->setObjectName(QStringLiteral("actionCopy"));
        QIcon icon4;
        icon4.addFile(QStringLiteral(":/Icons/images/copy.svg"), QSize(), QIcon::Normal, QIcon::Off);
        actionCopy->setIcon(icon4);
        actionConnectTSC = new QAction(MainWindow);
        actionConnectTSC->setObjectName(QStringLiteral("actionConnectTSC"));
        QIcon icon5;
        icon5.addFile(QStringLiteral(":/Icons/images/link.svg"), QSize(), QIcon::Normal, QIcon::Off);
        actionConnectTSC->setIcon(icon5);
        actionPacketFilter = new QAction(MainWindow);
        actionPacketFilter->setObjectName(QStringLiteral("actionPacketFilter"));
        QIcon icon6;
        icon6.addFile(QStringLiteral(":/Icons/images/filter.svg"), QSize(), QIcon::Normal, QIcon::Off);
        actionPacketFilter->setIcon(icon6);
        actionPlugins = new QAction(MainWindow);
        actionPlugins->setObjectName(QStringLiteral("actionPlugins"));
        QIcon icon7;
        icon7.addFile(QStringLiteral(":/Icons/images/plugin.svg"), QSize(), QIcon::Normal, QIcon::Off);
        actionPlugins->setIcon(icon7);
        actionOnlineHelp = new QAction(MainWindow);
        actionOnlineHelp->setObjectName(QStringLiteral("actionOnlineHelp"));
        actionViewBinary = new QAction(MainWindow);
        actionViewBinary->setObjectName(QStringLiteral("actionViewBinary"));
        QIcon icon8;
        icon8.addFile(QStringLiteral(":/Icons/images/binary.svg"), QSize(), QIcon::Normal, QIcon::Off);
        actionViewBinary->setIcon(icon8);
        centralwidget = new QWidget(MainWindow);
        centralwidget->setObjectName(QStringLiteral("centralwidget"));
        horizontalLayout = new QHBoxLayout(centralwidget);
        horizontalLayout->setObjectName(QStringLiteral("horizontalLayout"));
        tabWidget = new QTabWidget(centralwidget);
        tabWidget->setObjectName(QStringLiteral("tabWidget"));
        tabWidget->setBaseSize(QSize(0, 0));
        packetTab = new QWidget();
        packetTab->setObjectName(QStringLiteral("packetTab"));
        QSizePolicy sizePolicy(QSizePolicy::Expanding, QSizePolicy::Expanding);
        sizePolicy.setHorizontalStretch(0);
        sizePolicy.setVerticalStretch(0);
        sizePolicy.setHeightForWidth(packetTab->sizePolicy().hasHeightForWidth());
        packetTab->setSizePolicy(sizePolicy);
        horizontalLayout_2 = new QHBoxLayout(packetTab);
        horizontalLayout_2->setObjectName(QStringLiteral("horizontalLayout_2"));
        splitter_3 = new QSplitter(packetTab);
        splitter_3->setObjectName(QStringLiteral("splitter_3"));
        splitter_3->setOrientation(Qt::Horizontal);
        splitter_2 = new QSplitter(splitter_3);
        splitter_2->setObjectName(QStringLiteral("splitter_2"));
        splitter_2->setOrientation(Qt::Horizontal);
        packetTreeWidget = new QTreeWidget(splitter_2);
        QTreeWidgetItem *__qtreewidgetitem = new QTreeWidgetItem();
        __qtreewidgetitem->setText(0, QStringLiteral("Timestamp"));
        packetTreeWidget->setHeaderItem(__qtreewidgetitem);
        packetTreeWidget->setObjectName(QStringLiteral("packetTreeWidget"));
        packetTreeWidget->setMinimumSize(QSize(0, 0));
        packetTreeWidget->setMaximumSize(QSize(1000000, 16777215));
        packetTreeWidget->setSizeAdjustPolicy(QAbstractScrollArea::AdjustToContents);
        packetTreeWidget->setWordWrap(false);
        splitter_2->addWidget(packetTreeWidget);
        splitter_3->addWidget(splitter_2);
        splitter = new QSplitter(splitter_3);
        splitter->setObjectName(QStringLiteral("splitter"));
        splitter->setOrientation(Qt::Vertical);
        paramTreeWidget = new QTreeWidget(splitter);
        QTreeWidgetItem *__qtreewidgetitem1 = new QTreeWidgetItem();
        __qtreewidgetitem1->setText(0, QStringLiteral("Name"));
        paramTreeWidget->setHeaderItem(__qtreewidgetitem1);
        paramTreeWidget->setObjectName(QStringLiteral("paramTreeWidget"));
        paramTreeWidget->setAutoExpandDelay(-1);
        paramTreeWidget->setUniformRowHeights(true);
        splitter->addWidget(paramTreeWidget);
        paramTreeWidget->header()->setCascadingSectionResizes(false);
        paramTreeWidget->header()->setDefaultSectionSize(170);
        paramTreeWidget->header()->setHighlightSections(true);
        splitter_3->addWidget(splitter);

        horizontalLayout_2->addWidget(splitter_3);

        tabWidget->addTab(packetTab, QString());
        plotTab = new QWidget();
        plotTab->setObjectName(QStringLiteral("plotTab"));
        sizePolicy.setHeightForWidth(plotTab->sizePolicy().hasHeightForWidth());
        plotTab->setSizePolicy(sizePolicy);
        verticalLayout = new QVBoxLayout(plotTab);
        verticalLayout->setObjectName(QStringLiteral("verticalLayout"));
        gridLayout = new QGridLayout();
        gridLayout->setObjectName(QStringLiteral("gridLayout"));
        xaxisComboBox = new QComboBox(plotTab);
        xaxisComboBox->setObjectName(QStringLiteral("xaxisComboBox"));

        gridLayout->addWidget(xaxisComboBox, 0, 1, 1, 1);

        label = new QLabel(plotTab);
        label->setObjectName(QStringLiteral("label"));

        gridLayout->addWidget(label, 0, 2, 1, 1);

        label_2 = new QLabel(plotTab);
        label_2->setObjectName(QStringLiteral("label_2"));

        gridLayout->addWidget(label_2, 0, 4, 1, 1);

        styleEdit = new QLineEdit(plotTab);
        styleEdit->setObjectName(QStringLiteral("styleEdit"));
        styleEdit->setMaximumSize(QSize(40, 16777215));

        gridLayout->addWidget(styleEdit, 0, 9, 1, 1);

        horizontalSpacer = new QSpacerItem(25, 17, QSizePolicy::Expanding, QSizePolicy::Minimum);

        gridLayout->addItem(horizontalSpacer, 0, 10, 1, 1);

        label_4 = new QLabel(plotTab);
        label_4->setObjectName(QStringLiteral("label_4"));

        gridLayout->addWidget(label_4, 0, 0, 1, 1);

        paramNameEdit = new QLineEdit(plotTab);
        paramNameEdit->setObjectName(QStringLiteral("paramNameEdit"));
        paramNameEdit->setMaximumSize(QSize(150, 16777215));

        gridLayout->addWidget(paramNameEdit, 0, 3, 1, 1);

        comboBox = new QComboBox(plotTab);
        comboBox->setObjectName(QStringLiteral("comboBox"));
        comboBox->setMinimumSize(QSize(120, 0));
        comboBox->setMaximumSize(QSize(150, 16777215));
        comboBox->setModelColumn(0);

        gridLayout->addWidget(comboBox, 0, 5, 1, 1);

        descLabel = new QLabel(plotTab);
        descLabel->setObjectName(QStringLiteral("descLabel"));
        descLabel->setMinimumSize(QSize(0, 0));
        descLabel->setMaximumSize(QSize(0, 16777215));

        gridLayout->addWidget(descLabel, 0, 6, 1, 1);

        label_3 = new QLabel(plotTab);
        label_3->setObjectName(QStringLiteral("label_3"));

        gridLayout->addWidget(label_3, 0, 8, 1, 1);

        plotButton = new QPushButton(plotTab);
        plotButton->setObjectName(QStringLiteral("plotButton"));
        plotButton->setMaximumSize(QSize(100, 16777215));

        gridLayout->addWidget(plotButton, 0, 11, 1, 1);

        savePlotButton = new QPushButton(plotTab);
        savePlotButton->setObjectName(QStringLiteral("savePlotButton"));
        savePlotButton->setMaximumSize(QSize(100, 16777215));

        gridLayout->addWidget(savePlotButton, 0, 12, 1, 1);

        dataTypeComboBox = new QComboBox(plotTab);
        dataTypeComboBox->setObjectName(QStringLiteral("dataTypeComboBox"));

        gridLayout->addWidget(dataTypeComboBox, 0, 7, 1, 1);

        exportButton = new QPushButton(plotTab);
        exportButton->setObjectName(QStringLiteral("exportButton"));

        gridLayout->addWidget(exportButton, 0, 13, 1, 1);


        verticalLayout->addLayout(gridLayout);

        tabWidget->addTab(plotTab, QString());

        horizontalLayout->addWidget(tabWidget);

        MainWindow->setCentralWidget(centralwidget);
        menubar = new QMenuBar(MainWindow);
        menubar->setObjectName(QStringLiteral("menubar"));
        menubar->setGeometry(QRect(0, 0, 1376, 22));
        menu_File = new QMenu(menubar);
        menu_File->setObjectName(QStringLiteral("menu_File"));
        menu_Help = new QMenu(menubar);
        menu_Help->setObjectName(QStringLiteral("menu_Help"));
        menuSetting = new QMenu(menubar);
        menuSetting->setObjectName(QStringLiteral("menuSetting"));
        menu_Tools = new QMenu(menubar);
        menu_Tools->setObjectName(QStringLiteral("menu_Tools"));
        menuAction = new QMenu(menubar);
        menuAction->setObjectName(QStringLiteral("menuAction"));
        menuEdit = new QMenu(menubar);
        menuEdit->setObjectName(QStringLiteral("menuEdit"));
        MainWindow->setMenuBar(menubar);
        statusbar = new QStatusBar(MainWindow);
        statusbar->setObjectName(QStringLiteral("statusbar"));
        MainWindow->setStatusBar(statusbar);
        toolBar = new QToolBar(MainWindow);
        toolBar->setObjectName(QStringLiteral("toolBar"));
        MainWindow->addToolBar(Qt::TopToolBarArea, toolBar);
        dockWidget = new QDockWidget(MainWindow);
        dockWidget->setObjectName(QStringLiteral("dockWidget"));
        dockWidgetContents_2 = new QWidget();
        dockWidgetContents_2->setObjectName(QStringLiteral("dockWidgetContents_2"));
        horizontalLayout_3 = new QHBoxLayout(dockWidgetContents_2);
        horizontalLayout_3->setObjectName(QStringLiteral("horizontalLayout_3"));
        statusListWidget = new QListWidget(dockWidgetContents_2);
        statusListWidget->setObjectName(QStringLiteral("statusListWidget"));

        horizontalLayout_3->addWidget(statusListWidget);

        dockWidget->setWidget(dockWidgetContents_2);
        MainWindow->addDockWidget(static_cast<Qt::DockWidgetArea>(8), dockWidget);

        menubar->addAction(menu_File->menuAction());
        menubar->addAction(menuEdit->menuAction());
        menubar->addAction(menuAction->menuAction());
        menubar->addAction(menuSetting->menuAction());
        menubar->addAction(menu_Tools->menuAction());
        menubar->addAction(menu_Help->menuAction());
        menu_File->addAction(actionOpen);
        menu_File->addAction(actionSave);
        menu_File->addAction(actionExit);
        menu_Help->addAction(actionOnlineHelp);
        menu_Help->addAction(actionAbout);
        menuSetting->addAction(actionSetIDB);
        menu_Tools->addAction(actionPlot);
        menu_Tools->addAction(actionLoadMongodb);
        menu_Tools->addAction(actionConnectTSC);
        menu_Tools->addAction(actionPacketFilter);
        menu_Tools->addAction(actionPlugins);
        menu_Tools->addAction(actionViewBinary);
        menuAction->addAction(actionPrevious);
        menuAction->addAction(actionNext);
        menuAction->addAction(actionLog);
        menuEdit->addAction(actionPaste);
        menuEdit->addAction(actionCopy);
        toolBar->addAction(actionOpen);
        toolBar->addAction(actionSave);
        toolBar->addSeparator();
        toolBar->addAction(actionPrevious);
        toolBar->addAction(actionNext);
        toolBar->addSeparator();
        toolBar->addAction(actionPaste);
        toolBar->addAction(actionCopy);
        toolBar->addSeparator();
        toolBar->addAction(actionPlugins);
        toolBar->addAction(actionPacketFilter);
        toolBar->addSeparator();
        toolBar->addAction(actionPlot);
        toolBar->addSeparator();
        toolBar->addAction(actionLoadMongodb);
        toolBar->addAction(actionConnectTSC);
        toolBar->addAction(actionViewBinary);

        retranslateUi(MainWindow);

        tabWidget->setCurrentIndex(0);


        QMetaObject::connectSlotsByName(MainWindow);
    } // setupUi

    void retranslateUi(QMainWindow *MainWindow)
    {
        MainWindow->setWindowTitle(QApplication::translate("MainWindow", "STIX data parser and viewer", Q_NULLPTR));
        actionOpen->setText(QApplication::translate("MainWindow", "&Open", Q_NULLPTR));
        actionExit->setText(QApplication::translate("MainWindow", "&Exit", Q_NULLPTR));
        actionAbout->setText(QApplication::translate("MainWindow", "About", Q_NULLPTR));
        actionPrevious->setText(QApplication::translate("MainWindow", "Previous", Q_NULLPTR));
        actionNext->setText(QApplication::translate("MainWindow", "Next", Q_NULLPTR));
        actionSetIDB->setText(QApplication::translate("MainWindow", "Set &IDB", Q_NULLPTR));
        actionSave->setText(QApplication::translate("MainWindow", "Sa&ve", Q_NULLPTR));
        actionLog->setText(QApplication::translate("MainWindow", "Show Log", Q_NULLPTR));
        actionPlot->setText(QApplication::translate("MainWindow", "&Plot", Q_NULLPTR));
        actionPaste->setText(QApplication::translate("MainWindow", "P&aste", Q_NULLPTR));
#ifndef QT_NO_TOOLTIP
        actionPaste->setToolTip(QApplication::translate("MainWindow", "Read raw data from the clipboard", Q_NULLPTR));
#endif // QT_NO_TOOLTIP
        actionLoadMongodb->setText(QApplication::translate("MainWindow", "Connect MonogoDB", Q_NULLPTR));
        actionCopy->setText(QApplication::translate("MainWindow", "&Copy", Q_NULLPTR));
        actionConnectTSC->setText(QApplication::translate("MainWindow", "Connect to TSC", Q_NULLPTR));
        actionPacketFilter->setText(QApplication::translate("MainWindow", "Packet Filter", Q_NULLPTR));
        actionPlugins->setText(QApplication::translate("MainWindow", "Plugin manager", Q_NULLPTR));
        actionOnlineHelp->setText(QApplication::translate("MainWindow", "Online help", Q_NULLPTR));
        actionViewBinary->setText(QApplication::translate("MainWindow", "Packet binary data", Q_NULLPTR));
        actionViewBinary->setIconText(QApplication::translate("MainWindow", "Binary data viewer", Q_NULLPTR));
#ifndef QT_NO_TOOLTIP
        actionViewBinary->setToolTip(QApplication::translate("MainWindow", "Binary data viewer", Q_NULLPTR));
#endif // QT_NO_TOOLTIP
        QTreeWidgetItem *___qtreewidgetitem = packetTreeWidget->headerItem();
        ___qtreewidgetitem->setText(1, QApplication::translate("MainWindow", "Description", Q_NULLPTR));
        QTreeWidgetItem *___qtreewidgetitem1 = paramTreeWidget->headerItem();
        ___qtreewidgetitem1->setText(3, QApplication::translate("MainWindow", "Eng. Value", Q_NULLPTR));
        ___qtreewidgetitem1->setText(2, QApplication::translate("MainWindow", "Raw", Q_NULLPTR));
        ___qtreewidgetitem1->setText(1, QApplication::translate("MainWindow", "Description", Q_NULLPTR));
        tabWidget->setTabText(tabWidget->indexOf(packetTab), QApplication::translate("MainWindow", "Packets", Q_NULLPTR));
#ifndef QT_NO_TOOLTIP
        plotTab->setToolTip(QApplication::translate("MainWindow", "plot parameters\n"
"", Q_NULLPTR));
#endif // QT_NO_TOOLTIP
        xaxisComboBox->clear();
        xaxisComboBox->insertItems(0, QStringList()
         << QApplication::translate("MainWindow", "Parameter repeat # as X", Q_NULLPTR)
         << QApplication::translate("MainWindow", "Timestamp - T0 as X", Q_NULLPTR)
         << QApplication::translate("MainWindow", "Histogram", Q_NULLPTR)
        );
        label->setText(QApplication::translate("MainWindow", "Data source:", Q_NULLPTR));
        label_2->setText(QApplication::translate("MainWindow", "In", Q_NULLPTR));
        styleEdit->setText(QApplication::translate("MainWindow", "-", Q_NULLPTR));
        label_4->setText(QApplication::translate("MainWindow", "Type:", Q_NULLPTR));
        comboBox->clear();
        comboBox->insertItems(0, QStringList()
         << QApplication::translate("MainWindow", "the same packet", Q_NULLPTR)
         << QApplication::translate("MainWindow", "all loaded packets", Q_NULLPTR)
        );
        descLabel->setText(QString());
        label_3->setText(QApplication::translate("MainWindow", "Curve Style:", Q_NULLPTR));
        plotButton->setText(QApplication::translate("MainWindow", "Plot", Q_NULLPTR));
        savePlotButton->setText(QApplication::translate("MainWindow", "Save", Q_NULLPTR));
        dataTypeComboBox->clear();
        dataTypeComboBox->insertItems(0, QStringList()
         << QApplication::translate("MainWindow", "Raw values", Q_NULLPTR)
         << QApplication::translate("MainWindow", "Engineering values", Q_NULLPTR)
        );
        exportButton->setText(QApplication::translate("MainWindow", "Export data", Q_NULLPTR));
        tabWidget->setTabText(tabWidget->indexOf(plotTab), QApplication::translate("MainWindow", "Plot", Q_NULLPTR));
        menu_File->setTitle(QApplication::translate("MainWindow", "&File", Q_NULLPTR));
        menu_Help->setTitle(QApplication::translate("MainWindow", "&Help", Q_NULLPTR));
        menuSetting->setTitle(QApplication::translate("MainWindow", "&Settings", Q_NULLPTR));
        menu_Tools->setTitle(QApplication::translate("MainWindow", "&Tools", Q_NULLPTR));
        menuAction->setTitle(QApplication::translate("MainWindow", "&View", Q_NULLPTR));
        menuEdit->setTitle(QApplication::translate("MainWindow", "&Edit", Q_NULLPTR));
        toolBar->setWindowTitle(QApplication::translate("MainWindow", "toolBar", Q_NULLPTR));
        dockWidget->setWindowTitle(QApplication::translate("MainWindow", "Log", Q_NULLPTR));
    } // retranslateUi

};

namespace Ui {
    class MainWindow: public Ui_MainWindow {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_MAINWINDOW_H
