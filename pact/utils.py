# -*- coding: utf-8 -*-

class EdgeTriggered(object):

    def __init__(self, callback, args, kwargs):
        super(EdgeTriggered, self).__init__()
        self._callback = callback
        self._args = args
        self._kwargs = kwargs
        self._satisfied = False

    def satisfied(self):
        if not self._satisfied:
            self._satisfied = self._callback(*self._args, **self._kwargs)
        return self._satisfied

    def __repr__(self):
        qual_name = getattr(self._callback, '__qualname__', None) or \
            getattr(self._callback, '__name__', str(self._callback))
        module_name = getattr(self._callback, '__module__', '???')
        func_desc = "{}.{}".format(module_name, qual_name)
        extra = " ✔" if self._satisfied else ""
        return '<{0.__class__.__name__}: {func_desc} ({0._args}, {0._kwargs}){extra}>'.format(
            self, func_desc=func_desc, extra=extra)
