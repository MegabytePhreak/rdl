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
    rule.add_option(VNUMBER)
    rule.pass_single = True


def value(rule):
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
    rule.add_option((_or('name', 'desc'), '=', STRING, ';'))
    rule.astAttrs = {'name': ID, 'value': STRING}


def enum_item(rule):
    rule.add_option((ID, '=', sized_numeric, ['{', star(enum_prop), '}'], ';'))
    rule.astAttrs = {'name': ID, 'value': sized_numeric, 'properties': [enum_prop]}


def enum_def(rule):
    rule.add_option(("enum", ID, '{', star(enum_item), '}', ';'))
    rule.astAttrs = {'name': ID, 'items': [enum_item]}


def prop_assign(rule):
    rule.add_option((ID, ['=', value], ';'))
    rule.astAttrs = {'name': ID, 'value': [value]}


def default_prop_assign(rule):
    rule.add_option(('default', prop_assign))
    rule.astAttrs = {'assign': prop_assign}


def dynamic_prop_assign(rule):
    rule.add_option((instance_ref, '->', prop_assign))
    rule.astAttrs = {'instance': instance_ref, 'assign': prop_assign}


def field_body(rule):
    rule.add_option(('{', star(_or(prop_assign,  default_prop_assign, dynamic_prop_assign, enum_def)), '}'))
    rule.astAttrs = {'contents': [prop_assign, default_prop_assign, dynamic_prop_assign, enum_def]}


def field_def(rule):
    rule.add_option(("field", ID, field_body, ['=', sized_numeric], ';'))
    rule.astAttrs = {'name': ID, 'body': field_body}


def anonymous_field_inst(rule):
    rule.add_option(('field', field_body, ID, [_or(array, array_range)], ['=', sized_numeric], ';'))
    rule.astAttrs = {'body': field_body, 'name': ID, 'array': [array, array_range], 'reset': sized_numeric}


def component_inst(rule):
    rule.add_option(([_or('internal', 'external')], ['alias', ID], ID, ID, [_or(array, array_range)], ';'))
    rule.astAttrs = {'type': {'type': ID, 'single': True}, 'name': {'type': ID, 'single': True}}


def component_body(rule):
    rule.add_option(('{', star(_or(prop_assign, default_prop_assign, dynamic_prop_assign, enum_def,
                                  field_def, component_inst, anonymous_field_inst, component_def)), '}'))


def component_def(rule):
    rule.add_option((ID, ID, component_body, ';'))


def anonymous_component_inst(rule):
    rule.add_option(([_or('internal', 'external')], ID, component_body, ID, [_or(array, array_range)], ';'))


def root(rule):
    rule.add_option((star(_or(enum_def, component_inst, anonymous_component_inst, component_def,
                              default_prop_assign, prop_assign, dynamic_prop_assign)),))

grammar = Grammar(start=root, tokens=all_tokens, ignore=[WHITE, NEWLINE], ast_tokens=[VNUMBER, NUMBER])