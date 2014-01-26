__author__ = 'MegabytePhreak'

import ConfigParser
import sys
import os.path


class Config(ConfigParser.RawConfigParser, object):

    _cfg_defaults = {
        'rdlcompiler': {
            'outputs': 'verilog vhdl html c'
        },
        'preprocessor': {
            'perl': 'perl',
            'perlpp': '/home/megabytephreak/code/rdl/perlpp/rdlcompiler_perlpp.pl',
            'vppreproc': '/usr/bin/site_perl/vppreproc',
        }
    }

    _instance = None

    if sys.platform.startswith('win'):
        SYSTEM_CONFIG_PATH = os.path.expandvars(r'%PROGRAMDATA%\rdlcompiler\rdlcompiler.conf')
        USER_CONFIG_PATH = os.path.expandvars(r'%LOCALAPPDATA%\rdlcompiler\rdlcompiler.conf')
    else:
        SYSTEM_CONFIG_PATH = '/etc/rdlcompiler.conf'
        USER_CONFIG_PATH = os.path.expanduser('~/.rdlcompiler.conf')

    @classmethod
    def create(cls, *args, **kwargs):
        cls._instance = Config(*args, **kwargs)

    @classmethod
    def cfg(cls):
        return cls._instance

    def __init__(self, defaults=None, *args, **kwargs):
        super(Config, self).__init__(*args, **kwargs)

        if defaults is None:
            defaults = self._cfg_defaults

        for section, options in defaults.iteritems():
            self.add_section(section)
            for option, value in options.iteritems():
                self.set(section, option, value)


