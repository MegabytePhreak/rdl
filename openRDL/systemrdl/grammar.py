__author__ = 'MegabytePhreak'

from tokens import *
from codetalker.pgm import Grammar
from codetalker.pgm.special import star, plus, _or, commas


def instance_ref(rule):
    rule.add_option((ID, star('.', ID)))
    rule.astAttrs = {'path': [ID]}


def unsized_numeric(rule):
    rule.add_option(NUMBER)
    rule.add_option(HEX)
    rule.pass_single = True


def sized_numeric(rule):
    rule.add_option(('0',))
    rule.add_option(('0x0',))
    rule.add_option(VNUMBER)
    rule.pass_single = True


def value(rule):
    rule.add_option(MLSTRING)
    rule.add_option(STRING)
    rule.add_option(TF)
    rule.add_option(sized_numeric)
    rule.add_option(unsized_numeric)
    rule.add_option(ACCESSTYPE)
    rule.add_option(ADDRESSTYPE)
    rule.add_option(PRECEDENCE)
    rule.add_option(instance_ref)
    rule.pass_single = True


def array(rule):
    rule.add_option(('[', unsized_numeric, ']'))
    rule.astAttrs = {'size': unsized_numeric}


def array_range(rule):
    rule.add_option(('[', unsized_numeric, ':', unsized_numeric, ']'))
    rule.astAttrs = {'range': unsized_numeric}


def enum_prop(rule):
    rule.add_option((_or('name', 'desc'), '=', _or(STRING, MLSTRING), ';'))
    rule.astAttrs = {'name': ID, 'value': [STRING, MLSTRING]}


def enum_item(rule):
    rule.add_option((ID, '=', sized_numeric, ['{', star(enum_prop), '}'], ';'))
    rule.astAttrs = {'name': ID, 'value': sized_numeric, 'properties': [enum_prop]}


def enum_def(rule):
    rule.add_option(("enum", ID, '{', star(enum_item), '}', ';'))
    rule.astAttrs = {'name': ID, 'items': [enum_item]}


def prop_assign(rule):
    rule.add_option((_or(PRECEDENCE,ID), ['=', value], ';'))
    rule.astAttrs = {'name': [PRECEDENCE,ID], 'value': [value]}


def default_prop_assign(rule):
    rule.add_option(('default', prop_assign))
    rule.astAttrs = {'assign': prop_assign}


def dynamic_prop_assign(rule):
    rule.add_option((instance_ref, '->', prop_assign))
    rule.astAttrs = {'instance': instance_ref, 'assign': prop_assign}


def inst_mod(rule):
    rule.add_option(([_or(array, array_range)],star(_or(('=', sized_numeric), (ALLOC, unsized_numeric)))))
    rule.astAttrs = {'array': [array, array_range], 'reset': [sized_numeric],
                     'alloc_mode': [ALLOC], 'alloc': [unsized_numeric]}


def component_body(rule):
    rule.add_option(('{', star(_or(prop_assign, default_prop_assign, dynamic_prop_assign, enum_def,
                                   anonymous_component_inst, component_inst, component_def)), '}'))


def component_def(rule):
    rule.add_option((ID, ID, component_body, ';'))


def anonymous_component_inst(rule):
    rule.add_option(([INTEXT], ID, component_body, ID, inst_mod, ';'))


def component_inst(rule):
    rule.add_option(([INTEXT], ['alias', ID], ID, ID, inst_mod, ';'))
    rule.astAttrs = {'type': {'type': ID, 'single': True}, 'name': {'type': ID, 'single': True}}


def root(rule):
    rule.add_option((star(_or(enum_def, component_inst, anonymous_component_inst, component_def,
                              default_prop_assign, prop_assign, dynamic_prop_assign)),))

grammar = Grammar(start=root, tokens=all_tokens, ignore=[WHITE, NEWLINE, CCOMMENT, CMCOMMENT],
                  ast_tokens=[VNUMBER, NUMBER, MLSTRING, HEX, INTEXT, ALLOC])
