"""
Internal utils
"""
import re
import sys
import struct
import dateutil.parser
from xml.sax import saxutils

from sidn.constants import NS

RE_CL_ID = re.compile(r'<clID>[^<]+</clID>')
RE_PW = re.compile(r'<pw>[^<]+</pw>')


def python_2_unicode_compatible(klass):
    """
    A decorator that defines __unicode__ and __str__ methods under Python 2.
    Under Python 3 it does nothing.

    To support Python 2 and 3 with a single code base, define a __str__ method
    returning text and apply this decorator to the class.
    """
    if sys.version_info[0] == 2:
        klass.__unicode__ = klass.__str__
        klass.__str__ = lambda self: self.__unicode__().encode('utf-8')
    return klass


class cached_property(object):
    """
    Decorator that converts a method with a single self argument into a
    property cached on the instance.

    Optional ``name`` argument allows you to make cached properties of other
    methods. (e.g.  url = cached_property(get_absolute_url, name='url') )
    """
    def __init__(self, func, name=None):
        self.func = func
        self.__doc__ = getattr(func, '__doc__')
        self.name = name or func.__name__

    def __get__(self, instance, type=None):
        if instance is None:
            return self
        res = instance.__dict__[self.name] = self.func(instance)
        return res


def xml_format(xml, **data):
    """
    Apply a str.format() format for XML, with data escaped.
    """
    data = _xml_escape(**data)
    return xml.format(**data)


def _xml_escape(**data):
    """
    Escape the data for inclusion in XML
    """
    return dict((k, escape(v)) for k, v in data.iteritems())


def escape(value):
    """
    Escape a single value for XML
    """
    if value is None:
        return None
    elif isinstance(value, (int, long)):
        return str(value)
    else:
        return saxutils.escape(value)


def mask_sensitive_fields(cmd):
    cmd = RE_CL_ID.sub('<clID>***</clID>', cmd)
    cmd = RE_PW.sub('<pw>***</pw>', cmd)
    return cmd


def _get_int32_format():
    """
    Get the struct pack/unpack syntax for 32 bit integers.
    """
    # http://www.bortzmeyer.org/4934.html
    # Get the size of C integers. We need 32 bits unsigned.
    format_32 = ">I"  # big endian unsigned int
    if struct.calcsize(format_32) < 4:
        format_32 = ">L"  # big endian unsigned long
        if struct.calcsize(format_32) != 4:
            raise Exception("Cannot find a 32 bits integer")
    elif struct.calcsize(format_32) > 4:
        format_32 = ">H"  # big endian unsigned short
        if struct.calcsize(format_32) != 4:
            raise Exception("Cannot find a 32 bits integer")
    else:
        pass
    return format_32


INT32_FORMAT = _get_int32_format()


def int32_from_net(data):
    return struct.unpack(INT32_FORMAT, data)[0]


def int32_to_net(value):
    return struct.pack(INT32_FORMAT, value)


def get_node_text(parent_node, node_name, default=None):
    """
    Get the text content for a child node.

    :type parent_node: xml.etree.ElementTree.Element
    :type node_name: str
    :rtype: unicode|None
    """
    if parent_node is None:
        return default
    # Handling of optional fields
    return parent_node.findtext(node_name, namespaces=NS)


def get_node_date(parent_node, node_name):
    """
    Read the date value for a child node.

    :type parent_node: xml.etree.ElementTree.Element
    :type node_name: str
    :rtype: datetime|None
    """
    text = get_node_text(parent_node, node_name)
    return parse_iso_date(text)


def parse_iso_date(date):
    """
    Parse the ISO date format the EPP submits.
    """
    if date is None:
        return None
    else:
        # Dates like: 1995-12-10T23:00:00.000Z
        return dateutil.parser.parse(date)
