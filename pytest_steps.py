import os
import sys
import inspect
import traceback

import py
import pytest
from _pytest.terminal import TerminalReporter

DEFAULT_OUTDENT = 2


class StepStates:
    PASSED = 'PASSED'
    ERROR = 'ERROR'
    STEPGROUP = 'Step group'

    @staticmethod
    def get_state_color(state):
        colors = {
            StepStates.PASSED: 'green',
            StepStates.ERROR: 'red',
            StepStates.STEPGROUP: 'light'
        }
        return colors[state]


def pytest_addhooks(pluginmanager):
    """Register plugin hooks."""
    import hooks
    pluginmanager.addhooks(hooks)


def pytest_addoption(parser):
    group = parser.getgroup("test suite steps", "steps", after="general")
    group._addoption(
        '--nosteps', action="store_false", dest="steps", default=True,
        help=(
            "disable pytest-steps"
        )
    )


@pytest.mark.trylast
def pytest_configure(config):
    if config.option.steps:
        standard_reporter = config.pluginmanager.getplugin('terminalreporter')
        config.pluginmanager.unregister(standard_reporter)
        config.pluginmanager.register(StepsPlugin(standard_reporter), 'terminalreporter')


class StepsPlugin(TerminalReporter):
    def __init__(self, reporter):
        TerminalReporter.__init__(self, reporter.config)
        self.config = reporter.config
        self.outdent = DEFAULT_OUTDENT
        self.stdout = os.fdopen(os.dup(sys.stdout.fileno()), 'w')
        self.tw = py._io.terminalwriter.TerminalWriter(self.stdout)

    def pytest_pycollect_makeitem(self, collector, name, obj):
        """Add config object for all marked functions"""
        if hasattr(obj, 'step'):
            obj.config = self.config

    def pytest_runtest_logreport(self, report):
        rep = report
        res = self.config.hook.pytest_report_teststatus(report=rep)
        cat, letter, word = res
        self.stats.setdefault(cat, []).append(rep)
        if rep.when == 'setup':
            self.tw.line()
            self.tw.line('  {} -->'.format(rep.location[2]))
        elif rep.when == 'teardown':
            self.outdent = DEFAULT_OUTDENT

    def pytest_steps_report_step(self, state, name):
        markup = {
            'text': state,
            StepStates.get_state_color(state): True
        }
        additional = ''

        if state == StepStates.STEPGROUP:
            additional = ':'

        self.tw.line('{}{} {}{}'.format(
            '  ' * self.outdent,
            self.tw.markup(**markup),
            name,
            additional)
        )

    def pytest_steps_report_traceback(self, traceback):
        for line in traceback.splitlines():
            self.tw.line('{}{}'.format('  ' * self.outdent, line))

    def increase_outdent(self):
        self.outdent += 1

    def decrease_outdent(self):
        self.outdent -= 1


class StepInfo(object):
    def __init__(self, step_group=False, description=None, log_input=True, log_output=True):
        self.step_group = step_group
        self.description = description
        self.function = None
        self.args = None
        self.kwargs = None
        self.config = None
        self.result = None
        self.traceback = None
        self.log_input = log_input
        self.log_output = log_output

    def initialize(self):
        if self.description is None:
            doc = inspect.getdoc(self.function)
            if doc is not None:
                self.description = doc.splitlines()[0]
            else:
                self.description = self.function.__name__
        self.stepper = self.config.pluginmanager.getplugin('terminalreporter')

    def run(self):
        self.initialize()
        self._before_run()
        try:
            self._execute()
        except:
            self.traceback = traceback.format_exc()
            raise
        finally:
            self._after_run()
        return self.result

    @property
    def name(self):
        format_args = ', '.join(map(lambda x: str(x), self._get_clean_args())) if self.args else ''
        format_kwargs = ', '.join(map(lambda x: '%s=%s' % (str(x[0]), str(x[1])), self.kwargs.items())) if self.kwargs else ''
        fmt = self.description
        if (format_args or format_kwargs) and self.log_input:
            fmt += '('
            if format_args:
                fmt += format_args
            if format_kwargs:
                if format_args:
                    fmt += '; '
                fmt += format_kwargs
            fmt += ')'
        if self.result and self.log_output:
            fmt += ' -> %s' % str(self.result)
        return fmt

    def _get_clean_args(self):
        args = self.args
        if args:
            args_def = inspect.getargspec(self.function)[0]
            if args_def and args_def[0] == u'self':
                args = args[1:]
        return args

    def report(self, state, show_name=True, show_result=False):
        name = self.name if show_name else ''
        if show_result and self.result and self.log_output:
            name += ' -> %s' % str(self.result)
        self.config.hook.pytest_steps_report_step(
            state=state,
            name=name
        )

    def report_exception(self):
        self.config.hook.pytest_steps_report_traceback(traceback=self.traceback)

    def _before_run(self):
        if self.step_group:
            self.report(StepStates.STEPGROUP)
            self.stepper.increase_outdent()

    def _after_run(self):
        state = StepStates.ERROR if self.traceback else StepStates.PASSED
        if self.step_group:
            self.stepper.decrease_outdent()
            self.report(state, show_name=False, show_result=True)
        else:
            self.report(state)
        if self.traceback:
            self.report_exception()

    def _execute(self):
        self.result = self.function(*self.args, **self.kwargs)


def step(func=None, step_group=False, description=None, log_input=True, log_output=True):
    step_info = StepInfo(step_group, description, log_input, log_output)

    def wrapper(*args, **kwargs):
        step_info.config = wrapper.config
        step_info.args = args
        step_info.kwargs = kwargs
        return step_info.run()

    def param_wrapper(func):
        step_info.function = func
        return pytest.mark.step(wrapper)
    if func is None:
        return param_wrapper
    else:
        step_info.function = func
    return pytest.mark.step(wrapper)


def group(func=None, description=None, log_input=True, log_output=True):
    return step(func, step_group=True, description=description, log_input=log_input, log_output=log_output)