__author__ = 'MegabytePhreak'

from ply import lex
import re
from collections import OrderedDict

from properties import properties


def _make_lexer():
    WS = '[ \t]+'
    STRING = r'"([^"]|\\")*"'

    keywords = {
        'default':  'DEFAULT',

        'internal': 'INTEXT',
        'external': 'INTEXT',

        'rw':       'ACCESSTYPE',
        'wr':       'ACCESSTYPE',
        'r':        'ACCESSTYPE',
        'w':        'ACCESSTYPE',
        'na':       'ACCESSTYPE',

        'compact':  'ADDRESSTYPE',
        'regalign':  'ADDRESSTYPE',
        'fullalign': 'ADDRESSTYPE',

        'hw':       'PRECEDENCETYPE',
        'sw':       'PRECEDENCETYPE',

        'true':     'TF',
        'false':    'TF',

        'enum':     'ENUM',
        'alias':    'ALIAS',
        'property': 'PROPERTY',

        'bothedge':     'INTRMOD',
        'posedge':      'INTRMOD',
        'negedge':      'INTRMOD',
        'level':        'INTRMOD',
        'nonsticky':    'NONSTICKY',

        'addrmap':      'COMPTYPE',
        'regfile':      'COMPTYPE',
        'reg':          'COMPTYPE',
        'field':        'COMPTYPE',
        'signal':       'COMPTYPE',
    }

    # hw and sw are properties, but they are lexed as a precedence
    keywords.update({prop.name: 'PROPNAME' for prop in properties if prop.name not in keywords})

    tokens = ['VNUM', 'NUM', 'STRING', 'ID', 'DEREF', 'INC', 'MOD', 'LSQ', 'RSQ', 'RBRACE', 'LBRACE',
              'LPAREN', 'RPAREN', 'COLON', 'COMMA', 'DOT', 'OR', 'AT', 'SEMI', 'EQ']
    tokens += list(OrderedDict.fromkeys(keywords.values()))



    @lex.TOKEN(r'`line' + WS + r'\d+' + WS + STRING + WS + r'\d+[ \t]*\n')
    def t_line(t):
        (directive, lineno, path, level) = t.value.split()
        t.lexer.lineno = int(lineno)
        t.lexer.filename = path[1:-1]  # Remove quotes
        # Suppress the token, no return

    VNUM = '(\\d+)\'([bdh])([0-9a-fA-F]+)'
    VNUM_RE = re.compile(VNUM)

    @lex.TOKEN(VNUM)
    def t_VNUM(t):
        (width, radix, digits) = VNUM_RE.match(t.value).groups()
        width = int(width)

        try:
            value = int(digits, {'b': 2, 'd': 10, 'h': 16}[radix])

            t.value = (width, value)
            return t

        except ValueError:
            print("Error:%s: Illegal verilog-style literal '%s' has invalid digits for radix '%s'" %
                  (token_loc(t), t.value, radix))

    @lex.TOKEN(r'\d+|0x[0-9a-fA-F]+')
    def t_NUM(t):
        t.value = int(t.value)
        return t

    @lex.TOKEN(STRING)
    def t_STRING(t):
        # RDL string may contain embedded newlines, keep track of the line numbers
        t.lexer.lineno += t.value.count('\n')
        t.value = t.value[1:-1].decode('string-escape')
        return t

    @lex.TOKEN(r'\\?[a-zA-Z_][a-zA-Z_0-9]*')
    def t_ID(t):
        if t.value[0] == '\\':
            if t.value[1:] not in keywords:
                print("Warning:%s: Escaped identifer '%s' does not represent a SystemRDL keyword." %
                      (token_loc(t), t.value))
            t.value = t.value[1:]
            return t

        t.type = keywords.get(t.value, 'ID')    # Check for reserved words
        return t

    @lex.TOKEN(r'\s+')
    def t_ws(t):
        pass

    @lex.TOKEN(r'\n')
    def t_newline(t):
        t.lexer.lineno += 1

    @lex.TOKEN(r'/\*(.|\n)*?\*/')
    def t_mlcomment(t):
        t.lexer.lineno += t.value.count('\n')

    @lex.TOKEN('//[^\n]*\n')
    def t_slcomment(t):
        t.lexer.lineno += 1

    def t_error(t):
        print("Warning:%s: Illegal character '%s'." % (token_loc(t), t.value))
        t.lexer.skip(1)
        return t

    t_LBRACE = r'{'
    t_RBRACE = r'}'
    t_LSQ = r'\['
    t_RSQ = r'\]'

    t_LPAREN = r'\('
    t_RPAREN = r'\)'

    t_AT = r'@'
    t_OR = r'\|'
    t_SEMI = r';'
    t_COLON = r':'
    t_COMMA = r','
    t_DOT = r'\.'

    t_DEREF = r'->'

    t_EQ = r'='
    t_INC = r'\+='
    t_MOD = r'%='

    # Compute column.
    #     input is the input text string
    #     token is a token instance
    def _find_column(self, t):
        last_cr = t.lexer.lexdata.rfind('\n', 0, t.lexpos)
        if last_cr < 0:
            last_cr = 0
        column = (t.lexpos - last_cr) + 1
        return column

    def token_loc(t):
        return '%s:%d:%d' % (t.lexer.filename, t.lexer.lineno, _find_column(t))

    return tokens, lex.lex()


class RdlToken(object):
    def __init__(self, value, location):
        self.value = value
        self.location = location


class RdlLexer(object):

    def __init__(self):
        self.tokens,self._lexer = _make_lexer()


    def input(self, data, filename='<string>'):
        self._lexer.filename = filename
        self._lexer.lineno = 1
        return self._lexer.input(data)

    def token(self):
        tok = self._lexer.token()
        if tok is not None:
            tok.value = RdlToken(tok.value, (self._lexer.filename, tok.lineno, tok.lexpos))
        return tok

    def __iter__(self):
        return self

    def next(self):
        tok = self.token()
        if tok is None:
            raise StopIteration()
        return tok

if __name__ == "__main__":
    lex.runmain(RdlLexer())
