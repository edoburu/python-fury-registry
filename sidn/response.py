import sys
from xml.etree import ElementTree

from sidn.constants import XMLNS
from sidn.utils import cached_property, get_node_date, get_node_text, python_2_unicode_compatible

from . import objects


def register_namespaces():
    """
    Register the namespaces in the ElementTree globals.
    This improves the output for debugging, but will override any previously registered prefixes.
    """
    for prefix, uri in XMLNS.items():
        ElementTree.register_namespace(prefix, uri)


@python_2_unicode_compatible
class XmlObject(object):
    """
    Wrapper object for EPP responses
    """

    def __init__(self, element):
        """
        :type element: xml.etree.ElementTree.Element
        """
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

    if sys.version_info[0] == 2:
        def __repr__(self):
            return '<{0} {1}>'.format(self.__class__.__name__, unicode(self).encode('utf-8'))
    else:
        def __repr__(self):
            return '<{0} {1}>'.format(self.__class__.__name__, self)


class EPPResponse(XmlObject):
    """
    Wrapper object for EPP responses
    """

    @cached_property
    def result(self):
        """
        :rtype: xml.etree.ElementTree.Element
        """
        return self.element.find('epp:result', XMLNS)

    @cached_property
    def result_code(self):
        return int(self.result.attrib['code'])

    @cached_property
    def result_msg(self):
        return self.result.find('epp:msg', XMLNS).text

    @cached_property
    def resData(self):
        """
        Return the resdata node from the response.
        Use `:meth:`~xml.etree.ElementTree.Element.find` to find child nodes.

        :rtype: xml.etree.ElementTree.Element
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

    __nonzero__ = __bool__  # python 2

    @cached_property
    def msgQ(self):
        """
        :rtype: xml.etree.ElementTree.Element
        """
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
    def message(self):
        """
        Textual content of the message (only for op="req")
        """
        if self.msgQ is None:
            return None
        return get_node_text(self.msgQ, 'epp:msg')


class SidnPollResponse(EPPPollResponse):
    """
    SIDN Extension for polling responses.
    """

    @cached_property
    def pollData(self):
        """
        Return the SIDN extension data
        """
        return SidnPollData(self.resData.find('sidn-ext-epp:pollData', XMLNS))


class SidnPollData(XmlObject):
    """
    The SIDN extension for poll data.
    """
    DOMAIN_TRANSFER_START = "domain:transfer-start"
    DOMAIN_TRANSFER = "domain:transfer"
    DOMAIN_DELETE = "domain:delete"

    @cached_property
    def command(self):
        """
        The command that is stored in the :attr:`resData`.
        This can be:

        * ``domain:transfer-start`` (:attr:`DOMAIN_TRANSFER_START`)
        * ``domain:transfer`` (:attr:`DOMAIN_TRANSFER`)
        * ``domain:delete`` (:attr:`DOMAIN_DELETE`)
        """
        return get_node_text(self.element, 'sidn-ext-epp:command')

    @cached_property
    def result(self):
        return self.element.find('sidn-ext-epp:data/epp:result', XMLNS)

    @cached_property
    def code(self):
        return int(self.result.attrib['code'])

    @cached_property
    def message(self):
        return get_node_text(self.result, 'epp:msg')

    @cached_property
    def resData(self):
        """
        The SIDN poll data has another resData node inside.
        :rtype: xml.etree.ElementTree.Element
        """
        return self.element.find('sidn-ext-epp:data/epp:resData', XMLNS)

    @cached_property
    def object(self):
        """
        Return the object wrapped in the extended notification message.
        """
        element = self.resData[0]  # type: ElementTree.Element
        if element.tag == '{urn:ietf:params:xml:ns:domain-1.0}trnData':  # full qualified name for "domain:trnData"
            trnData = self.resData.find('domain:trnData', XMLNS)
            return objects.TransferStatus.from_xml(trnData)
        else:
            raise NotImplementedError("Unsupported extension node: {}".format(element.tag))
