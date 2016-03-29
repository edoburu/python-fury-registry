import logging
import socket
import ssl
from xml.etree import ElementTree

from sidn.constants import EPP_OK, EPP_QUEUE_EMPTY, EPP_LOGOUT_OK
from . import commands
from . import handlers
from sidn.response import NS, EPPResponse, EPPPollResponse
from sidn.utils import int32_from_net, int32_to_net, mask_sensitive_fields

logger = logging.getLogger(__name__)


class EPPError(RuntimeError):
    """
    Error response returned by the server.
    """
    def __init__(self, code, message, ext_code=None, ext_message=None):
        if ext_code:
            super(EPPError, self).__init__(u"{0} (code {1}/{2})".format(ext_message, code, ext_code))
        else:
            super(EPPError, self).__init__(u"{0} (code {1})".format(message, code))

        self.code = code
        self.message = message
        self.ext_code = ext_code
        self.ext_message = ext_message


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
        self.host = host
        self.port = port
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

    def __repr__(self):
        return "<EPP: {0}:{1}>".format(self.host, self.port)

    def __del__(self):
        # Auto logout on instance destruction.
        # This is important, to avoid overflowing the max allowed sessions.
        try:
            self.logout()
        except EPPError:
            pass  # Will occur when not properly connected
        self.socket.close()

    def cmd(self, xml, silent=False, response_class=EPPResponse):
        """
        Execute a raw request on the server.

        :rtype: sidn.response.EPPResponse
        """
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("SIDN request: %s", mask_sensitive_fields(xml))

        # Write and read
        self._write(xml)
        raw_response = self._read()
        if raw_response is None:
            raise IOError("Server disconnected")

        # Convert to response objects
        response = self._parse_response(raw_response, response_class=response_class)
        code = response.result_code
        if not silent or code not in (EPP_OK, EPP_QUEUE_EMPTY, EPP_LOGOUT_OK):
            logger.info("- [%d] %s", code, response.result_msg)

        return response

    @staticmethod
    def _parse_response(raw_response, response_class=EPPResponse):
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
        # Note for failures, multiple <result> nodes may be present for multiple error conditions.
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
        return response_class(response)

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

            logger.debug("SIDN Response: %s", xml_bytes.decode('utf-8'))
            return xml_bytes  # raw result for ElementTree to convert.
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
        """
        Perform the logout, happens automatically on ``__dell__`.
        """
        cmd = commands.epp.logout
        return self.cmd(cmd, silent=True)

    def poll(self, ack=False, transaction_id=None):
        """
        Poll for service notification messages.

        It returns the first message.
        When :meth:`poll` is called again with ``ack`` to True, the message will be removed.
        The next call to :meth:`poll` will return the next available message.

        :param ack: Set to true to acknowledge the message, and remove it from the server.
        :param transaction_id:
        :rtype: sidn.response.EPPPollResponse
        """
        # https://tools.ietf.org/html/rfc5730#section-2.9.2.3
        if ack:
            op = 'ack'  # acknowledge read, and remove it
        else:
            op = 'req'  # Get first message
        cmd = commands.epp.poll(op=op, transaction_id=transaction_id)
        return self.cmd(cmd, response_class=EPPPollResponse)

    @property
    def domains(self):
        """
        :rtype: sidn.handlers.DomainHandler
        """
        # These are not assigned to the class, to avoid circular references.
        # Only keep references temporary, so __del__ will be called.
        return handlers.DomainHandler(self)

    @property
    def contacts(self):
        """
        :rtype: sidn.handlers.ContactHandler
        """
        return handlers.ContactHandler(self)

    @property
    def hosts(self):
        """
        :rtype: sidn.handlers.HostHandler
        """
        return handlers.HostHandler(self)
