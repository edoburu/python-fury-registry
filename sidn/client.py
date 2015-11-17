import logging
import socket
import ssl
from xml.etree import ElementTree

from sidn.constants import EPP_OK, EPP_QUEUE_EMPTY, EPP_LOGOUT_OK
from . import commands
from . import handlers
from .handlers import NS
from sidn.utils import int32_from_net, int32_to_net, mask_sensitive_fields

logger = logging.getLogger(__name__)


class EPP(object):
    """
    The EPP client
    """

    def __init__(self, host, port=700, username=None, password=None, certfile=None, timeout=2):
        """
        Initialize the client.
        This establishes a connection to the SIDN DRS5 system via EPP.

        :raises socket.error: In case the connection failed.
        """
        # Add handlers
        self.domains = handlers.DomainHandler(self)
        self.contacts = handlers.ContactHandler(self)
        self.hosts = handlers.HostHandler(self)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(timeout)
        self.socket.connect((host, port))
        try:
            self.ssl = ssl.wrap_socket(self.socket, certfile=certfile)
        except socket.error:
            logger.error("ERROR: Could not setup a secure connection. Check whether your IP is allowed to connect to the host.")
            raise

        self._read_greeting()
        if username and password:
            self.login(username, password)

    def __del__(self):
        try:
            self.logout()
            self.socket.close()
        except EPPError:
            """ Will occur when not properly connected """

    def cmd(self, cmd, silent=False):
        """
        Execute a raw request on the server.

        :rtype: EPPResponse
        """
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("SIDN request: %s", mask_sensitive_fields(cmd))

        # Write and read
        self._write(cmd)
        raw_response = self._read()

        # Convert to response objects
        response = self._parse_response(raw_response)
        code = response.result_code
        if not silent or code not in (EPP_OK, EPP_QUEUE_EMPTY, EPP_LOGOUT_OK):
            logger.info("- [%d] %s", code, response.result_msg)

        return response

    @staticmethod
    def _parse_response(raw_response):
        # Standard wrapper:
        # <epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
        #   <response>
        #     <result code="1000"><msg>..</msg></result>
        #     <resData>..</resData>
        #   </response>
        # </epp>
        #
        xml = ElementTree.XML(raw_response)
        response = xml.find('epp:response', NS)

        # Check <result> node
        result = response.find('epp:result', NS)
        result_code = int(result.attrib['code'])
        if result_code >= 2000:
            msg = result.find('epp:msg', NS)
            ext = response.find('epp:extension', NS)
            if ext is not None:
                msg_node = ext.find('sidn-ext-epp:ext/sidn-ext-epp:response/sidn-ext-epp:msg', NS)
                ext_code = msg_node.attrib['code']
                ext_message = msg_node.text
            else:
                ext_code = ext_message = None

            raise EPPError(result_code, msg.text, ext_code, ext_message)
        return EPPResponse(response)

    def _read(self):
        # The first 4 bytes indicate the size.
        # Read then, then read N bytes.
        size_field = self.ssl.read(4)
        if size_field:
            size = int32_from_net(size_field) - 4
            remaining = size
            xml_bytes = ''
            while remaining > 0:
                xml_bytes += self.ssl.read(remaining)
                remaining = size - len(xml_bytes)

            logger.debug("SIDN Response: %s", xml_bytes)
            return xml_bytes.decode('utf-8')
        else:
            return None

    def _write(self, xml):
        # Convert to the raw data to be send.
        # utf-8 may take multiple bytes per character.
        xml_bytes = xml.encode('utf-8') + "\r\n"
        # +4 for the length field itself (section 4 mandates that)
        length = int32_to_net(len(xml_bytes) + 4)
        self.ssl.send(length)
        return self.ssl.send(xml_bytes)

    def _read_greeting(self):
        # Read greeting
        raw_response = self._read()
        xml = ElementTree.XML(raw_response)

        # <epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
        #   <greeting>
        #     <svID>..</svID>
        #     <svcMenu>
        #       <version>1.0</version>
        #        ...
        #     </svcMenu>
        #   </greeting>
        # </epp>
        greeting = xml.find('epp:greeting', NS)
        svcMenu = greeting.find('epp:svcMenu', NS)

        svid = greeting.find('epp:svID', NS).text
        version = svcMenu.find('epp:version', NS).text
        logger.info("Connected to %s (v%s)\n", svid, version)

    def login(self, username, password):
        """
        Perform the login.
        """
        # Login
        xml = commands.epp.login(username, password)
        return self.cmd(xml, silent=True)

    def logout(self):
        cmd = commands.epp.logout
        return self.cmd(cmd, silent=True)

    def poll(self, transaction_id=None):
        cmd = commands.epp.poll(transaction_id)
        return self.cmd(cmd)


class EPPResponse(object):
    """
    Wrapper object for EPP responses
    """

    def __init__(self, response):
        """
        :type response: xml.etree.ElementTree.Element
        """
        self.response = response

    @property
    def result(self):
        return self.response.find('epp:result', NS)

    @property
    def result_code(self):
        return int(self.result.attrib['code'])

    @property
    def result_msg(self):
        return self.result.find('epp:msg', NS).text

    @property
    def resData(self):
        """
        Return the resdata node from the response

        :rtype: xml.etree.ElementTree.Element
        """
        resData = self.response.find('epp:resData', NS)
        if resData is None:
            raise AttributeError("There is no resData node in this response")
        return resData


class EPPError(RuntimeError):
    """
    Error response returned by the server.
    """
    def __init__(self, code, message, ext_code=None, ext_message=None):
        if ext_code:
            super(EPPError, self).__init__("{0} (code {1}/{2})".format(ext_message, code, ext_code))
        else:
            super(EPPError, self).__init__("{0} (code {1})".format(message, code))

        self.code = code
        self.message = message
        self.ext_code = ext_code
        self.ext_message = ext_message
