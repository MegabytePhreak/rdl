__author__ = 'megabytephreak'

from rdl_lexer import RdlLexer, RdlToken
from ply import yacc
from ply.lex import LexToken
import rdl_ast
from rdlcompiler.colorize import colorize, RED
from rdlcompiler.logger import logger


def make_list_prod(prod, tprod):

    def rule(self, p):
        if len(p) == 3:
            p[0] = p[1] + [p[2]]
        else:
            p[0] = []

    rule.__doc__ = "{0} : {0} {1} \n |".format(prod, tprod)
    return rule


def make_oneof_prod(prod, prods):

    def rule(self, p):
        p[0] = p[1]

    lines = ['%s : %s' % (prod, prods[0])]
    lines += prods[1:]
    rule.__doc__ = '\n| '.join(lines)
    return rule


class RdlParser(RdlLexer):

    start = 'root'

    p_root = make_list_prod('root', 'elem')

    p_elem = make_oneof_prod('elem', ['enum_def',   'comp_def',
                                      'anon_comp_inst', 'comp_inst',
                                      'default_prop_assign', 'prop_assign', 'dynamic_prop_assign'])

    def p_comp_def(self, p):
            """ comp_def : COMPTYPE id LBRACE comp_body RBRACE SEMI
            """
            p[0] = rdl_ast.CompDef(p[1].value, p[2].value, p[4])
            p[0].span = (p[1].location.index, p[6].location.index - p[1].location.index)


    def p_anon_comp_inst(self, p):
        """ anon_comp_inst : int_ext COMPTYPE LBRACE comp_body RBRACE comp_inst_elems SEMI
                           | COMPTYPE LBRACE comp_body RBRACE comp_inst_elems SEMI
        """
        if len(p) > 7:
            p[0] = rdl_ast.AnonCompInst(p[2].value, p[4], p[6], p[1])
        else:
            p[0] = rdl_ast.AnonCompInst(p[1].value, p[3], p[5], None)

    # def p_anon_comp_inst_error(self, p):
    #     """ anon_comp_inst : int_ext COMPTYPE LBRACE error RBRACE comp_inst_elems SEMI
    #                         | COMPTYPE LBRACE error RBRACE comp_inst_elems SEMI
    #     """
    #
    #     self.syntax_error("Syntax Error in component body, missing semicolon?", p[3])

    def p_comp_inst(self, p):
        """ comp_inst : int_ext id  comp_inst_elems SEMI
                      | ID  comp_inst_elems SEMI
        """
        intext = None
        if len(p) > 4:
            p[0] = rdl_ast.CompInst(p[2].value, p[3], p[1])
        else:
            p[0] = rdl_ast.CompInst(p[1].value, p[2])

    def p_comp_inst_error(self, p):
        """ comp_inst : int_ext error SEMI
                      | id error SEMI
        """
        self.syntax_error("Syntax Error in component instantiation", p[1])


    def p_int_ext(self, p):
        """ int_ext : INTEXT
        """
        p[0] = p[1].value

    p_comp_body = make_list_prod('comp_body', 'comp_elem')
    p_comp_elem = make_oneof_prod('comp_elem', ['enum_def',  'comp_def',
                                  'anon_comp_inst', 'comp_inst',
                                  'default_prop_assign', 'prop_assign', 'dynamic_prop_assign'])

    def p_comp_inst_elems(self, p):
        """ comp_inst_elems : comp_inst_elems COMMA comp_inst_elem
                            | comp_inst_elem
        """
        if len(p) > 2:
            p[0] = p[1] + [p[3]]
        else:
            p[0] = [p[1]]

    def p_comp_inst_elem(self, p):
        """ comp_inst_elem : id array_decl reset_value addr_alloc
        """
        p[0] = rdl_ast.InstParams(p[1].value, p[2], p[3], p[4])

    def p_array_decl(self, p):
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

    def p_reset_value(self, p):
        """ reset_value : EQ sized_numeric
                        |
        """
        if len(p) > 1:
            p[0] = p[2]
        else:
            p[0] = None


    def p_addr_alloc(self, p):
        """ addr_alloc : alloc_pos alloc_inc
        """
        p[0] = (p[1], p[2])

    def p_alloc_pos(self, p):
        """ alloc_pos : AT numeric
                      | MOD numeric
                      |
        """
        if len(p) > 1:
            p[0] = (p[1].value, p[2])
        else:
            p[0] = None

    def p_alloc_inc(self, p):
        """ alloc_inc : INC numeric
                      |
        """
        if len(p) > 1:
            p[0] = p[2]
        else:
            p[0] = None

    def p_propname(self, p):
        """ propname : PROPNAME
                     | PRECEDENCETYPE
        """
        p[0] = p[1].value


    def p_default_prop_assign(self, p):
        """ default_prop_assign : DEFAULT prop_assign
        """
        p[2].set_default = True
        p[0] = p[2]

    def p_prop_assign_0(self, p):
        """ prop_assign : propname maybe_value SEMI
        """
        p[0] = rdl_ast.PropAssign(p[1], p[2])
        p[0].span = (p.lexspan(1)[0], p[3].location.index - p.lexspan(1)[0])

    def p_prop_assign_1(self, p):
        """ prop_assign : NONSTICKY INTRMOD propname maybe_value SEMI
                        | INTRMOD propname maybe_value SEMI
                        | NONSTICKY propname maybe_value SEMI
        """
        if len(p) == 6:
            p[0] = rdl_ast.IntrPropAssign(p[3], p[4], (p[1].value, p[2].value))
        else:
            p[0] = rdl_ast.IntrPropAssign(p[2], p[3], (p[1].value,))

    def p_dynamic_prop_assign(self, p):
        """ dynamic_prop_assign :  instance_ref maybe_value SEMI
        """
        p[0] = rdl_ast.PropAssign(p[1], p[2])

    def p_maybe_value(self, p):
        """ maybe_value : EQ value
                       |
        """
        if len(p) == 1:
            p[0] = True
        else:
            p[0] = p[2]

    def p_enum_def(self, p):
        """ enum_def : ENUM ID LBRACE enum_body RBRACE SEMI
        """
        p[0] = rdl_ast.EnumDef(p[2].value, p[4])
        p[0].span = (p[1].location.index, p[6].location.index - p[1].location.index)

    p_enum_body = make_list_prod('enum_body', 'encoding')

    def p_encoding(self, p):
        """ encoding : ID EQ sized_numeric SEMI
                     | ID EQ sized_numeric LBRACE enum_props RBRACE SEMI
        """
        if len(p) == 5:
            p[0] = rdl_ast.EnumEncoding(p[1].value, p[3], [])
            p[0].span = (p[1].location.index, p[4].location.index - p[1].location.index)
        else:
            p[0] = rdl_ast.EnumEncoding(p[1].value, p[3], p[5])
            p[0].span = (p[1].location.index, p[7].location.index - p[1].location.index)

    p_enum_props = make_list_prod('enum_props', 'prop_assign')

    p_value = make_oneof_prod('value', ['instance_ref', 'literal'])

    def p_instance_ref(self, p):
        """ instance_ref : instance_ref_path
                         | instance_ref_path DEREF propname
        """
        p[0] = rdl_ast.InstanceRef(p[1])

        if len(p) > 2:
            p[0].set_prop(p[3])

    def p_instance_ref_path(self, p):
        """ instance_ref_path : instance_ref_elem
                              | instance_ref_path DOT instance_ref_elem
        """
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    def p_instance_ref_elem(self, p):
        """ instance_ref_elem : ID
                              | ID LSQ numeric RSQ
        """
        if len(p) == 2:
            p[0] = p[1].value
        else:
            p[0] = rdl_ast.Subscript(p[1].value, p[3])

    def p_literal_1(self, p):
        """ literal : STRING
        """
        p[0] = p[1].value

    def p_literal_2(self, p):
        """ literal : TF
        """
        if p[1].value == 'true':
            p[0] = True
        else:
            p[0] = False

    def p_literal_3(self, p):
        """ literal : ACCESSTYPE
        """
        p[0] = rdl_ast.AccessType(p[1].value)

    def p_literal_4(self, p):
        """ literal : ADDRESSTYPE
        """
        p[0] = rdl_ast.AddressingType(p[1].value)

    def p_literal_5(self, p):
        """ literal : PRECEDENCETYPE
        """
        p[0] = rdl_ast.PrecedenceType(p[1].value)

    def p_literal_6(self, p):
        """ literal : numeric
        """
        p[0] = p[1]

    def p_numeric_0(self, p):
        """ numeric : NUM
        """
        p[0] = p[1].value

    def p_numeric_1(self, p):
        """ numeric : VNUM"""
        p[0] = p[1].value

    def p_sized_numeric_1(self, p):
        """ sized_numeric : VNUM"""
        p[0] = p[1].value

    def p_sized_numeric_2(self, p):
        """ sized_numeric : NUM
        """
        if p[1].value != 0:
            self.syntax_error("Expected sized_numeric (Verilog-style numeric literal or 0)", p[1])

        p[0] = (-1, p[1].value)

    def p_id(self, p):
        """ id : ID
        """
        p[0] = p[1];

    def p_id_error(self, p):
        """ id : PROPNAME
               | INTRMOD
        """
        self.syntax_error(
            "Identifier '%s' is a keyword name. If you need to use this name, please use the escaped form '\\%s'."
            % (p[1].value, p[1].value), p[1])
        raise SyntaxError

    def p_error(self, t):
        if t:
            prev = self._parser.symstack[-1]
            if type(prev) == LexToken:
                msg = "Unexpected %s after %s." % (t.type, prev.type)
            else:
                print prev
                msg = "Unexpected %s." % t.type

            self.syntax_error(msg, t)

            while 1:
                tok = self.token()             # Get the next token
                if not tok or tok.type == 'SEMI': break
            self._parser.errok()

            return tok
        else:
            msg = "Unexpected end of file"
            self._parser.restart()
        self.syntax_error(msg, t)

    def syntax_error(self, message, token):
        if token is not None:
            if not isinstance(token, RdlToken):
                token = RdlToken(token)

            logger.log_line(self.format_line_message(token, colorize(RED, "Error: ") + message))
        else:
            logger.log_line(colorize(RED, "Error: ") + message)

        self.syntax_errors += 1

    def __init__(self, debug=False):
        RdlLexer.__init__(self)
        self.syntax_errors = 0
        self.debug = False

        self._parser = yacc.yacc(module=self,
                                 debug=debug,
                                 tabmodule=None,        # Don't try to precomputed parse table from a file
                                 write_tables=False,    # No point in saving the parse tables then either
                                 optimize=False,        # Yet another part of avoiding the parse table loading
                                )

    def parse(self, string):
        string = string.expandtabs(4)
        return self._parser.parse(string, lexer=self, debug=self.debug, tracking=True)
