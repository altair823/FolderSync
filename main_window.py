import sys
from time import sleep

from PyQt5 import uic
from PyQt5.QtCore import QThreadPool, QTimer, QRunnable, pyqtSlot, QObject, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox
from history_io import History
from file_sync import FileSync
from os import path, scandir
from MainWindows import Ui_MainWindow

#TempMainWindowUI = uic.loadUiType("MainWindows.ui")[0]


class _Signal(QObject):
    progress = pyqtSignal(int)

def get_dir_size(path='.'):
    total = 0
    with scandir(path) as it:
        for entry in it:
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_dir_size(entry.path)
    return total

class _ProgressBar(QRunnable):
    def __init__(self, fromLoc, destLoc):
        super().__init__()
        self.signal = _Signal()
        self.fromLoc = fromLoc
        self.destLoc = destLoc

    @pyqtSlot()
    def run(self):
        sleep(0.01)
        originSize = get_dir_size(self.fromLoc)
        destSize = 0
        while originSize > destSize:
            destSize = get_dir_size(self.destLoc)
            percent = destSize / originSize * 100
            self.signal.progress.emit(percent)
            print(percent)
            sleep(0.01)



class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.historyList = History.loadHistory()
        self.fromList = self.historyList['original']
        self.destList = self.historyList['destination']
        for item in self.fromList:
            self.comboBoxFrom.addItem(item)
        for item in self.destList:
            self.comboBoxDest.addItem(item)

        self.threadpool = QThreadPool()
        self.timer = QTimer()

        self.pushButtonAddFrom.clicked.connect(self.AddFromLocation)
        self.pushButtonAddDest.clicked.connect(self.AddDestLocation)

        self.pushButtonDeleteFrom.clicked.connect(self.DelFromLocation)
        self.pushButtonDeleteDest.clicked.connect(self.DelDestLocation)

        self.pushButtonClearFrom.clicked.connect(self.ClearFromLocation)
        self.pushButtonClearDest.clicked.connect(self.ClearDestLocation)

        self.isSyncing = False
        self.pushButtonSync.clicked.connect(self.Synchronize)

    def AddFromLocation(self):
        newLoc = QFileDialog.getExistingDirectory(self, 'Open Directory', './')
        if self.comboBoxFrom.findText(newLoc) != -1:
            QMessageBox.information(self, 'Message', '이미 존재하는 경로입니다.')
            return
        self.fromList.append(newLoc)
        self.comboBoxFrom.addItem(newLoc)
        index = self.comboBoxFrom.findText(newLoc)
        self.comboBoxFrom.setCurrentIndex(index)

    def AddDestLocation(self):
        newLoc = QFileDialog.getExistingDirectory(self, 'Open Directory', './')
        if self.comboBoxDest.findText(newLoc) != -1:
            QMessageBox.information(self, 'Message', '이미 존재하는 경로입니다.')
            return
        self.destList.append(newLoc)
        self.comboBoxDest.addItem(newLoc)
        index = self.comboBoxDest.findText(newLoc)
        self.comboBoxDest.setCurrentIndex(index)

    def DelFromLocation(self):
        self.fromList.remove(self.comboBoxFrom.currentText())
        self.comboBoxFrom.removeItem(self.comboBoxFrom.currentIndex())

    def DelDestLocation(self):
        self.destList.remove(self.comboBoxDest.currentText())
        self.comboBoxDest.removeItem(self.comboBoxDest.currentIndex())

    def ClearFromLocation(self):
        self.fromList.clear()
        self.comboBoxFrom.clear()

    def ClearDestLocation(self):
        self.destList.clear()
        self.comboBoxDest.clear()

    def Synchronize(self):
        if self.comboBoxFrom.currentText() == '':
            QMessageBox.information(self, 'Message', '원본의 위치가 올바르지 않습니다!')
            return
        elif self.comboBoxDest.currentText() == '':
            QMessageBox.information(self, 'Message', '목적지의 위치가 올바르지 않습니다!')
            return
        elif self.comboBoxFrom.currentText() == self.comboBoxDest.currentText():
            QMessageBox.information(self, 'Message', '원본과 목적지의 위치가 같습니다!')
            return
        try:
            self.pgb = _ProgressBar(self.comboBoxFrom.currentText(), self.comboBoxDest.currentText())
            self.syncWorker = FileSync(self.comboBoxFrom.currentText(), self.comboBoxDest.currentText())
            self.threadpool.start(self.pgb)
            self.threadpool.start(self.syncWorker)
            self.pushButtonSync.setDisabled(True)
            self.pushButtonAddFrom.setDisabled(True)
            self.pushButtonAddDest.setDisabled(True)
            self.pushButtonDeleteFrom.setDisabled(True)
            self.pushButtonDeleteDest.setDisabled(True)
            self.pushButtonClearFrom.setDisabled(True)
            self.pushButtonClearDest.setDisabled(True)
            self.comboBoxFrom.setDisabled(True)
            self.comboBoxDest.setDisabled(True)
            self.pgb.signal.progress.connect(self.progressBar.setValue)
            self.syncWorker.signal.finished.connect(self.SyncComplete)
        except FileNotFoundError:
            QMessageBox.information(self, 'Message', '파일 경로에 이상이 있습니다!')
            return

    def SyncComplete(self):
        QMessageBox.information(self, 'Message', '동기화 완료!')
        self.progressBar.setValue(100)
        self.pushButtonSync.setEnabled(True)
        self.pushButtonSync.setEnabled(True)
        self.pushButtonAddFrom.setEnabled(True)
        self.pushButtonAddDest.setEnabled(True)
        self.pushButtonDeleteFrom.setEnabled(True)
        self.pushButtonDeleteDest.setEnabled(True)
        self.pushButtonClearFrom.setEnabled(True)
        self.pushButtonClearDest.setEnabled(True)
        self.comboBoxFrom.setEnabled(True)
        self.comboBoxDest.setEnabled(True)


    def closeEvent(self, event):
        self.historyList['original'] = self.fromList
        self.historyList['destination'] = self.destList
        History.saveHistory(self.historyList)



