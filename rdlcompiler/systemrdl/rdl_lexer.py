

from ply import lex
import re
from collections import OrderedDict, namedtuple


from properties import properties
from rdlcompiler.colorize import colorize, RED, BOLD
from rdlcompiler.logger import logger

Location = namedtuple('Location', ['filename', 'lineno', 'index'])


class RdlToken(object):
    def __init__(self, tok):
        self.value = tok.value
        self.location = Location(tok.lexer.filename, tok.lineno, tok.lexpos)

    def __str__(self):
        return "RdlToken('%s')" % str(self.value)


class RdlLexer(object):

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
   #     'alias':    'ALIAS',
    #    'property': 'PROPERTY',

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

    @lex.TOKEN(r'`line' + WS + r'\d+' + WS + STRING + WS + r'\d+[ \t]*\n')
    def t_line_directive(self, t):
        (directive, lineno, path, level) = t.value.split()
        t.lexer.lineno = int(lineno)
        t.lexer.filename = path[1:-1]  # Remove quotes
        # Suppress the token, no return

    VNUM = '(\\d+)\'([bdh])([0-9a-fA-F_]+)'
    VNUM_RE = re.compile(VNUM)

    @lex.TOKEN(VNUM)
    def t_VNUM(self, t):
        (width, radix, digits) = self.VNUM_RE.match(t.value).groups()
        width = int(width)

        try:
            value = int(digits.replace('_', ''), {'b': 2, 'd': 10, 'h': 16}[radix])

            t.value = (width, value)
            return t

        except ValueError:
            print self.lex_error(
                t, "Illegal Verilog-style literal '%s' has invalid digits for radix '%s'" % (t.value, radix))

    @lex.TOKEN(r'0x[0-9a-fA-F]+|\d+')
    def t_NUM(self, t):
        t.value = int(t.value, base=0)
        return t

    @lex.TOKEN(STRING)
    def t_STRING(self,t):
        # RDL string may contain embedded newlines, keep track of the line numbers
        t.lexer.lineno += t.value.count('\n')
        t.value = t.value[1:-1].decode('string-escape')
        return t

    @lex.TOKEN(r'\\?[a-zA-Z_][a-zA-Z_0-9]*')
    def t_ID(self, t):
        if t.value[0] == '\\':
            if t.value[1:] not in self.keywords:
                self.lex_error(t, "Escaped identifier '%s' does not represent a SystemRDL keyword" % t.value)

            t.value = t.value[1:]
            return t

        t.type = self.keywords.get(t.value, 'ID')    # Check for reserved words
        return t

    @lex.TOKEN(r'/\*(.|\n)*?\*/')
    def t_mlcomment(self, t):
        t.lexer.lineno += t.value.count('\n')

    @lex.TOKEN(r'//[^\n]*\n')
    def t_slcomment(self, t):
        t.lexer.lineno += 1

    @lex.TOKEN(r'\n')
    def t_newline(self, t):
        t.lexer.lineno += 1

    @lex.TOKEN(r'[ \t]+')
    def t_ws(self, t):
        pass

    def t_error(self, t):
        self.lex_error(t, "Unrecognized input")
        t.lexer.skip(1)

    t_LBRACE = r'{'
    t_RBRACE = r'}'
    t_LSQ = r'\['
    t_RSQ = r'\]'

    t_AT = r'@'
   # t_OR = r'\|'
    t_SEMI = r';'
    t_COLON = r':'
    t_COMMA = r','
    t_DOT = r'\.'

    t_DEREF = r'->'

    t_EQ = r'='
    t_INC = r'\+='
    t_MOD = r'%='

    def prefix_message(self, message, filename=None, lineno=None, token=None ):
        if token is not None:
            lineno = token.location.lineno
            filename = token.location.filename

        if filename is None:
            filename = '<string>'

        return colorize(BOLD, "%s:%d: " % (filename, lineno)) + message

    def format_line(self, index=None, token=None):
        if token is not None:
            column = self.token_to_column(token)
            line = self.token_to_line(token)
        else:
            column = self.index_to_column(index)
            line = self.index_to_line(index)

        if column is not None:
            caret = colorize(RED, "^".rjust(column))
            return "%s\n%s" % (line, caret)

        return line

    def lex_error(self, token, message):
        if token is not RdlToken:
            token = RdlToken(token)

        logger.log_line(self.format_line_message(token, colorize(RED, "Error: ") + message))

        self.lex_errors += 1

    def format_line_message(self, token, message):
        return '\n'.join((
            self.prefix_message(message, token=token),
            self.format_line(token=token)
        ))

    def token_to_column(self, token):
        return self.index_to_column(token.location.index)

    def index_to_column(self, index):
        last_newline = self.data.rfind('\n', 0, index)

        column = (index - last_newline)

        return column

    def token_to_line(self, token):
        return self.index_to_line(token.location.index)

    def index_to_line(self, index):
        line_start = self.data.rfind('\n', 0, index) + 1
        if line_start == -1:
            line_start = 0
        line_end = self.data.find('\n', line_start+1)
        if line_end == -1:
            line_end = len(self.data)

        return self.data[line_start:line_end]

    def input(self, data, filename='<string>'):
        self._lexer.filename = filename
        self._lexer.lineno = 1
        self.data = data

        return self._lexer.input(data)

    def token(self):
        tok = self._lexer.token()
        if tok is not None:
            # Tokens without a processing function don't set this themselves
            tok.lexer = self._lexer
            # Wrap the token up to present useful data when in the parsing stage
            tok.value = RdlToken(tok)
        return tok


    def __init__(self):
        # hw and sw are properties, but they are lexed as a precedence
        self.keywords.update({prop.name: 'PROPNAME' for prop in properties if prop.name not in self.keywords})

        self.tokens = ['VNUM', 'NUM', 'STRING', 'ID', 'DEREF', 'INC', 'MOD', 'LSQ', 'RSQ', 'RBRACE', 'LBRACE',
                       'COLON', 'COMMA', 'DOT',
                       #'OR',
                       'AT', 'SEMI', 'EQ']
        self.tokens += list(OrderedDict.fromkeys(self.keywords.values()))

        self._lexer = lex.lex(object=self)
        self.lex_errors = 0
        self.data = None

if __name__ == "__main__":
    lex.runmain(RdlLexer())
