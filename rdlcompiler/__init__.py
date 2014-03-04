__author__ = 'MegabytePhreak'


import argparse
from .systemrdl.preprocessor import preprocess_mode, preprocess
from .systemrdl.parser import RdlParser
import re
from .config import Config


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

    conf = parser.add_argument_group('Configuration Options')
    conf.add_argument('--no-system-config', action='store_false', dest='load_system_config',
                        help="Don't load the system-level configuration file: '%s'" % Config.SYSTEM_CONFIG_PATH)
    conf.add_argument('--no-user-config', action='store_false', dest='load_user_config',
                       help="Don't load the user-level configuration file: '%s'" % Config.USER_CONFIG_PATH)
    conf.add_argument('-C', '--config', action='append', dest='config_files', type=argparse.FileType('rb'),
                        metavar='CONFIG_FILE', default=[],
                        help="Load extra configuration file")
    conf.add_argument('-O', '--override', action='append', dest='overrides', type=parse_override,
                        metavar='SECTION.OPTION=VALUE', default=[],
                        help="Override loaded configuration settings with specified value")

    return parser.parse_args()


def parse_override(arg):
    rx = r'([^.]+)\.([^.]+)=(.+)'
    res = re.match(rx, arg)
    if res is None:
        raise argparse.ArgumentTypeError('Expected configuration override')
    return res.groups()


def main():
    Config.create()
    args = parse_args()

    if args.load_system_config:
        Config.cfg().read(Config.SYSTEM_CONFIG_PATH)
    if args.load_user_config:
        Config.cfg().read(Config.USER_CONFIG_PATH)

    for f in args.config_files:
        Config.cfg().readfp(f, f.name)

    for override in args.overrides:
        Config.cfg().set(override[0], override[1], override[2])

    contents = preprocess(args.inputs, preprocessor_mode_map[args.preprocessor])

    if args.preprocess_only:
        if args.output is None:
            print contents
        else:
            open(args.output, 'wb').write(contents)
        exit(0)

    p = RdlParser()

    ast = p.parse(contents)

    for node in ast:
        print node

if __name__ == '__main__':
    main()