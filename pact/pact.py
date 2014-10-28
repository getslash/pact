from .utils import EdgeTriggered


class Pact(object):

    def __init__(self, msg):
        super(Pact, self).__init__()
        self.msg = msg
        self._until = []

    def until(self, callback, *args, **kwargs):
        """Adds a callback criterion for the completion of this pact
        """
        self._until.append(EdgeTriggered(callback, args, kwargs))

    def finished(self):
        """Returns whether or not this pact is finished
        """
        return all(u.satisfied() for u in self._until)

    def __repr__(self):
        return self.msg

