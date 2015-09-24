from pytest_steps import step


@step()
def foo():
    pass


@step()
def some_func():
    raise AssertionError('error')


class Test(object):
    def test_smth(self, request):
        self.bar()
        foo()

    @step(step_group=True, description='Bar function')
    def bar(self):
        foo()
        self.third_step()

    @step(step_group=True, description='Second step group')
    def third_step(self):
        foo()

    def test_smth2(self):
        self.bar()
        self.third_step()
        self.third_step()
        some_func()
