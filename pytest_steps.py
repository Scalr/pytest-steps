import os
import sys

import py
import pytest


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
        config.pluginmanager.register(StepsPlugin(config), 'stepsplugin')


class StepsPlugin(object):
    def __init__(self, config):
        self.config = config
        self.outdent = DEFAULT_OUTDENT
        self.stdout = os.fdopen(os.dup(sys.stdout.fileno()), 'w')
        self.tw = py._io.terminalwriter.TerminalWriter(self.stdout)

    def pytest_pycollect_makeitem(self, collector, name, obj):
        """Add config object for all marked functions"""
        if hasattr(obj, 'step'):
            obj.config = self.config

    def pytest_runtest_logreport(self, report):
        if report.when == 'setup':
            self.tw.line()
            self.tw.line('  {} -->'.format(report.location[2]))
        elif report.when == 'teardown':
            self.outdent = DEFAULT_OUTDENT
            self.tw.line()

    def pytest_steps_report_step(self, state, name, *args, **kwargs):
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

    def increase_outdent(self):
        self.outdent += 1

    def decrease_outdent(self):
        self.outdent -= 1


def step(step_group=False, description=''):
    def deco(func):
        def wrapper(*args, **kwargs):
            state = StepStates.PASSED
            if step_group:
                wrapper.config.hook.pytest_steps_report_step(
                    state=StepStates.STEPGROUP,
                    name=description or func.__name__
                )
                wrapper.config.pluginmanager.getplugin('stepsplugin').increase_outdent()
            try:
                result = func(*args, **kwargs)
            except:
                state = StepStates.ERROR
                raise
            finally:
                if step_group:
                    wrapper.config.pluginmanager.getplugin('stepsplugin').decrease_outdent()
                    wrapper.config.hook.pytest_steps_report_step(
                        state=state,
                        name=''
                    )
                else:
                    wrapper.config.hook.pytest_steps_report_step(
                        state=state,
                        name=description or func.__name__,
                        *args, **kwargs
                    )
            return result
        return pytest.mark.step(wrapper)
    return deco