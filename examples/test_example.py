from pytest_steps import step


@step(description='Increase value', log_output=False)
def increase(v):
    return v+1


@step(log_input=False)
def decrease(v):
    return v-1


class TestClass(object):
    def test_some_feature(self):
        result = self.do_some_calculation(2, second_param=3)
        self.verify_result(result)
        increase(result)
        decrease(result)

    @step(step_group=True)
    def do_some_calculation(self, first_param, second_param):
        first_param = increase(first_param)
        second_param = increase(second_param)
        return first_param + second_param

    @step(log_input=False)
    def verify_result(self, actual_data):
        assert actual_data == 7
