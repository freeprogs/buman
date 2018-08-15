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
import time
import os
import re


class ConfigFileNotFound(Exception):
    pass


class ConfigFileEmpty(Exception):
    pass


class ConfigFileSyntax(Exception):
    pass


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
        consolemessages = ConsoleMessages()
        self.console.print_message(consolemessages.get_progname())

    def get_configuration(self):
        """."""
        consolemessages = ConsoleMessages()
        configchecker = ConfigFileChecker()
        filename = self.args.get_argument('config')
        logfile = self.args.get_argument('logfile')
        self.console.print_message(
            consolemessages.get_logfile(logfile))
        self.console.print_message(
            consolemessages.get_configuration(filename))
        if not configchecker.exists(filename):
            self.console.print_message(
                consolemessages.get_config_nofile())
            raise ConfigFileNotFound
        if configchecker.is_empty(filename):
            self.console.print_message(
                consolemessages.get_config_empty())
            raise ConfigFileEmpty
        if not configchecker.is_correct(filename):
            self.console.print_message(
                consolemessages.get_config_syntax())
            raise ConfigFileSyntax
        self.config.load_from_file(filename)

    def make_tasks(self):
        """."""
        converter = RecordConverter()
        for record in self.config.get_records():
            for task in converter.record_to_tasks(record):
                self.tasks_queue.add_task(task)

    def process_tasks(self):
        """."""
        logconfigurator = LogConfigurator()
        sysoperations = SystemOperations()
        consolemessages = ConsoleMessages()
        repconverter = ReportConverter()
        logconf_default = LogConfig(
            self.args.get_argument('logfile'), Logger.LEVEL_ERROR)
        taskn_total = self.tasks_queue.length()
        taskn_success = taskn_skipped = taskn_failed = 0
        taskn_cur = 0

        self.console.print_message(
            consolemessages.get_header(
                self.args.get_argument('config'),
                self.args.get_argument('logfile')))
        for task in self.tasks_queue.iterate():
            taskn_cur += 1
            self.logger.set_config(
                logconfigurator.get_config_from_task(task, logconf_default))
            self.console.print_message(
                consolemessages.get_task_left(
                    task.name, taskn_cur, taskn_total),
                with_newline=False)
            status, report = sysoperations.execute_task(task)
            self.console.print_message(consolemessages.get_task_right(status))
            if status == SystemOperations.STATUS_OK:
                taskn_success += 1
                self.logger.log_message(
                    repconverter.to_log_message(report), Logger.LEVEL_INFO)
            elif status == SystemOperations.STATUS_SKIPPED:
                taskn_skipped += 1
            elif status == SystemOperations.STATUS_FAILED:
                taskn_failed += 1
                self.logger.log_message(
                    repconverter.to_log_message(report), Logger.LEVEL_ERROR)
            elif status == SystemOperations.STATUS_CTRLC:
                raise KeyboardInterrupt
            self.console.print_message(repconverter.to_console_message(report))
        self.console.print_message(
            consolemessages.get_footer(
                taskn_total, taskn_success, taskn_skipped, taskn_failed))

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


class ConfigFileChecker:
    """."""

    def exists(self, filename):
        """."""
        out = os.path.exists(filename)
        return out

    def is_empty(self, filename):
        """."""
        with open(filename, encoding='utf-8') as fin:
            result = fin.read().strip()
        return result == ''

    def is_correct(self, filename):
        """."""
        with open(filename, encoding='utf-8') as fin:
            text = fin.read()
        cleared = text.strip()
        out = re.search(r'^\{.*\}$', cleared) is not None
        return out


class ConfigCheckTokenizer:
    """."""

    def tokenize(self, text):
        """."""


class ConfigCheckToken:
    """."""

    def __init__(self):
        self.type = None
        self.value = None


class ConfigFile:
    """."""

    def __init__(self, filename, reader, parser):
        self.filename = filename
        self.reader = reader
        self.parser = parser

    def load_records(self):
        """."""
        out = []
        with open(self.filename, encoding='utf-8') as fin:
            while True:
                block = self.reader.read_block(fin)
                if not block:
                    break
                record = self.parser.from_string(block)
                out.append(record)
        return out


class FileReader:
    """."""

    def read_block(self, ifp):
        """."""
        if hasattr(self, 'x'):
            return ''
        else:
            self.x = 1
            return '{x}'


class RecordParser:
    """."""

    def from_string(self, s):
        """."""
        record = Record()
        tokenizer = ConfigParseTokenizer()
        blocks = tokenizer.text_to_blocks(s)
        tokens = tokenizer.blocks_to_tokens(blocks)
        for token in tokens:
            if token.type == ConfigParseToken.NAME:
                record.name = token.value
            elif token.type == ConfigParseToken.SRC:
                record.sources.append(token.value)
            elif token.type == ConfigParseToken.DST:
                record.destinations.append(token.value)
            elif token.type == ConfigParseToken.OPT:
                option = RecordOption()
                option.name = token.value[0]
                option.params = token.value[1]
                record.options.append(option)
        return record


class ConfigParseTokenizer:
    """."""

    def text_to_blocks(self, text):
        """."""

    def blocks_to_tokens(self, blocks):
        """."""


class ConfigParseToken:
    """."""

    NAME = 1
    SRC = 2
    DST = 3
    OPT = 4

    def __init__(self):
        self.type = None
        self.value = None


class RecordConverter:
    """."""

    def record_to_tasks(self, record):
        """."""
        out = []
        for src in record.sources:
            for dst in record.destinations:
                task = Task()
                task.name = record.name
                task.source = src
                task.destination = dst
                for opt in record.options:
                    option = TaskOption()
                    option.name = opt.name
                    option.params = opt.params
                    task.options.append(option)
                out.append(task)
        return out


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
        self.tasks.append(task)

    def iterate(self):
        """."""
        return iter(self.tasks)

    def length(self):
        """."""
        return len(self.tasks)


class LogConfigurator:
    """."""

    def __init__(self):
        pass

    def get_config_from_task(self, task, default):
        logopt = [i for i in task.options if i.name == 'log']
        if logopt:
            opt = logopt[0]
            filename = opt.params.get('filename', default.filename)
            level = opt.params.get('level', default.level)
            return LogConfig(filename, level)
        else:
            return default


class LogConfig:
    """."""

    def __init__(self, filename, level):
        self.filename = filename
        self.level = level


class Logger:
    """."""

    LEVEL_INFO = 1
    LEVEL_WARNING = 2
    LEVEL_ERROR = 3

    def __init__(self):
        self.config = None

    def set_config(self, config):
        """."""
        self.config = config

    def log_message(self, message, level):
        """."""
        if level >= self.config.level:
            logfilename = self.config.filename
            logfile = LogFile()
            if not os.path.exists(logfilename):
                datetime = time.strftime(
                    '%Y-%m-%d %H:%M:%S', time.localtime())
                logfile.open(logfilename)
                logfile.write(LogMessages().get_file_header(datetime))
            else:
                logfile.open(logfilename)
            logfile.write(message)
            logfile.close()


class LogMessages:
    """."""

    def get_file_header(self, datetime):
        """."""
        out = ('# Log of __PROGRAM_NAME__ __PROGRAM_VERSION__\n'
               '# Created ' + datetime + '\n')
        return out


class LogFile:
    """."""

    def __init__(self):
        self.ofp = None

    def open(self, filename):
        """."""
        self.ofp = open(filename, 'a')

    def write(self, text):
        """."""
        print(text, file=self.ofp)

    def close(self):
        """."""
        self.ofp.close()


class ConsoleMessages:
    """."""

    def get_progname(self):
        """."""
        out = '__PROGRAM_NAME__ __PROGRAM_VERSION__'
        return out

    def get_configuration(self, filename):
        """."""
        fmt = 'Loading configuration from {}'
        out = fmt.format(filename)
        return out

    def get_logfile(self, filename):
        """."""
        fmt = 'Set default logging to {}'
        out = fmt.format(filename)
        return out

    def get_config_nofile(self):
        """."""
        out = 'no config file found'
        return out

    def get_config_empty(self):
        """."""
        out = 'config file is empty'
        return out

    def get_config_syntax(self):
        """."""
        out = 'config file has incorrect syntax'
        return out

    def get_header(self, configfile, logfile):
        """."""
        datetime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        fmt = 'Started processing at {}\n'
        out = fmt.format(datetime)
        return out

    def get_task_left(self, name, number, total):
        """."""
        timehms = time.strftime('%H:%M:%S', time.localtime())
        fmt = '{}/{} started at {} {} ... '
        out = fmt.format(number, total, timehms, name)
        return out

    def get_task_right(self, status):
        """."""
        out = ('OK', 'SKIPPED', 'FAILED', 'INTERRUPT')[status]
        return out

    def get_footer(self, total, success, skipped, failed):
        """."""
        datetime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        fmt = ('\n'
               'Completed processing at {}\n'
               'Success: {}, Failed: {}, Skipped: {}, Total: {}')
        out = fmt.format(datetime, success, failed, skipped, total)
        return out


class SystemOperations:
    """."""

    STATUS_OK = 0
    STATUS_SKIPPED = 1
    STATUS_FAILED = 2
    STATUS_CTRLC = 3

    def execute_task(self, task):
        """."""
        converter = TaskConverter()
        task.begin = time.time()
        try:
            for i in 1, 2, 3:
                print('cmd', i, end=' ', flush=True)
                time.sleep(1)
            task.status = (0, 'Success')
            #task.status = (1, 'File is not found')
            task.end = time.time()
            report = converter.task_to_report(task)
            if task.status[0] == 0:
                out = (self.STATUS_OK, report)
            else:
                out = (self.STATUS_FAILED, report)
        except KeyboardInterrupt:
            out = (self.STATUS_CTRLC, None)
        return out


class TaskConverter:
    """."""

    def task_to_report(self, task):
        """."""
        report = Report()
        report.name = task.name
        report.status = task.status
        report.begin = task.begin
        report.end = task.end
        report.source = task.source
        report.destination = task.destination
        report.options = ', '.join(
            '{}=({})'.format(
                i.name, ','.join(
                    '{}:{}'.format(k, v) for k, v in i.params.items()))
            for i in task.options)
        return report


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
        out = '{} {} {} {} {} {} ret={} {}'.format(
            report.name,
            time.strftime('%H:%M:%S', time.localtime(report.begin)),
            time.strftime('%H:%M:%S', time.localtime(report.end)),
            report.source,
            report.destination,
            report.options,
            report.status[0],
            report.status[1])
        return out

    def to_log_message(self, report):
        """."""
        out = '{} {} {} {} {} {} {}'.format(
            time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(report.end)),
            report.name,
            report.source,
            report.destination,
            report.options,
            report.status[0],
            report.status[1])
        return out


class Console:
    """."""

    def __init__(self):
        self.ofp = sys.stdout

    def print_message(self, message, with_newline=True):
        """."""
        if with_newline:
            print(message, file=self.ofp)
        else:
            print(message, file=self.ofp, flush=True, end='')


def main():
    """."""
    app = Application()
    try:
        app.run()
    except (ConfigFileNotFound,
            ConfigFileEmpty,
            ConfigFileSyntax):
        return 1
    except KeyboardInterrupt:
        print('Bye')
    return 0

if __name__ == '__main__':
    sys.exit(main())
