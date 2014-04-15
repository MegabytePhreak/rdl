__author__ = 'megabytephreak'


import sys


class Logger:
    def __init__(self, out=sys.stderr):
        self._out = out

    def log(self, message):
        self._out.write(message)

    def log_line(self, message):
        self._out.write(message)
        self._out.write('\n')

    def get_dest(self):
        return self._out


logger = Logger()