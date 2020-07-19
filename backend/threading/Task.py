from datetime import datetime

from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal

class Task(QThread):
    # `object` data returned from processing, anything
    result = pyqtSignal(object)

    def __init__(self, fn, *args, **kwargs):
        super().__init__()

        self._fn = fn
        self._args = args
        self._kwargs = kwargs

    def run(self):
        res = self._fn(*self._args, **self._kwargs)
        self.result.emit(res)

    def callback(self, fn):
        self.result.connect(fn, Qt.QueuedConnection)

def onceTask(context, fn, *args, **kwargs):
    signature = str(datetime.now())
    task = Task(fn, *args, **kwargs)
    setattr(context, signature, task)
    task.callback(lambda : delattr(context, signature))
    return task

class Tasks(QObject):
    def __init__(self):
        self._tasks = {}
        self._id = 0

    def add(self, task):
        curr = self._id
        self._id += 1
        self._tasks[curr] = task
        task.result.connect(lambda : self._tasks.pop(curr))

    def create(self, fn, *args, **kwargs):
        task = Task(fn, *args, **kwargs)
        self.add(task)
        return task
