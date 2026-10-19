"""Internal utils
"""

from __future__ import annotations

import re
import struct
from datetime import datetime
from xml.etree.ElementTree import Element
from xml.sax import saxutils

import dateutil.parser

from fury_registry.constants import XMLNS

RE_CL_ID = re.compile(r"<clID>[^<]+</clID>")
RE_PW = re.compile(r"<pw>[^<]+</pw>")


def xml_format(xml: str, **data: int | str | None) -> str:
    """Apply a str.format() format for XML, with data escaped.
    """
    data = {k: escape(v) for k, v in data.items()}
    return xml.format(**data)


def escape(value: int | str | None) -> str | None:
    """Escape a single value for XML
    """
    if value is None:
        return None
    if isinstance(value, int):
        return str(value)
    return saxutils.escape(value)


def mask_sensitive_fields(cmd: str) -> str:
    cmd = RE_CL_ID.sub("<clID>***</clID>", cmd)
    cmd = RE_PW.sub("<pw>***</pw>", cmd)
    return cmd


def int32_from_net(data: bytes) -> int:
    return struct.unpack(">I", data)[0]


def int32_to_net(value: int) -> bytes:
    return struct.pack(">I", value)


def get_node_text(
    parent_node: Element | None, node_name: str, default=None,
) -> str | None:
    """Get the text content for a child node."""
    if parent_node is None:
        return default
    # Handling of optional fields
    return parent_node.findtext(node_name, namespaces=XMLNS)


def get_node_date(parent_node: Element | None, node_name: str) -> datetime | None:
    """Read the date value for a child node."""
    # Dates like: 1995-12-10T23:00:00.000Z
    text = get_node_text(parent_node, node_name)
    return dateutil.parser.parse(text) if text else None
