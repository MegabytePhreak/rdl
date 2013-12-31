__author__ = 'megabytephreak'

import openRDL.systemrdl.grammar as grammar
from codetalker import testing
import os


def readall(path):
    path = os.path.join(os.path.dirname(__file__), path)
    with open(path, 'rb') as f:
        return f.read()


parse_rule = testing.parse_rule(__name__,grammar.grammar)

parse_rule(grammar.enum_def, (
    'enum TEST_ENUM {};',
    'enum TEST_ENUM { test_entry = 0; };',
    'enum TEST_ENUM { test_entry = 1\'b0 { desc="Some Description"; }; };',
    'enum a_123 { '
    'test_entry = 1\'b0 { desc="Some Description"; }; '
    'another_entry =  1\'b2; '
    '};',
), (
    'enum TEST_ENUM { test_entry = 1\'b0 { desc="Some Description" }; };',
))

parse_rule(grammar.value, (
    '0',
    '1234',
    '10\'b1',
    '11\'d10',
    '12\'hab',
    '"Hello, String!"',
    'some.item',
    '16\'h12_ab_34_cd',
    'true',
    'false',
), (
    '\'b0',
))

parse_rule(grammar.root, (
    'reg { foo->bar = "baz"; } blah;',
    'reg foo { };',
    'foo bar[10];',
    """
     default hw=na;                                                    // All the fields in the this register have the same properties
   default sw=r;                                                     // So define them global for this register

   field {
       desc = "Number of Ports (NP): 0's based value indicating the maximum number of ports
               supported by the HBA silicon. A maximum of 32 ports can be supported. A value of
               '0h', indicating one port, is the minimum requirement. Note that the number of ports
               indicated in this field may be more than the number of ports indicated in the GHC.PI
               register.";
   } NP[5] = 5'b0_00_01;
    """,
    readall('rdl/sata_ahci_example.rdl.ppp.rdl'),
), () )