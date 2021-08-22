from os import path
from distutils.dir_util import copy_tree

from PyQt5.QtCore import QRunnable, QObject, pyqtSignal, pyqtSlot


class _Signal(QObject):
    finished = pyqtSignal()


class FileSync(QRunnable):
    def __init__(self, originLoc, destLoc):
        super().__init__()
        self.signal = _Signal()
        self.originLoc = originLoc
        self.destLoc = destLoc

    def doSync(self):
        if not path.isdir(self.originLoc) or not path.isdir(self.destLoc):
            raise FileNotFoundError('Wrong dir')
        else:
            copy_tree(self.originLoc, self.destLoc)

    @pyqtSlot()
    def run(self):
        self.doSync()
        self.signal.finished.emit()

