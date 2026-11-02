from __future__ import annotations

from typing import Self
from xml.etree.ElementTree import Element


class ParsedObject:
    """Base interface to parse XML nodes.
    """

    @classmethod
    def from_xml(cls, node: Element, extension: Element | None = None) -> Self:
        return cls(**cls.parse_xml_fields(node, extension=extension))

    @classmethod
    def parse_xml_fields(cls, node: Element, extension: Element | None = None) -> dict:
        raise NotImplementedError("missing parse_xml_fields")


class BaseCheckData(ParsedObject):
    """Result from a check"""

    @classmethod
    def parse_xml_fields(cls, chkdata: Element, extension=None):
        if chkdata is None:
            raise ValueError("chkData not provided")

        # Support 3 namespaces and subtle variations:
        # - domain:chkData/domain:cd/domain:name
        # - host:chkData/host:cd/host:name
        # - contact:chkData/contact:cd/contact:id
        ns = chkdata.tag[:chkdata.tag.find('}') + 1]

        cd = chkdata.find(f"{ns}cd")
        id_tag = cd[0]  # contact:id or domain:name, host:name
        reason = cd.find(f"{ns}reason")

        return dict(
            identifier=id_tag.text,
            avail=id_tag.attrib["avail"] in ("1", "true"),
            reason=reason.text if reason is not None else None,
        )

    def __init__(self, identifier: str, avail: bool, reason: str|None):
        self._identifier = identifier
        self.avail = avail
        self.reason = reason

    def __bool__(self):
        return self.avail

    def __repr__(self):
        if self.reason:
            return f"<Check {self._identifier}: {self.avail} ({self.reason})>"
        else:
            return f"<Check {self._identifier}: {self.avail}>"

    def __str__(self):
        return self._identifier
