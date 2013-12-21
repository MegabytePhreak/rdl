from codetalker.pgm.tokens import *
import re


class VNUMBER(ReToken):
    rx = re.compile(r"\d+'[bBdDhH]\d+(_\d+)*")


class ACCESSTYPE(StringToken):
    strings = ['rw', 'wr', 'r', 'w', 'na']


class ADDRESSTYPE(StringToken):
    strings = ['compact', 'regalign', 'fullalign']


class PRECEDENCE(StringToken):
    strings = ['hw', 'sw']


class TF(StringToken):
    strings = ['true', 'false']


class SYMBOL(CharToken):
    chars = '{}[];=\''


class DEREF(StringToken):
    strings = ['->']


