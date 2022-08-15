# -*- coding: utf-8 -*-

import os, sys
from PyQt5 import QtCore
sys.path.append("..")
from searchSite import Driver, citilink, regard, dnsshop, ozon

class requestsearch(QtCore.QObject):
    finished = QtCore.pyqtSignal(object)
    found = QtCore.pyqtSignal(object)
    startSearch = QtCore.pyqtSignal(object)

    def __init__(self, request):
        super().__init__()
        self.request = request
        self.stoped = False
        self._mutex = QtCore.QMutex()
        self.driver = Driver(headless = False)

    def stop(self):
        self._mutex.lock()
        self.stoped = True
        self._mutex.unlock()

    def _stopSearch(self):
        self.driver.stop()
        self.finished.emit(False)

    def run(self):
        self.driver.start()

        if self.stoped: return self._stopSearch()
        buf = citilink.search(self.driver, self.request)
        self.startSearch.emit("citilink.ru")
        # try:
        #     self.found.emit(next(buf))
        # except Exception as e:
        #     self.found.emit(None)
        f = False
        for res in buf:
            if self.stoped: return self._stopSearch()
            f = True
            self.found.emit(res)
        if not f:
            self.found.emit(None)

        if self.stoped: return self._stopSearch()
        buf = regard.search(self.driver, self.request)
        self.startSearch.emit('regard.ru')
        # try:
        #     self.found.emit(next(buf))
        # except Exception as e:
        #     self.found.emit(None)
        f = False
        for res in buf:
            if self.stoped: return self._stopSearch()
            f = True
            self.found.emit(res)
        if not f:
            self.found.emit(None)

        if self.stoped: return self._stopSearch()
        buf = dnsshop.search(self.driver, self.request)
        self.startSearch.emit('dns-shop.ru')
        # try:
        #     self.found.emit(next(buf))
        # except Exception as e:
        #     self.found.emit(None)
        f = False
        for res in buf:
            if self.stoped: return self._stopSearch()
            f = True
            self.found.emit(res)
        if not f:
            self.found.emit(None)
        self.driver.stop()
        self.finished.emit(True)
