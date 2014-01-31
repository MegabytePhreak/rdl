__author__ = 'MegabytePhreak'

from rdlcompiler.systemrdl import lexer
import os


def readall(path):
    path = os.path.join(os.path.dirname(__file__), path)
    with open(path, 'rb') as f:
        return f.read()


def lexer_test(data):
    l = lexer.RdlLexer()
    l.input(data)
    l.filename = ''

    for tok in l:
        assert tok.type != 'error'


#def test_sata_example():
#    lexer_test(readall('rdl/sata_ahci_example.rdl.ppp.rdl'))

enum_tests = (
    'enum TEST_ENUM {^};',
    'enum TEST_ENUM { test_entry = 0; };',
    'enum TEST_ENUM { test_entry = 1\'b0 { desc="Some Description"; }; };',
    'enum a_123 { test_entry = 1\'b0 { desc="Some Description"; }; '
)

for i, test in enumerate(enum_tests):
    def enum_test():
        lexer_test(test)

    globals()['test_enum_%d'%i] = enum_test
