__author__ = 'megabytephreak'


class Enum(object):

    def __init__(self, name):
        self.name = name
        self.width = None
        self.encodings = {}

    def encoding_from_value(self, value):
        for encoding in self.encodings.itervalues():
            if encoding.value == value:
                return encoding
        else:
            return None


class EnumEncoding(object):

    def __init__(self, name, value):
        self.name = name
        self.value = value
        self.properties = {}


class Property(object):

    def __init__(self, name, value, type=None, is_default=False):
        self.name = name
        self.value = value
        self.type = type
        self.is_default = is_default


class Component(object):
    pass

    def __init__(self):
        self.properties = {}


class Register(Component):

    def __init__(self, name):
        super(Register, self).__init__()

        self.name = name
        self.fields = {}
        self.width = None


class Field(Component):

    def __init__(self, name):
        super(Register, self).__init__()

        self.name = name
        self.width = None