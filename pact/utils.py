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


class GroupWaitPredicate(object):

    def __init__(self, pacts):
        super(GroupWaitPredicate, self).__init__()
        self._remaining = list(reversed(pacts))

    def __call__(self):
        for index in range(len(self._remaining), 0, -1):
            index -= 1
            if self._remaining[index].finished():
                self._remaining.pop(index)
        return not self._remaining

    def __repr__(self):
        return repr(self._remaining)
