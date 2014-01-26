__author__ = 'MegabytePhreak'


def cfg():
    global _config
    return _config

import ConfigParser
import argparse
import os
from systemrdl.preprocessor import preprocess_mode, preprocess
import re
import sys

if sys.platform.startswith('win'):
    SYSTEM_CONFIG_PATH = os.path.expandvars(r'%PROGRAMDATA%\rdlcompiler\rdlcompiler.conf')
    USER_CONFIG_PATH = os.path.expandvars(r'%LOCALAPPDATA%\rdlcompiler\rdlcompiler.conf')
else:
    SYSTEM_CONFIG_PATH = '/etc/rdlcompiler.conf'
    USER_CONFIG_PATH = os.path.expanduser('~/.rdlcompiler.conf')


_config = None


def init_config():
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

    global _config
    _config = ConfigParser.RawConfigParser()
    for section, options in _cfg_defaults.iteritems():
        cfg().add_section(section)
        for option, value in options.iteritems():
            cfg().set(section, option, value)


def parse_override(arg):
    rx = r'([^.]+)\.([^.]+)=(.+)'
    res = re.match(rx, arg)
    if res is None:
        raise argparse.ArgumentTypeError('Expected configuration override')
    return res.groups()


preprocessor_mode_map = {
    'auto': preprocess_mode.AUTO,
    'none': preprocess_mode.NONE,
    'perlpp': preprocess_mode.PERL_ONLY,
    'verilog': preprocess_mode.VERILOG_ONLY,
    'full': preprocess_mode.BOTH
}


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('inputs', nargs='+', action='store',
                        help=
                        """Files to process. The contents of the files will be concatenated before any
                         preprocessing.""")

    compile_opts = parser.add_argument_group('Compiler Options')
    compile_opts.add_argument('-E', '--preprocess-only', action='store_true', dest='preprocess_only',
                              help="Only preprocess the input files, do not compile them and produce outputs")
    compile_opts.add_argument('-o', '--output', action='store', dest='output',
                              help="Output filename or prefix")
    compile_opts.add_argument('-p', '--preprocessor', choices=preprocessor_mode_map, action='store', default='auto',
                              help="Type of preprocessing to perform, default='auto'")

    config = parser.add_argument_group('Configuration Options')
    config.add_argument('--no-system-config', action='store_false', dest='load_system_config',
                        help="Don't load the system-level configuration file: '%s'" % SYSTEM_CONFIG_PATH)
    config.add_argument('--no-user-config', action='store_false', dest='load_user_config',
                        help="Don't load the user-level configuration file: '%s'" % USER_CONFIG_PATH)
    config.add_argument('-C', '--config', action='append', dest='config_files', type=argparse.FileType('rb'),
                        metavar='CONFIG_FILE', default=[],
                        help="Load extra configuration file")
    config.add_argument('-O', '--override', action='append', dest='overrides', type=parse_override,
                        metavar='SECTION.OPTION=VALUE', default=[],
                        help="Override loaded configuration settings with specified value")

    return parser.parse_args()


def main():
    init_config()
    args = parse_args()

    if args.load_system_config:
        cfg().read(SYSTEM_CONFIG_PATH)
    if args.load_user_config:
        cfg().read(USER_CONFIG_PATH)

    for f in args.config_files:
        cfg().readfp(f, f.name)

    for override in args.overrides:
        cfg().set(override[0], override[1], override[2])

    print args

    print cfg()._sections

    contents = preprocess(args.inputs, preprocessor_mode_map[args.preprocessor])

    if args.preprocess_only:
        if args.output is None:
            print contents
        else:
            open(args.output, 'wb').write(contents)
        exit(0)

if __name__ == '__main__':
    main()