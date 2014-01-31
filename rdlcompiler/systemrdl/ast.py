__author__ = 'MegabytePhreak'

import types


def _indent(level):
    if level > 0:
        return '    '*level
    return ''


class AstNode(object):
    pass

    def pprint(self, level=0):
        pass

    def __str__(self):
        return self.pprint(0)


class Subscript(AstNode):
    def __init__(self, name, index):
        self.name = name
        self.index = index


class EnumDef(AstNode):
    def __init__(self, name, encodings):
        self.name = name
        self.encodings = encodings

    def pprint(self, level=0):
        strs = ["EnumDef( '%s', [\n" % self.name]
        for encoding in self.encodings:
            strs += [_indent(level+1), '%s,\n' % encoding.pprint(abs(level)+1)]
        strs += _indent(level) + '])'

        return ''.join(strs)


class EnumEncoding(AstNode):
    def __init__(self, mnemonic, value, properties):
        self.mnemonic = mnemonic
        self.value = value
        self.properties = properties

    def pprint(self, level=0):
        strs = ["EnumEncoding( '%s', %s, [" % (self.mnemonic, self.value)]
        if len(self.properties) > 0:
            strs += '\n'
            for prop in self. properties:
                strs += [_indent(level+1), '%s,\n' % prop.pprint(level+1)]
            strs += _indent(level) + '])'
        else:
            strs += '])'

        return ''.join(strs)


class PropAssign(AstNode):
    def __init__(self, name, value, set_default=False):
        self.name = name
        self.value = value
        self.set_default = set_default

    def pprint(self, level=0):
        if isinstance(self.value, types.StringTypes):
            return "PropAssign('%s', '%s')" % (self.name, self.value.encode('string-escape'))

        return "PropAssign('%s', %s)" % (self.name, self.value.pprint(level))


class IntrPropAssign(AstNode):
    def __init__(self, name, value, modifers):
        self.name = name
        self.value = value
        self.modifiers = modifers


class DynamicPropRef(AstNode):
    def __init__(self, instance, name):
        self.instance = instance
        self.name = name


class InstanceRef(AstNode):
    def __init__(self, path):
        self.path = path

    def add_child_ref(self, child):
        self.path.append(child)


class AccessType(AstNode):
    def __init__(self, value):
        if value is None:
            value = 'rw'

        if value not in ['rw', 'wr', 'r', 'w', 'na']:
            raise SyntaxError("Ilegal AccessType value '%s'" % value)

        if value == 'wr':
            value = 'rw'

        self.value = value


class AddressingType(AstNode):
    def __init__(self, value):
        if value is None:
            value = 'regalign'

        if value not in ['compact', 'regalign', 'fullalign']:
            raise SyntaxError("Ilegal AddressingType value '%s'" % value)

        self.value = value


class PrecedenceType(AstNode):
    def __init__(self, value):
        if value is None:
            value = 'sw'

        if value not in ['hw', 'sw']:
            raise SyntaxError("Ilegal PrecedenceType value '%s'" % value)

        self.value = value