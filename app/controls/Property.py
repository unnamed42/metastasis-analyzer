from PyQt5.QtCore import QObject, pyqtProperty, pyqtSignal

class Property(pyqtProperty):
    # name and notify should not be set in constructor
    def __init__(self, type_, name="", notify=None):
        # delay the constructor until in PropertyMeta
        if name and notify:
            # getter and setter see below
            super().__init__(type_, self.getter, self.setter, notify=notify)
        self._type = type_
        self._name = "__" + name
        self._signame = "{}Changed".format(name)

    # the first argument is not the property name,
    # is the callee object instead
    def getter(self, inst):
        return getattr(inst, self._name)

    def setter(self, inst, value):
        oldval = getattr(inst, self._name, None)
        # test only for object identity
        if not (value is oldval):
            setattr(inst, self._name, value)
            getattr(inst, self._signame).emit(value)

##
#  Usage of a Property:
#  class Model(QObject, metaclass=PropertyMeta):
#      foo = Property("Hello, world!")
#
#      def __init__(self, parent):
#          super().__init__(parent)
#
#      @pyqtSlot()
#      def debug(self):
#          self.foo = "I modified foo!"
##

class PropertyMeta(type(QObject)):
    def __new__(meta, name, bases, attrs):
        for key in list(attrs.keys()):
            attr = attrs[key]
            if not isinstance(attr, Property):
                continue
            type_ = attr._type
            notify = pyqtSignal(type_)
            attrs[key] = Property(type_, key, notify=notify)
            attrs["{}Changed".format(key)] = notify
        return super().__new__(meta, name, bases, attrs)
