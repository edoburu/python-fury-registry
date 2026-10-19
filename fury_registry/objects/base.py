from __future__ import annotations

from typing import Self
from xml.etree.ElementTree import Element


class ParsedObject:
    """
    Base interface to parse XML nodes.
    """

    @classmethod
    def from_xml(cls, node: Element, extension: Element | None = None) -> Self:
        return cls(**cls.parse_xml_fields(node, extension=extension))

    @classmethod
    def parse_xml_fields(cls, node: Element, extension: Element | None = None) -> dict:
        raise NotImplementedError("missing parse_xml_fields")
