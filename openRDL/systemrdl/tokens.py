from codetalker.pgm.tokens import *
import re

class KEYWORD(IdToken):
    strings = ['default']

class VNUMBER(ReToken):
    rx = re.compile(r"\d+'[bBdDhH][0-9a-fA-F]+(_[0-9a-fA-F]+)*")


class ACCESSTYPE(IdToken):
    strings = ['rw', 'wr', 'r', 'w', 'na']


class ADDRESSTYPE(IdToken):
    strings = ['compact', 'regalign', 'fullalign']



class PRECEDENCE(IdToken):
    strings = ['hw', 'sw']


class TF(IdToken):
    strings = ['true', 'false']


class SYMBOL(CharToken):
    chars = '{}[];=\'.'


class DEREF(StringToken):
    strings = ['->']


all_tokens = [ KEYWORD, SYMBOL, ACCESSTYPE, ADDRESSTYPE, PRECEDENCE, TF, ID, VNUMBER, NUMBER, DEREF ]