__author__ = 'MegabytePhreak'

from enum import Enum, unique


@unique
class RdlType(Enum):
    sizedNumeric = 'sn'
    unsizedNumeric = 'un'
    numeric = 'n'
    boolean = 'b'
    string = 's'
    AddressMode = 'AddressMode'
    Precedence = 'Precedence'
    AccessMode = 'AccessMode'
    enum = 'Enum'
    SignalDest = 'SD'
    SignalSource = 'SS'


@unique
class RdlComponent(Enum):
    Field = 'f'
    Register = 'r'
    RegisterFile = 'R'
    AddressMap = 'A'
    Signal = 'S'
    Enum = 'e'


class RdlProperty(object):
    def __init__(self, name, types, comps, impl=True):
        self.name = name

        if isinstance(types, RdlType):
            self.types = set((types,))
        else:
            for t in types:
                assert isinstance(t, RdlType)
            self.types = set(types)

        if isinstance(comps, RdlComponent):
            self.comp = set((comps,))
        else:
            for t in comps:
                assert isinstance(t, RdlComponent)
            self.comps = set(comps)

        self.impl = impl


def _gen_props():

    #l = locals()
    #for t in RdlType:
    #    l[t.value] = t
    #for c in RdlComponent:
    #    l[c.value] = t
    un = RdlType.unsizedNumeric
    sn = RdlType.sizedNumeric
    n = RdlType.numeric
    b = RdlType.boolean
    s = RdlType.string
    SS = RdlType.SignalSource
    SD = RdlType.SignalDest

    f = RdlComponent.Field
    r = RdlComponent.Register
    R = RdlComponent.RegisterFile
    A = RdlComponent.AddressMap
    S = RdlComponent.Signal
    e = RdlComponent.Enum

    return [
        RdlProperty('accesswidth',      n,              R),
        RdlProperty('activehigh',       b,              S),
        RdlProperty('activelow',        b,              S),
        RdlProperty('addressing',       RdlType.AddressMode, A),
        RdlProperty('alignment',        un,             (R, A)),
        RdlProperty('anded',            (b, SS),        f),
        RdlProperty('arbiter',          b,              A, False),
        RdlProperty('async',            b,              S),
        RdlProperty('bigendian',        b,              A),
        #This is actually a interrupt modifier
        #RdlProperty('bothedge',        b,              f),
        RdlProperty('bridge',           b,              A, False),
        RdlProperty('counter',          b,              f, False),
        RdlProperty('cpuif_reset',      b,              S),
        RdlProperty('decr',             (SS, SD),       f, False),
        RdlProperty('decrsaturate',     (n, SS, SD),    f, False),
        RdlProperty('decrthreshold',    (n, SS, SD),    f, False),
        RdlProperty('decrvalue',        (n, SS, SD),    f, False),
        RdlProperty('decrwidth',        (n, SS, SD),    f, False),
        RdlProperty('desc',             s,              (f, r, R, A, S, e)),
        RdlProperty('dontcompare',      (b, sn),        f, False),
        #RdlProperty('dontcompare',     b,              (r, R, A), False),
        RdlProperty('donttest',         (b, sn),        f, False),
        #RdlProperty('donttest',        b,              (r, R, A), False),
        RdlProperty('enable',           (SS, SD),       f, False),
        RdlProperty('encode',           RdlType.enum,   f),
        RdlProperty('errextbus',        n,              r, False),
        RdlProperty('field_reset',      n,              A),
        RdlProperty('fieldwidth',       n,              f),
        RdlProperty('halt',             SD,             f, False),
        RdlProperty('haltenable',       (SS, SD),       f, False),
        RdlProperty('haltmask',         (SS, SD),       f, False),
        RdlProperty('hw',               RdlType.AccessMode, f),
        RdlProperty('hwclr',            (b, SS, SD),    f),
        RdlProperty('hwenable',         (b, SS, SD),    f),
        RdlProperty('hwdisable',        (b, SS, SD),    f),
        RdlProperty('hwset',            (b, SS, SD),    f),
        RdlProperty('incr',             (SS, SD),       f, False),
        RdlProperty('incrsaturate',     (n, SS, SD),    f, False),
        RdlProperty('incrthreshold',    (n, SS, SD),    f, False),
        RdlProperty('incrvalue',        (n, SS, SD),    f, False),
        RdlProperty('incrwidth',        (n, SS, SD),    f, False),
        RdlProperty('intr',             b,              f),
        #RdlProperty('intr',            SS,             r),
        #This is actually a interrupt modifier
        #RdlProperty('level',           b,              f),
        RdlProperty('littlendian',      b,              A),
        RdlProperty('lsb0',             b,              A),
        RdlProperty('mask',             (SS, SD),       f),
        RdlProperty('msb0',             b,              A),
        RdlProperty('name',             s,              (f, r, R, A, S, e)),
        #This is actually a interrupt modifier
        #RdlProperty('negedge',         b,              f),
        RdlProperty('next',             (SS, SD),        f),
        #This is actually a interrupt modifier
        #RdlProperty('nonsticky',       b,              f),
        RdlProperty('ored',             (b, SS),        f, False),
        RdlProperty('overflow',         SS,             f, False),
        #This is actually a interrupt modifier
        #RdlProperty('posedge',         b,              f),
        RdlProperty('precedence',       RdlType.Precedence, f),
        RdlProperty('rclr',             b,              f),
        RdlProperty('regwidth',         n,              r),
        RdlProperty('reset',            (n, SS, SD),    f),
        RdlProperty('resetsignal',      (SS, SD),       f),
        RdlProperty('rset',             b,              f),
        RdlProperty('rsvdset',          b,              A),
        RdlProperty('rsvdsetX',         b,              A),
        RdlProperty('saturate',         (n, SS, SD),    f, False),
        RdlProperty('shared',           b,              r),
        RdlProperty('sharedextbus',     b,              (R, A)),
        RdlProperty('signalwidth',     n,              S),
        RdlProperty('singlepulse',      b,              f),
        RdlProperty('sticky',           b,              f),
        RdlProperty('stickybit',        b,              f),
        RdlProperty('sw',               RdlType.AccessMode, f),
        RdlProperty('swacc',            (b, SS),        f),
        RdlProperty('swmod',            (b, SS),        f),
        RdlProperty('swwe',             (b, SS, SD),    f),
        RdlProperty('swwel',            (b, SS, SD),    f),
        RdlProperty('sync',              b,             S),
        RdlProperty('threshold',         (n, SS),       f, False),
        RdlProperty('underflow',         SS,            f, False),
        RdlProperty('we',                (b, SS, SD),   f),
        RdlProperty('wel',               (b, SS, SD),   f),
        RdlProperty('woclr',             b,             f),
        RdlProperty('woset',             b,             f),
        RdlProperty('xored',             (b, SS),       f),
    ]


properties = _gen_props()


