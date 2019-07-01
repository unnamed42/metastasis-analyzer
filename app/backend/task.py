from PyQt5.QtCore import QObject, QRunnable, QThreadPool, pyqtSlot, pyqtSignal

from sys import exc_info
from traceback import print_exc, format_exc

class _Signals(QObject):
    """
    Defines the signals available from a running worker thread.

    Supported signals are:

    done
        No data

    error
        `tuple` (exctype, value, traceback.format_exc() )

    result
        `object` data returned from processing, anything

    progress
        `int` indicating % progress
    """

    done = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)

class Task(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super().__init__()

        self._fn = fn
        self._args = args
        self._kwargs = kwargs
        self.signals = _Signals()

    @pyqtSlot()
    def run(self):
        try:
            result = self._fn(*self._args, **self._kwargs)
        except:
            print_exc()
            e, value = exc_info()[:2]
            self.signals.error.emit((e, value, format_exc()))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.done.emit()

    def start(self, pool=None):
        pool = pool or QThreadPool.globalInstance()
        pool.start(self)
