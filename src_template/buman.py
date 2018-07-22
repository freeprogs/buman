#!/usr/bin/env python3

# __PROGRAM_NAME__ __PROGRAM_VERSION__
#
# __PROGRAM_COPYRIGHT__ __PROGRAM_AUTHOR__ __PROGRAM_AUTHOR_EMAIL__
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Backup manager for backup files and directories with given options.

"""

__version__ = '__PROGRAM_VERSION_NO_V__'
__date__ = '__PROGRAM_DATE__'
__author__ = '__PROGRAM_AUTHOR__ __PROGRAM_AUTHOR_EMAIL__'
__license__ = 'GNU GPLv3'


import sys
import argparse


class Application:
    """."""

    def run(self):
        """."""
        controller = Controller()
        controller.get_arguments()
        controller.get_configuration()
        controller.make_tasks()
        controller.process_tasks()
        controller.finalize()


class Controller:
    """."""

    def __init__(self):
        self.args = Arguments()
        self.config = Configuration()
        self.tasks_queue = TasksQueue()
        self.console = Console()
        self.logger = Logger()

    def get_arguments(self):
        """."""
        self.args.load_from_cmdline()

    def get_configuration(self):
        """."""
        filename = self.args.get_argument('config')
        self.config.load_from_file(filename)

    def make_tasks(self):
        """."""

    def process_tasks(self):
        """."""

    def finalize(self):
        """."""


class Arguments:
    """."""

    def __init__(self):
        self.args = None

    def load_from_cmdline(self):
        """."""
        self.args = CommandLineArguments().parse_arguments()

    def get_argument(self, argname):
        """."""
        return getattr(self.args, argname)


class CommandLineArguments:
    """."""

    def __init__(self):
        self.default_config = '__PROGRAM_NAME__.conf'
        self.default_logfile = '__PROGRAM_NAME__.log'

    def parse_arguments(self):
        """."""
        desc = """
        Backup manager for backup files and directories with given options.
        """
        parser = argparse.ArgumentParser(description=desc)
        parser.add_argument('--config',
                            default=self.default_config,
                            help='configuration file (default: %(default)s)')
        parser.add_argument('--logfile',
                            default=self.default_logfile,
                            help='file for logging (default: %(default)s)')
        parser.add_argument('--version', '-V',
                            action='version',
                            version='%(prog)s ' + 'v' + __version__)
        parser.add_argument('--license',
                            action='version',
                            version='License: ' + __license__ +
                            ', see more details in file LICENSE'
                            ' or at <http://www.gnu.org/licenses/>.',
                            help='show program\'s license and exit')
        args = parser.parse_args()
        return args


class Configuration:
    """."""

    def __init__(self):
        self.records = None

    def load_from_file(self, filename):
        """."""
        config_file = ConfigFile(filename, FileReader(), RecordParser())
        self.records = config_file.load_records()

    def get_records(self):
        """."""
        return self.records


class ConfigFile:
    """."""

    def __init__(self, filename, reader, parser):
        self.filename = filename
        self.reader = reader
        self.parser = parser

    def load_records(self):
        """."""
        return []


class FileReader:
    """."""

    def read_block(self):
        """."""
        return ''


class RecordParser:
    """."""

    def from_string(self, s):
        """."""
        return Record()


class RecordConverter:
    """."""

    def record_to_tasks(self, record):
        """."""
        return []


class RecordOptionConverter:
    """."""

    def record_to_task(self, option):
        """."""
        return TaskOption()


class Record:
    """."""

    def __init__(self):
        self.name = None
        self.sources = []
        self.destinations = []
        self.options = []


class RecordOption:
    """."""

    def __init__(self):
        self.name = None
        self.params = {}


class Task:
    """."""

    def __init__(self):
        self.name = None
        self.source = None
        self.destination = None
        self.options = []


class TaskOption:
    """."""

    def __init__(self):
        self.name = None
        self.params = {}


class TasksQueue:
    """."""

    def __init__(self):
        self.tasks = []

    def add_task(self, task):
        """."""

    def iterate(self):
        """."""
        return iter(self.tasks)


class LogConfigurator:
    """."""

    def __init__(self):
        pass

    def get_config_from_task(self, task, default):
        return LogConifg()


class LogConfig:
    """."""

    def __init__(self, filename):
        self.filename = filename
        self.ofp = None

    def open(self):
        """."""

    def close(self):
        """."""


class Logger:
    """."""

    def __init__(self):
        self.config = None

    def set_config(self, config):
        """."""

    def log_message(self, message):
        """."""


class SystemOperations:
    """."""

    def execute_task(self, task):
        """."""
        return Report()


class TaskConverter:
    """."""

    def task_to_report(self, task):
        """."""
        return Report()


class Report:
    """."""

    def __init__(self):
        self.name = None
        self.status = ()
        self.begin = None
        self.end = None
        self.source = None
        self.destination = None
        self.options = None


class ReportConverter:
    """."""

    def to_console_message(self, report):
        """."""
        return ''

    def to_log_message(self, report):
        """."""
        return ''


class Console:
    """."""

    def __init__(self):
        self.ofp = sys.stdout

    def print_message(self, message):
        """."""


def main():
    """."""
    app = Application()
    app.run()
    return 0

if __name__ == '__main__':
    sys.exit(main())
