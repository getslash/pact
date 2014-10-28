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

Our code can now interact with the returned *pact* object:

.. code-block:: python

		>>> p = pact_delete_async('/path')
		>>> p.finished()
		False
		>>> sleep(10)
		>>> p.finished()
		True




		


