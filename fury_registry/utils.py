"""
Internal utils
"""
import re
import struct
from xml.sax import saxutils

import dateutil.parser
from fury_registry.constants import XMLNS

RE_CL_ID = re.compile(r'<clID>[^<]+</clID>')
RE_PW = re.compile(r'<pw>[^<]+</pw>')


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
    return {k: escape(v) for k, v in data.items()}


def escape(value):
    """
    Escape a single value for XML
    """
    if value is None:
        return None
    elif isinstance(value, int):
        return str(value)
    else:
        return saxutils.escape(value)


def mask_sensitive_fields(cmd):
    cmd = RE_CL_ID.sub('<clID>***</clID>', cmd)
    cmd = RE_PW.sub('<pw>***</pw>', cmd)
    return cmd


def int32_from_net(data):
    return struct.unpack(">I", data)[0]


def int32_to_net(value):
    return struct.pack(">I", value)


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
    return parent_node.findtext(node_name, namespaces=XMLNS)


def get_node_date(parent_node, node_name):
    """
    Read the date value for a child node.

    :type parent_node: xml.etree.ElementTree.Element
    :type node_name: str
    :rtype: datetime|None
    """
    # Dates like: 1995-12-10T23:00:00.000Z
    text = get_node_text(parent_node, node_name)
    return dateutil.parser.parse(text) if text else None
