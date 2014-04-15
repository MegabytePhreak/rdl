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

    def pprint(self, level=0):
        return "Subscript('%s', %d)" % (self.name, self.index)


class EnumDef(AstNode):
    def __init__(self, name, encodings):
        self.name = name
        self.encodings = encodings

    def pprint(self, level=0):
        strs = ["EnumDef( '%s', [\n" % self.name]
        for encoding in self.encodings:
            strs += [_indent(level+2), '%s,\n' % encoding.pprint(abs(level)+2)]
        strs += _indent(level+1) + '])'

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
                strs += [_indent(level+2), '%s,\n' % prop.pprint(level+2)]
            strs += _indent(level+1) + '])'
        else:
            strs += '])'

        return ''.join(strs)

class PropAssign(AstNode):
    def __init__(self, name, value, set_default=False):
        self.name = name
        self.value = value
        self.set_default = set_default

    def pprint(self, level=0):
        value = self.value

        if hasattr(self.value, 'pprint'):
            value = value.pprint(level+1)
        elif isinstance(value, types.StringTypes):
            value = (value[:57] + '...') if len(value) > 60 else value
            value = "'" + value.encode('string-escape') + "'"

        if isinstance(self.name, types.StringTypes):
            return "PropAssign('%s', %s)" % (self.name, value)
        else:
            return "PropAssign(%s, %s)" % (self.name, value)


class IntrPropAssign(AstNode):
    def __init__(self, name, value, modifers):
        self.name = name
        self.value = value
        self.modifiers = modifers

    def pprint(self, level=0):
        return "IntrPropAssign(%s, %s, %s)" % (self.name, self.value, self.modifiers)


class InstanceRef(AstNode):
    def __init__(self, path, prop = None):
        self.path = path
        self.prop = prop

    def add_child_ref(self, child):
        self.path.append(child)

    def set_prop(self, prop):
        self.prop = prop

    def pprint(self, level=0):
        strs = ['InstanceRef([']
        for i, elem in enumerate(self.path):
            if hasattr(elem, 'pprint'):
                strs += [elem.pprint(level+1), ', ']
            else:
                strs += ["'%s', " % elem]

        strs[-1] = strs[-1][:-2]
        strs += ['],']

        if self.prop is not None:
            strs += ", '%s')" % self.prop
        else:
            strs += ')'

        return ''.join(strs)


class AccessType(AstNode):
    def __init__(self, value):
        if value is None:
            value = 'rw'

        if value not in ['rw', 'wr', 'r', 'w', 'na']:
            raise SyntaxError("Illegal AccessType value '%s'" % value)

        if value == 'wr':
            value = 'rw'

        self.value = value

    def pprint(self, level=0):
        return 'AccessType(%s)' % repr(self.value)


class AddressingType(AstNode):
    def __init__(self, value):
        if value is None:
            value = 'regalign'

        if value not in ['compact', 'regalign', 'fullalign']:
            raise SyntaxError("Ilegal AddressingType value '%s'" % value)

        self.value = value

    def pprint(self, level=0):
        return 'AddressingType(%s)' % repr(self.value)


class PrecedenceType(AstNode):
    def __init__(self, value):
        if value is None:
            value = 'sw'

        if value not in ['hw', 'sw']:
            raise SyntaxError("Ilegal PrecedenceType value '%s'" % value)

        self.value = value

    def pprint(self, level=0):
        return 'PrecedenceType(%s)' % repr(self.value)


class CompDef(AstNode):
    def __init__(self, ctype, name, elems):
        self.type = ctype
        self.name = name
        self.elems = elems

    def pprint(self, level=0):
        strs = ["CompDef( '%s', '%s', [\n" % (self.type, self.name)]
        for encoding in self.elems:
            strs += [_indent(level+1), '%s,\n' % encoding.pprint(abs(level)+1)]
        strs += _indent(level+1) + '])'

        return ''.join(strs)


class InstParams(AstNode):
    def __init__(self, name, array_params, reset_value, addr_alloc):
        self.name = name
        self.array_params = array_params
        self.reset_value = reset_value
        self.addr_alloc = addr_alloc

    def pprint(self, level=0):
        return "InstParams('%s', %s, %s, %s)" % (self.name, self.array_params, self.reset_value, self.addr_alloc)


class CompInst(AstNode):
    def __init__(self, compname, instances, location=None):
        self.compname = compname
        self.instances = instances
        self.location = location

    def pprint(self, level=0):
        strs = ["CompInst( '%s', [" % (self.compname,)]
        if len(self.instances) > 1:
            strs += '\n'
            for instance in self.instances:
                strs += [_indent(level+2), '%s,\n' % instance.pprint(abs(level)+2)]
            strs += _indent(level+1) + '],\n'
            strs += _indent(level+1) + '%s)' % repr(self.location)
        else:
            if len(self.instances) == 1:
                strs += ['%s], ' % self.instances[0].pprint(abs(level)+1)]
            else:
                strs += '], '
            strs += '%s)' % repr(self.location)

        return ''.join(strs)


class AnonCompInst(AstNode):
    def __init__(self, comptype, compelems, instances, location=None):
        self.comp = CompDef(comptype, None, compelems)
        self.instances = instances
        self.location = location

    def pprint(self, level=0):
        strs = ["AnonCompInst( '%s', [\n" % (self.comp.type,)]
        for encoding in self.comp.elems:
            strs += [_indent(level+1), '%s,\n' % encoding.pprint(abs(level)+1)]
        strs += _indent(level+1) + '], ['

        if len(self.instances) > 1:
            strs += '\n'
            for instance in self.instances:
                strs += [_indent(level+2), '%s,\n' % instance.pprint(abs(level)+2)]
            strs += _indent(level+1) + '],\n'
            strs += _indent(level+1) + '%s)' % repr(self.location)
        else:
            if len(self.instances) == 1:
                strs += ['%s], ' % self.instances[0].pprint(abs(level)+1)]
            else:
                strs += '], '
            strs += '%s)' % repr(self.location)
        return ''.join(strs)