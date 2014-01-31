__author__ = 'MegabytePhreak'

from ply import yacc
import ast
import lexer


def _make_parser(tokens, *args, **kwargs):

    start = 'root'

    def make_list_prod(prod, tprod):

        def rule(p):
            if len(p) == 3:
                p[0] = p[1] + [p[2]]
            else:
                p[0] = [p[1]]

        rule.__doc__ = "{0} : {0} {1} \n | {1}".format(prod, tprod)
        print rule.__doc__
        return rule

    def make_oneof_prod(prod, prods):

        def rule(p):
            p[0] = p[1]

        lines = ['%s : %s' % (prod, prods[0])]
        lines += prods[1:]
        rule.__doc__ = '\n| '.join(lines)
        print rule.__doc__
        return rule

    def error(tok, text, *args):
            message = text % args
            print("Error:%s:%d: %s" %
                  (tok.location[0], tok.location[1], message))
            raise SyntaxError

    p_root = make_list_prod('root', 'elem')

    p_elem = make_oneof_prod('elem', ['enum_def',  # 'comp_def',
                                      #'anon_comp_inst', 'comp_inst',
                                      'default_prop_assign', 'prop_assign', 'dynamic_prop_assign'])

    def p_propname(p):
        """ propname : PROPNAME
                     | PRECEDENCETYPE
        """
        p[0] = p[1].value


    def p_default_prop_assign(p):
        """ default_prop_assign : DEFAULT prop_assign
        """
        p[2].set_default = True
        p[0] = p[1]

    def p_prop_assign_0(p):
        """ prop_assign : propname maybe_value SEMI
        """
        p[0] = ast.PropAssign(p[1], p[2])

    def p_pop_assign_1(p):
        """ prop_assign : NONSTICKY INTRMOD propname maybe_value SEMI
                        | INTRMOD propname maybe_value SEMI
                        | NONSTICKY propname maybe_value SEMI
        """
        if len(p) == 5:
            p[0] = ast.IntrPropAssign(p[3], p[4], (p[1], p[2]))
        else:
            p[0] = ast.IntrPropAssign(p[2], p[3], (p[1]))

    def p_dynamic_prop_assign(p):
        """ dynamic_prop_assign :  instance_ref maybe_value SEMI
        """
        p[0] = ast.PropAssign(p[1], p[2])

    def p_maybe_value(p):
        """ maybe_value : EQ value
                       |
        """
        if len(p) == 1:
            p[0] = True
        else:
            p[0] = p[2]

    def p_enum_def(p):
        """ enum_def : ENUM ID LBRACE enum_body RBRACE SEMI
        """
        p[0] = ast.EnumDef(p[2].value, p[4])

    p_enum_body = make_list_prod('enum_body', 'encoding')

    def p_encoding(p):
        """ encoding : ID EQ sized_numeric SEMI
                     | ID EQ sized_numeric LBRACE enum_props RBRACE SEMI
        """
        if len(p) == 5:
            p[0] = ast.EnumEncoding(p[1].value, p[3], [])
        else:
            p[0] = ast.EnumEncoding(p[1].value, p[3], p[5])

    p_enum_props = make_list_prod('enum_props', 'prop_assign')

    p_value = make_oneof_prod('value', ['instance_ref', 'literal'])

    def p_instance_ref(p):
        """ instance_ref : instance_ref_path
                         | instance_ref_path DEREF propname
        """
        p[0] = ast.InstanceRef([p[1].value])

        if len(p) > 2:
            p[0].set_deref(p[3])

    def p_instance_ref_path(p):
        """ instance_ref_path : instance_ref_elem
                              | instance_ref_path DOT instance_ref_elem
        """
        if len(p) == 2:
            p[0] = ast.InstanceRef([p[1].value])
        else:
            p[1].add_child_ref(p[3].value)
            p[0] = p[1]

    def p_instance_ref_elem(p):
        """ instance_ref_elem : ID
                              | ID LSQ numeric RSQ  DOT
        """
        if len(p) == 2:
            p[0] = p[1].value
        else:
            p[0] = ast.Subscript(p[1].value, p[2])

    def p_literal_1(p):
        """ literal : STRING
        """
        p[0] = p[1].value

    def p_literal_2(p):
        """ literal : TF
        """
        if p[1].value == 'true':
            p[0] = True
        else:
            p[0] = False

    def p_literal_3(p):
        """ literal : ACCESSTYPE
        """
        p[0] = ast.AccessType(p[1].value)

    def p_literal_4(p):
        """ literal : ADDRESSTYPE
        """
        p[0] = ast.AddressingType(p[1].value)

    def p_literal_5(p):
        """ literal : PRECEDENCETYPE
        """
        p[0] = ast.PrecedenceType(p[1].value)

    def p_literal_6(p):
        """ literal : numeric
        """
        p[0] = p[1]

    def p_numeric_0(p):
        """ numeric : NUM
        """
        p[0] = p[1].value

    def p_numeric_1(p):
        """ numeric : VNUM"""
        p[0] = p[1].value

    def p_sized_numeric_1(p):
        """ sized_numeric : VNUM"""
        p[0] = p[1].value

    def p_sized_numeric_2(p):
        """ sized_numeric : NUM
        """
        if p[1].value != 0:
            error(p[1], "Expected sized_numeric (Verilog-style numeric literal or 0)")

        p[0] = (-1, p[1].value)

    return yacc.yacc(*args, **kwargs)


class RdlParser(object):

    def __init__(self):
        self.lexer = lexer.RdlLexer()
        self.parser = _make_parser(self.lexer.tokens)

    def parse(self, string):

        return self.parser.parse(string, lexer=self.lexer)
