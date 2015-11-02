pytest-steps is a py.test plugin which let to adding some steps to your tests.
A prototype for pytest-steps is a project pytest-grail from Wargaming.

Example of usage:

.. code:: python
  from pytest_steps import step

  @step
  def first_step():
      pass

  def test_my():
      first_step()
      first_step()


In output You will see:

.. code:: python

  SUCCESS first_step()
  SUCCESS first_step()