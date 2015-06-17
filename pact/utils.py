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
