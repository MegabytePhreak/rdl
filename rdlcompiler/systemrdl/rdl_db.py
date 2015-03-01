__author__ = 'megabytephreak'

import copy
from rdl_lexer import RdlToken
from rdl_parser import RdlParser
from rdlcompiler.db.scope import *
import rdlcompiler.db as db
from rdl_ast import *
from properties import properties, RdlComponent, RdlType
from rdlcompiler.colorize import colorize, RED
from rdlcompiler.logger import logger


class RdlDbBuilder(RdlParser):

    def __init__(self):
        RdlParser.__init__(self)

        self.definitions = []
        self.instances = []
        self.defaults = []
        self.anon_counter = 0

    def build_db(self, string):
        self.definitions = []
        self.instances = []
        self.defaults = []
        self.anon_counter = 0

        ast = self.parse(string)

        instances = self.process_scope('<root>', ast, is_root=True)

    def gen_anon_name(self):
        name = "@anon%d" % self.anon_counter
        self.anon_counter += 1
        return name

    def process_scope(self, name, items, is_root = False ):

        instances = InstanceScope()
        self.instances.append(instances)

        if len(self.definitions) > 0:
            inner_defs = DefinitionScope(name, parent=self.definitions[-1])
        else:
            inner_defs = DefinitionScope(name)

        self.definitions.append(inner_defs)

        try:
            for node in items:
                if isinstance(node, EnumDef):
                    self.process_enumdef(node)
                elif isinstance(node, CompDef):
                    self.process_compdef(node)
                elif isinstance(node, AnonCompInst):
                    self.process_anoncompinst(node)

        finally:

            print self.definitions[-1].members
            print self.instances[-1]

            if not is_root:
                self.instances.pop()
            self.definitions.pop()

        return instances

    def process_enumdef(self, node):

        dbentry = db.Enum(node.name)

        for encnode in node.encodings:

            self.process_enumencoding(dbentry, encnode)

        self.definitions[-1][node.name] = dbentry

    def process_compdef(self, node, anonymous=False):

        if anonymous:
            node.name = self.gen_anon_name()

        if node.type == 'field':
            print "Skipping field '%s'" % node.name
            return
        elif node.type == 'reg':
            dbentry = db.Register(node.name)
        else:
            self.db_error("Unknown component type: %s" % node.type, node)
            return

        print node.elems
        self.process_scope(node.name, node.elems)

        self.definitions[-1][node.name] = dbentry

        return dbentry

    def process_anoncompinst(self, node):

        defnode = node.comp

        definition = self.process_compdef(defnode, anonymous=True)

        for instparams in node.instances:
            self.instantiate_component(definition, instparams)


    def process_enumencoding(self, dbentry, node):

        identifier = node.mnemonic
        width = node.value[0]
        value = node.value[1]

        if width != -1:
            if dbentry.width is not None and dbentry.width != width:
                self.db_error("Enum encoding '%s' gives conflicting width %d for enum '%s', previous width is %d" % (identifier, width, dbentry.name, dbentry.width), node)
            elif dbentry.width is None:
                dbentry.width = width

        if dbentry.encoding_from_value(value) is not None:
            previous = dbentry.encoding_from_value(value)
            self.db_error("Enum encoding '%s' has duplicate value '%d', previously assigned to encoding '%s'"  % (identifier, value, previous.name), node)

        encoding = db.EnumEncoding(identifier, value)

        for prop in node.properties:
            self.process_propassign(encoding.properties, prop, RdlComponent.Enum)

        dbentry.encodings[identifier] = encoding

    def process_propassign(self, props, propassign, component_type):

        name = propassign.name
        value = None

        if name in props:
            self.db_error("Multiple assignments to a property are nor permitted", propassign)

        propdef = None
        if name in properties:
            propdef = properties[name]

            if not propdef.impl:
                self.db_error("Property '%s' is not implemented" % name, propassign)

            if component_type not in propdef.components:
                self.db_error("Property '%s' is not applicable to %s components" % (name, component_type), propassign)

            for rdltype in propdef.types:
                value = self.check_type(propassign.value, rdltype)
                if value is not None:
                    break
            else:
                self.db_error("Value '%s' is not of a legal type for property '%s'" % (propassign.value, name), propassign)

        else:
            self.db_error("Unknown property '%s'" % name, propassign)

        props[name] = db.Property(name, value, propdef)

    def check_type(self, value, rdltype):

        if rdltype is RdlType.sizedNumeric:
            if isinstance(value, tuple) and len(value) == 2:
                return value
        elif rdltype is RdlType.unsizedNumeric:
            pass
        elif rdltype is RdlType.numeric:
            pass
        elif rdltype is RdlType.boolean:
            if isinstance(value, bool):
                return value
        elif rdltype is RdlType.string:
            if isinstance(value, str):
                return value
        elif rdltype is RdlType.AccessMode:
            if isinstance(value, AccessType):
                return value
        elif rdltype is RdlType.AddressMode:
            if isinstance(value, AddressingType):
                return value
        elif rdltype is RdlType.Precedence:
            if isinstance(value, PrecedenceType):
                return value
        elif rdltype is RdlType.enum:
            if isinstance(value, InstanceRef):
                if len(value.path) != 1:
                    self.db_error("Component definitions may not be referenced hierarchically", value)

                if value.prop is not None:
                    self.db_error("Component definition references may not specify a property", value)

                definition = self.definitions[-1][value.path[0]]

                if definition is None:
                    self.error("'%s' does not reference a known definition" % value.path[0], value)
                elif not isinstance(definition, db.Enum):
                    self.crror("Expected enum name, got other", value)

                return definition
        elif rdltype is RdlType.SignalDest:
            pass
        elif rdltype is RdlType.SignalSource:
            pass

        return None

    def instantiate_component(self, definition, instparams):
        comp = copy.copy(definition)

    def db_error(self, message, node=None):

        if node is not None:
            logger.log_line(self.format_line_message(node, colorize(RED, "Error: ") + message))
        else:
            logger.log_line(colorize(RED, "Error: ") + message)

        self.syntax_errors += 1

    def token_to_index(self, token):
        if isinstance(token, RdlToken):
            return token.location.index
        elif isinstance(token, AstNode):
            return token.span[0]
        else:
            raise AssertionError("Cannot map '%s' to source location" % token)







