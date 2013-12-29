__author__ = 'megabytephreak'

import openRDL.systemrdl.grammar as grammar
from codetalker import testing


parse_rule = testing.parse_rule(__name__,grammar.grammar)

parse_rule(grammar.enum_def, (
   "enum TEST_ENUM { test_entry = 0; };"
),(

))