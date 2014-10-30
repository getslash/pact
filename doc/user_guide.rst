.. _user_guide:

User's Guide
============

Creating Pacts
--------------

A *pact* is a form of a promise. It's similar to concepts like A+/promises that you may be familiar with already. It is intended for scenarios where you want to return 'handles' to asynchronous events, and be able to elegantly control what happens with those events.

Suppose we have an API that copies a large directory structure in the background, ``delete_async(path)``, returning some identifier for the ongoing task, and a complementary API, ``is_async_delete_finished(id)`` asking if it completed.

A *pact* wraps this api nicely:

.. code-block:: python

		>>> from pact import Pact

		>>> def pact_delete_async(path):
		...     returned = Pact('Deleting {0}'.format(path))
		...     operation_id = delete_async(path)
		...     returned.until(is_async_delete_finished, operation_id)
		...     return returned
		

Note the example uses :func:`pact.Pact.until` to denote when the pact can be considered 'finished'.

Checking Pact Status
--------------------

Our code can now interact with the returned *pact* object:

.. code-block:: python

		>>> p = pact_delete_async('/path')
		>>> p.finished()
		False
		>>> sleep(10)
		>>> p.finished()
		True

Waiting on Pacts
----------------

A very common scenario is to wait until a pact is finished. This is what the :func:`pact.Pact.wait` method is for:

.. code-block:: python

		>>> from pact import TimeoutExpired
		>>> p = pact_delete_async('/path')
		>>> p.wait()
		>>> p.finished()
		True

You can also specify a timeout in seconds. Expiration of the timeout will result in an exception:

.. code-block:: python

		>>> p = pact_delete_async('/path')
		>>> try:
		...     p.wait(timeout_seconds=1.5)
		... except TimeoutExpired as e:
		...     print('Got exception:', e)
		Got exception: Timeout of 1.5 seconds expired waiting for [Deleting /path]

Grouping Pacts
--------------

Pacts support joining multiple instances together to form a group:

.. code-block:: python

		>>> from pact import PactGroup
		>>> p1 = pact_delete_async('/path1')
		>>> p2 = pact_delete_async('/path2')
		>>> group = PactGroup([p1, p2])

There is a shorter syntax as well, using the ``+`` operator:

.. code-block:: python

		>>> group = p1 + p2

The most immediate thing you can do on a pact group is wait for it to end altogether:

.. code-block:: python

		>>> group.wait()

And of course it will be more descriptive when only one pact was not satisfied:

.. code-block:: python

		>>> group =(pact_delete_async('/path1') + pact_delete_async('/huge_directory'))
		>>> try:
		...     group.wait(timeout_seconds=10)
		... except TimeoutExpired as e:
		...     print('Got exception:', e)
		Got exception: Timeout of 10 seconds expired waiting for [Deleting /huge_directory]


Triggering Actions
------------------

You can easily attach callbacks to occur when a pact finishes:

.. code-block:: python
       
       >>> pact_delete_async('/path1').then(print, 'finished').wait()
       finished

This can be chained multiple times

.. code-block:: python
       
       >>> pact_delete_async('/path1').\
       ...    then(print, 'message1').\
       ...    then(print, 'message2').\
       ...    wait()
       message1
       message2

Also for groups:

.. code-block:: python
       
       >>> start_time = time()
       >>> group = pact_delete_async('/path1').\
       ...     then(lambda: print('path1 finished after', time() - start_time, 'seconds')) \
       ...   + pact_delete_async('/huge_dir').\
       ...     then(lambda: print('huge_dir finished after', time() - start_time, 'seconds'))
       >>> group.wait()
       path1 finished after 10.0 seconds
       huge_dir finished after 30.0 seconds
