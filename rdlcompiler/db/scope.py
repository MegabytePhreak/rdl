__author__ = 'megabytephreak'


class DefinitionScope(object):

    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent

        self.members = {}

    def lookup(self, identifier):
        if identifier in self.members:
            return self.members[identifier]
        elif self.parent is not None:
            return self.parent.lookup(identifier)
        return None

    def get(self, identifier, default = None):
        item = self.lookup(identifier)
        if identifier is not None:
            return item
        else:
            if default is not None:
                return default
            else:
                raise KeyError("Identifier '%s' does not name an component definition in this or any enclosing scope." % identifier)

    def __getitem__(self, identifier):
        return self.get(identifier)

    def __setitem__(self, identifier, value):
        item = self.lookup(identifier)
        if item is not None:
            raise KeyError("Identifier '%s' already names an component definition")
        else:
            self.members[identifier] = value

    def __contains__(self, identifier):
        return self.lookup(identifier) is not None

InstanceScope = dict
