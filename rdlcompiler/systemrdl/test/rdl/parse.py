__author__ = 'MegabytePhreak'

import rdlcompiler.systemrdl.parser as parser


def test_enum():
    p = parser.RdlParser()

    p.parse('enum myenum { True = 1\'b0; False = 1\'b1 { name="FALSE"; descn="The opposite of \nTRUE"; }; };')
