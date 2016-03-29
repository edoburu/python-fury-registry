import dateutil.parser

from xml.etree import ElementTree

import sys

from sidn.constants import EPP_QUEUE_NOT_EMPTY
from sidn.utils import python_2_unicode_compatible, cached_property

NS = {
    # Possible namespaces in the response
    # See greeting message for all possible supported extensions
    'epp': 'urn:ietf:params:xml:ns:epp-1.0',  # Base EPP; https://tools.ietf.org/html/rfc5730
    'obj': 'urn:ietf:params:xml:ns:obj-1.0',  # Base EPP; https://tools.ietf.org/html/rfc5730
    'domain': 'urn:ietf:params:xml:ns:domain-1.0',  # Domain name mapping; https://tools.ietf.org/html/rfc5731
    'host': 'urn:ietf:params:xml:ns:host-1.0',  # Host mapping; https://tools.ietf.org/html/rfc5732
    'contact': 'urn:ietf:params:xml:ns:contact-1.0',  # Contact mapping; https://tools.ietf.org/html/rfc5733
    'secDNS': 'urn:ietf:params:xml:ns:secDNS-1.1',  # DNSSec; https://tools.ietf.org/html/rfc5910
    'sidn-ext-epp': 'http://rxsd.domain-registry.nl/sidn-ext-epp-1.0',  # SIDN specific bits
}


def register_namespaces():
    """
    Register the namespaces in the ElementTree globals.
    This improves the output for debugging, but will override any previously registered prefixes.
    """
    for prefix, uri in NS.items():
        ElementTree.register_namespace(prefix, uri)


@python_2_unicode_compatible
class EPPResponse(object):
    """
    Wrapper object for EPP responses
    """

    def __init__(self, response):
        """
        :type response: xml.etree.ElementTree.Element
        """
        self.response = response

    def __str__(self):
        """
        Display the element as XML.

        Call :func:`register_namespaces` in case you like to have readable XML prefixes.
        """
        return ElementTree.tostring(self.response)

    if sys.version_info[0] == 2:
        def __repr__(self):
            return '<EPPResponse {0}>'.format(unicode(self).encode('utf-8'))
    else:
        def __repr__(self):
            return '<EPPResponse {0}>'.format(self)

    @cached_property
    def result(self):
        """
        :rtype: xml.etree.ElementTree.Element
        """
        return self.response.find('epp:result', NS)

    @cached_property
    def result_code(self):
        return int(self.result.attrib['code'])

    @cached_property
    def result_msg(self):
        return self.result.find('epp:msg', NS).text

    @cached_property
    def resData(self):
        """
        Return the resdata node from the response.
        Use `:meth:`~xml.etree.ElementTree.Element.find` to find child nodes.

        :rtype: xml.etree.ElementTree.Element
        """
        resData = self.response.find('epp:resData', NS)
        if resData is None:
            raise AttributeError("There is no resData node in this response")
        return resData

    @cached_property
    def extension(self):
        return self.response.find('epp:extension', NS)

    @cached_property
    def clTRID(self):
        return get_node_text(self.response.find('epp:trID', NS), 'epp:clTRID')

    @cached_property
    def svTRID(self):
        return get_node_text(self.response.find('epp:trID', NS), 'epp:svTRID')


class EPPPollResponse(EPPResponse):
    """
    Wrapper object for the EPP Poll response
    """

    def __init__(self, response):
        super(EPPPollResponse, self).__init__(response)

    def __bool__(self):
        return self.msgQ is not None  # self.result_code == EPP_QUEUE_NOT_EMPTY

    __nonzero__ = __bool__  # python 2

    @cached_property
    def msgQ(self):
        """
        :rtype: xml.etree.ElementTree.Element
        """
        return self.response.find('epp:msgQ', NS)

    @cached_property
    def message_count(self):
        if self.msgQ is None:
            return 0
        return int(self.msgQ.attrib['count'])

    @cached_property
    def message_id(self):
        if self.msgQ is None:
            return None
        return int(self.msgQ.attrib['id'])

    @cached_property
    def message_date(self):
        if self.msgQ is None:
            return None
        return get_node_date(self.msgQ, 'epp:qDate')

    @cached_property
    def message(self):
        if self.msgQ is None:
            return None
        return get_node_text(self.msgQ, 'epp:msg')


def get_node_text(parent_node, node_name):
    """
    Get the text content for a child node.

    :type parent_node: xml.etree.ElementTree.Element
    :type node_name: str
    :rtype: unicode|None
    """
    if parent_node is None:
        return None
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
