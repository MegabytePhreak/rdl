__author__ = 'megabytephreak'

import openRDL.systemrdl.grammar as grammar
from codetalker import testing


parse_rule = testing.parse_rule(__name__,grammar.grammar)

parse_rule(grammar.enum_def, (
    'enum TEST_ENUM {};',
    'enum TEST_ENUM { test_entry = 0; };',
    'enum TEST_ENUM { test_entry = 1\'b0 { desc="Some Description"; }; };',
    'enum a_123 { '
        'test_entry = 1\'b0 { desc="Some Description"; }; '
        ' another_entry =  1\'b2; '
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
), (
    '\'b0',
))

parse_rule(grammar.field_def, (
    'field global_reset { hw=na; sw=woclr; hwset; } = 0;',
), (

))

parse_rule(grammar.root, (
    'reg { } blah;',
    'reg foo { };',
    'foo bar[10];',
), () )