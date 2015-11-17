"""
Internal utils
"""
import re
import sys
import struct
from xml.sax.saxutils import escape

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
    format_32 = ">I"
    if struct.calcsize(format_32) < 4:
        format_32 = ">L"
        if struct.calcsize(format_32) != 4:
            raise Exception("Cannot find a 32 bits integer")
    elif struct.calcsize(format_32) > 4:
        format_32 = ">H"
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
