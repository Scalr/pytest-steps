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


Decorator test can take several parameters:

1. step_group (bool) - Set this function is a step group
2. description (str) - A human-like name for this function
3. log_input (bool) - Show input parameters in log or not
4. log_output (bool) - Show output from this function


In output You will see:

.. code:: python

  SUCCESS first_step()
  SUCCESS first_step()