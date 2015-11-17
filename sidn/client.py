import logging
import socket
import ssl
from BeautifulSoup import BeautifulStoneSoup  # TODO: replace this horrable class. It even case insensitive
from . import commands
from . import handlers
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
        """
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("SIDN request: %s", mask_sensitive_fields(cmd))
        self._write(cmd)
        raw_response = self._read()
        logger.debug("SIDN Response: %s", raw_response)

        soup = BeautifulStoneSoup(raw_response)
        if not soup:
            raise RuntimeError("Invalid response, XML soup")

        response = soup.find('response')
        result = soup.find('result')
        code = int(result['code'])
        response_code = int(response.result['code'])
        if response_code >= 2000:
            raise EPPError(response_code, response.result.msg.text)

        if not silent or code not in (1000, 1300, 1500):
            logger.info("- [%d] %s", code, result.msg.text)

        return response

    def _read(self):
        # The first 4 bytes indicate the size.
        # Read then, then read N bytes.
        length = self.ssl.read(4)
        if length:
            i = int32_from_net(length) - 4
            xml_bytes = self.ssl.read(i)
            return xml_bytes.decode('utf-8')

    def _write(self, xml):
        # Convert to the raw data to be send.
        # utf-8 may take multiple bytes per character.
        xml_bytes = xml.encode('utf-8') + "\r\n"
        # +4 for the length field itself (section 4 mandates that)
        length = int32_to_net(len(xml_bytes) + 4)
        self.ssl.send(length)
        return self.ssl.send(xml_bytes)

    def login(self, username, password):
        """
        Perform the login.
        """
        # Read greeting
        greeting = self._read()
        soup = BeautifulStoneSoup(greeting)
        svid = soup.find('svid')
        version = soup.find('version')
        logger.info("Connected to %s (v%s)\n", svid.text, version.text)

        # Login
        xml = commands.epp.login(username, password)
        return self.cmd(xml, silent=True)

    def logout(self):
        cmd = commands.epp.logout
        return self.cmd(cmd, silent=True)

    def poll(self, transaction_id=None):
        cmd = commands.epp.poll(transaction_id)
        return self.cmd(cmd)


class EPPError(RuntimeError):
    """
    Error response returned by the server.
    """
    def __init__(self, code, message):
        super(EPPError, self).__init__(message)
        self.code = code
        self.message = message
