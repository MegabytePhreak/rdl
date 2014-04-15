__author__ = 'megabytephreak'

import os
import tempfile
import re
from rdlcompiler.config import Config
import subprocess
from enum import Enum

class preprocess_mode(Enum):
    AUTO = -1
    NONE = 0
    VERILOG_ONLY = 1
    PERL_ONLY = 2
    BOTH = 3


def perl_available():
    try:
        with open(os.devnull) as fnull:
            subprocess.check_call([Config.cfg().get('preprocessor', 'perl'), '--version'],
                                  stdout=fnull, stderr=fnull)
        return True
    except OSError:
        return False


def required_preprocessors(filenames):
    ret = preprocess_mode.NONE
    perl_rx = re.compile(r'<%')
    verilog_rx = re.compile(r'`')
    for fname in filenames:
        with open(fname, 'rb') as f:
            content = f.read()
            if perl_rx.search(content) is not None:
                return preprocess_mode.BOTH
            if verilog_rx.search(content) is not None:
                ret = preprocess_mode.VERILOG_ONLY
    return ret


def perl_preprocess(filenames, output_path):
    try:
        subprocess.call([Config.cfg().get('preprocessor', 'perl'), Config.cfg().get('preprocessor', 'perlpp')]
                        + filenames + ['--output', output_path])
        return output_path
    except (OSError, subprocess.CalledProcessError) as ex:
        raise Exception('Unable to launch perl preprocessor: %s' % ex)


def verilog_preprocess(filenames):
    try:
        return subprocess.check_output([Config.cfg().get('preprocessor', 'perl'), Config.cfg().get('preprocessor', 'vppreproc'), '--mlstring'] +
                                       filenames)
    except (OSError, subprocess.CalledProcessError) as ex:
        raise Exception('Unable to launch verilog preprocessor: %s' % ex)


def concatenate_files(filenames):
    """ Concatenate the specified files, adding `line directives so the lexer can track source locations.
    """
    contents = []
    for filename in filenames:
        contents.append('`line 1 "%s" 1' % filename)
        with open(filename, 'rb') as f:
            contents.append(f.read())

    return '\n'.join(contents)


def preprocess(filenames, mode=preprocess_mode.AUTO):
    if mode == preprocess_mode.AUTO:
        mode = required_preprocessors(filenames)

    if mode != preprocess_mode.NONE and not perl_available():
        raise Exception("A perl installation is required in order to perform preprocessing, "
                        "but the configured perl executable '%s' was not found" %
                        Config.cfg().get('preprocessor', 'perl'))
    try:
        tempname = None
        if mode == preprocess_mode.PERL_ONLY or mode == preprocess_mode.BOTH:
            tempfd, tempname = tempfile.mkstemp('.'+os.path.basename(filenames[-1])+'.ppp')
            os.close(tempfd)
            filenames = [perl_preprocess(filenames, tempname)]
            if mode == preprocess_mode.PERL_ONLY:
                return open(filenames[0], 'rb').read()

        if mode == preprocess_mode.VERILOG_ONLY or mode == preprocess_mode.BOTH:
            return verilog_preprocess(filenames)
    finally:
        if tempname is not None:
           pass # os.remove(tempname)

    return concatenate_files(filenames)