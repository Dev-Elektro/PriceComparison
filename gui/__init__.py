# -*- coding: utf-8 -*-

import os, sys
import win32net, pywintypes
from PyQt5 import QtCore, QtWidgets, QtGui
from . import mainwindow
from .requestsearch import requestsearch


class App(QtWidgets.QMainWindow, mainwindow.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle(f'Сравнение цен')
        self.butSearch.clicked.connect(self.startSearch)
        self.progressBar.hide()
        self.textBrowser.setOpenExternalLinks(True)

    def startSearch(self):
        if len(self.lineSearch.text()) < 3:
            return
        self.thread = QtCore.QThread()
        self.request = requestsearch(self.lineSearch.text())
        self.request.moveToThread(self.thread)
        self.thread.started.connect(self.request.run)
        self.request.startSearch.connect(self.resultFrom)
        self.request.found.connect(self.foundSearch)
        self.request.finished.connect(self.finishSearch)
        self.request.finished.connect(self.thread.quit)
        self.request.finished.connect(self.request.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.butSearch.setText('Стоп')
        self.butSearch.clicked.disconnect()
        self.butSearch.clicked.connect(self.stopSearch)
        self.textBrowser.setTextInteractionFlags (QtCore.Qt.NoTextInteraction)
        self.textBrowser.clear()
        self.thread.start()
        self.statusbar.showMessage(f"Поиск: {self.lineSearch.text()}")
        self.progressBar.setMaximum(0)
        self.progressBar.setValue(0)
        self.progressBar.show()

    def closeEvent(self, event):
        try:
            self.request.stop()
            self.hide()
            self.thread.quit()
            self.thread.wait(30000)
        except Exception:
            pass
        event.accept()

    def stopSearch(self):
        self.request.stop()
        self.butSearch.setText('Остановка')
        self.statusbar.showMessage("Остановка поиска")

    def finishSearch(self, res):
        self.progressBar.hide()
        self.butSearch.setText('Поиск')
        self.butSearch.clicked.disconnect()
        self.butSearch.clicked.connect(self.startSearch)
        self.textBrowser.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse | QtCore.Qt.TextSelectableByKeyboard | QtCore.Qt.TextBrowserInteraction)
        self.statusbar.showMessage("Поиск завершен")
        if not res:
            self.textBrowser.insertHtml(f"<br><b>Поиск прерван</b><br>")

    def resultFrom(self, name):
        if self.textBrowser.toPlainText():
            self.textBrowser.insertHtml(f"<br>")
        self.textBrowser.insertHtml(f"<b>Результат с сайта {name}</b><br><br>")
        self.progressBar.setMaximum(3)
        self.progressBar.setValue(self.progressBar.value() + 1)

    def foundSearch(self, res):
        if not res:
            self.textBrowser.insertHtml(f"Нет результата.<br><br>")
            return
        self.textBrowser.insertHtml(f"<a href='{res.get('url')}'>{res.get('name')} - Цена: {res.get('price')}</a><br>")

def startGUI():
    app = QtWidgets.QApplication(sys.argv)
    translator = QtCore.QTranslator()
    if hasattr(sys, '_MEIPASS'):
        if translator.load(os.path.join(sys._MEIPASS, "qtbase_ru.qm")):
            app.installTranslator(translator)
    window = App()
    window.show()

    app.exec_()
