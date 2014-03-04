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
                p[0] = []

        rule.__doc__ = "{0} : {0} {1} \n |".format(prod, tprod)
        return rule

    def make_oneof_prod(prod, prods):

        def rule(p):
            p[0] = p[1]

        lines = ['%s : %s' % (prod, prods[0])]
        lines += prods[1:]
        rule.__doc__ = '\n| '.join(lines)
        return rule

    def error(tok, text, *args):
            message = text % args
            print("Error:%s:%d: %s" %
                  (tok.location[0], tok.location[1], message))
            raise SyntaxError

    p_root = make_list_prod('root', 'elem')

    p_elem = make_oneof_prod('elem', ['enum_def',   'comp_def',
                                      'anon_comp_inst', 'comp_inst',
                                      'default_prop_assign', 'prop_assign', 'dynamic_prop_assign'])

    def p_comp_def(p):
        """ comp_def : COMPTYPE ID LBRACE comp_body RBRACE SEMI
        """
        p[0] = ast.CompDef(p[1].value, p[2].value, p[4])

    def p_anon_comp_inst(p):
        """ anon_comp_inst : int_ext COMPTYPE LBRACE comp_body RBRACE comp_inst_elems SEMI
                           | COMPTYPE LBRACE comp_body RBRACE comp_inst_elems SEMI
        """
        if len(p) > 7:
            p[0] = ast.AnonCompInst(p[2].value, p[4], p[6], p[1])
        else:
            p[0] = ast.AnonCompInst(p[1].value, p[3], p[5], None)

    def p_comp_inst(p):
        """ comp_inst : int_ext ID  comp_inst_elems SEMI
                      | ID  comp_inst_elems SEMI
        """
        intext = None
        if len(p) > 4:
            p[0] = ast.CompInst(p[2].value, p[3], p[1])
        else:
            p[0] = ast.CompInst(p[1].value, p[2])


    def p_int_ext(p):
        """ int_ext : INTEXT
        """
        p[0] = p[1].value

    p_comp_body = make_list_prod('comp_body', 'comp_elem')
    p_comp_elem = make_oneof_prod('comp_elem', ['enum_def',  'comp_def',
                                  'anon_comp_inst', 'comp_inst',
                                  'default_prop_assign', 'prop_assign', 'dynamic_prop_assign'])

    def p_comp_inst_elems(p):
        """ comp_inst_elems : comp_inst_elems COMMA comp_inst_elem
                            | comp_inst_elem
        """
        if len(p) > 2:
            p[0] = p[1] + [p[3]]
        else:
            p[0] = [p[1]]

    def p_comp_inst_elem(p):
        """ comp_inst_elem : ID array_decl reset_value addr_alloc
        """
        p[0] = ast.InstParams(p[1].value, p[2], p[3], p[4])

    def p_array_decl(p):
        """ array_decl : LSQ numeric RSQ
                       | LSQ numeric COLON numeric RSQ
                       |
        """
        if len(p) == 4:
            p[0] = p[2]
        elif len(p) == 6:
            p[0] = (p[2], p[4])
        else:
            p[0] = None

    def p_reset_value(p):
        """ reset_value : EQ sized_numeric
                        |
        """
        if len(p) > 1:
            p[0] = p[2]
        else:
            p[0] = None


    def p_addr_alloc(p):
        """ addr_alloc : alloc_pos alloc_inc
        """
        p[0] = (p[1], p[2])

    def p_alloc_pos(p):
        """ alloc_pos : AT numeric
                      | MOD numeric
                      |
        """
        if len(p) > 1:
            p[0] = (p[1].value, p[2])
        else:
            p[0] = None

    def p_alloc_inc(p):
        """ alloc_inc : INC numeric
                      |
        """
        if len(p) > 1:
            p[0] = p[2]
        else:
            p[0] = None

    def p_propname(p):
        """ propname : PROPNAME
                     | PRECEDENCETYPE
        """
        p[0] = p[1].value


    def p_default_prop_assign(p):
        """ default_prop_assign : DEFAULT prop_assign
        """
        p[2].set_default = True
        p[0] = p[2]

    def p_prop_assign_0(p):
        """ prop_assign : propname maybe_value SEMI
        """
        p[0] = ast.PropAssign(p[1], p[2])

    def p_pop_assign_1(p):
        """ prop_assign : NONSTICKY INTRMOD propname maybe_value SEMI
                        | INTRMOD propname maybe_value SEMI
                        | NONSTICKY propname maybe_value SEMI
        """
        if len(p) == 6:
            p[0] = ast.IntrPropAssign(p[3], p[4], (p[1].value, p[2].value))
        else:
            p[0] = ast.IntrPropAssign(p[2], p[3], (p[1].value,))

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
        p[0] = ast.InstanceRef(p[1])

        if len(p) > 2:
            p[0].set_prop(p[3])

    def p_instance_ref_path(p):
        """ instance_ref_path : instance_ref_elem
                              | instance_ref_path DOT instance_ref_elem
        """
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    def p_instance_ref_elem(p):
        """ instance_ref_elem : ID
                              | ID LSQ numeric RSQ
        """
        if len(p) == 2:
            p[0] = p[1].value
        else:
            p[0] = ast.Subscript(p[1].value, p[3])

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
