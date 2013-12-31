from codetalker.pgm.tokens import *
import re


class KEYWORD(IdToken):
    strings = ['default'] # 'enum', 'field', 'reg', 'regfile', 'addrmap']


class INTEXT(IdToken):
    strings = ['internal', 'external']


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


class DEREF(StringToken):
    strings = ['->']


class ALLOC(StringToken):
    strings = ['+=', '@']


class SYMBOL(CharToken):
    chars = '{}[];=\'.:'


class MLSTRING(Token):

    _type = ReToken._type

    @classmethod
    def check(cls, text):
        length = 1
        escape = False

        if text[0] != '"':
            return 0

        for char in text[1:]:
            length += 1

            if escape:
                escape = False
            elif char == '\\':
                escape = True
            elif char == '"':
                break

        return length


all_tokens = [ KEYWORD, SYMBOL, ALLOC, ACCESSTYPE, ADDRESSTYPE, PRECEDENCE, TF, ID, STRING, HEX, VNUMBER, NUMBER,
               DEREF, CCOMMENT, CMCOMMENT, INTEXT, MLSTRING]