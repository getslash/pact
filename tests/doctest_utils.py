import itertools
import flux

_async_deletes = {}
_id = itertools.count()

def delete_async(path):
    returned = next(_id)
    timeout = 10 if 'huge' not in path else 30
    _async_deletes[returned] = flux.current_timeline.time() + timeout
    return returned

def is_async_delete_finished(operation_id):
    return flux.current_timeline.time() >= _async_deletes[operation_id]
