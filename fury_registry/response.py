from __future__ import annotations

from functools import cached_property
from xml.etree import ElementTree

from fury_registry.constants import XMLNS
from fury_registry.utils import get_node_date, get_node_text

from . import objects


def register_namespaces():
    """
    Register the namespaces in the ElementTree globals.
    This improves the output for debugging, but will override any previously registered prefixes.
    """
    for prefix, uri in XMLNS.items():
        ElementTree.register_namespace(prefix, uri)


class XmlObject:
    """
    Wrapper object for EPP responses
    """

    def __init__(self, element: ElementTree.Element):
        self.element = element

    def __str__(self):
        """
        Display the element as XML.

        Call :func:`register_namespaces` in case you like to have readable XML prefixes.
        """
        xml = ElementTree.tostring(self.element)
        if isinstance(xml, bytes):  # Python 3
            xml = xml.decode()
        return xml

    def __repr__(self):
        return f'<{self.__class__.__name__} {self}>'


class EPPResponse(XmlObject):
    """
    Wrapper object for EPP responses
    """

    @cached_property
    def result(self) -> ElementTree.Element|None:
        return self.element.find('epp:result', XMLNS)

    @cached_property
    def result_code(self) -> int:
        return int(self.result.attrib['code'])

    @cached_property
    def result_msg(self) -> str|None:
        return self.result.find('epp:msg', XMLNS).text

    @cached_property
    def resData(self) -> ElementTree.Element:
        """
        Return the resdata node from the response.
        Use `:meth:`~xml.etree.ElementTree.Element.find` to find child nodes.
        """
        resData = self.element.find('epp:resData', XMLNS)
        if resData is None:
            raise AttributeError("There is no resData node in this response")
        return resData

    @cached_property
    def extension(self):
        return self.element.find('epp:extension', XMLNS)

    @cached_property
    def clTRID(self):
        return get_node_text(self.element.find('epp:trID', XMLNS), 'epp:clTRID')

    @cached_property
    def svTRID(self):
        return get_node_text(self.element.find('epp:trID', XMLNS), 'epp:svTRID')


class EPPPollResponse(EPPResponse):
    """
    Wrapper object for the EPP Poll response
    """

    def __bool__(self):
        return self.msgQ is not None  # self.result_code == EPP_QUEUE_NOT_EMPTY

    @cached_property
    def msgQ(self) -> ElementTree.Element|None:
        return self.element.find('epp:msgQ', XMLNS)

    @cached_property
    def queue_count(self):
        """
        Number of messages in the queue.
        """
        if self.msgQ is None:
            return 0
        return int(self.msgQ.attrib['count'])

    @cached_property
    def queue_id(self):
        """
        ID of the currently fetched message.
        """
        if self.msgQ is None:
            return None
        return int(self.msgQ.attrib['id'])

    @cached_property
    def queue_date(self):
        """
        Date of the currently fetched message (only for op="req")
        """
        if self.msgQ is None:
            return None
        return get_node_date(self.msgQ, 'epp:qDate')

    @cached_property
    def message(self) -> str|None:
        """
        Textual content of the message (only for op="req")
        """
        if self.msgQ is None:
            return None
        return get_node_text(self.msgQ, 'epp:msg')

    @cached_property
    def trnData(self) -> objects.TransferStatus:
        """
        Return the object wrapped in the resData.
        """
        element = self.resData[0]  # type: ElementTree.Element
        if element.tag == '{urn:ietf:params:xml:ns:domain-1.0}trnData':  # full qualified name for "domain:trnData"
            trnData = self.resData.find('domain:trnData', XMLNS)
            return objects.TransferStatus.from_xml(trnData)
        else:
            raise NotImplementedError(f"Unsupported extension node: {element.tag}")
