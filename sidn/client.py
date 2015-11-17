#!/usr/bin/env python
import logging
import re
import socket
import ssl
import struct
from BeautifulSoup import BeautifulStoneSoup  # TODO: replace this horrable class. It even case insensitive
from . import commands

logger = logging.getLogger(__name__)

RE_CL_ID = re.compile(r'<clID>[^<]+</clID>')
RE_PW = re.compile(r'<pw>[^<]+</pw>')


class EPP(object):

    def __init__(self, host, port, user, password, certfile=None):
        self.connected = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(2)
        self.socket.connect((host, port))
        try:
            self.ssl = ssl.wrap_socket(self.socket, certfile=certfile)
        except socket.error:
            logger.error("ERROR: Could not setup a secure connection. Check whether your IP is allowed to connect to the host.")
            raise
        self.format_32 = self.format_32()
        self.login(user, password)

    def __del__(self):
        try:
            self.logout()
            self.socket.close()
        except EPPError:
            """ Will occur when not properly connected """
            pass

    def cmd(self, cmd, silent=False):
        """
        Execute a command on the server.
        """
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("SIDN request: %s", _mask_sensitive_fields(cmd))
        self._write(cmd)
        raw_response = self._read()
        logger.debug("SIDN Response: %s", raw_response)

        soup = BeautifulStoneSoup(raw_response)
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
            i = _int32_from_net(length) - 4
            xml_bytes = self.ssl.read(i)
            return xml_bytes.decode('utf-8')

    def _write(self, xml):
        # Convert to the raw data to be send.
        # utf-8 may take multiple bytes per character.
        xml_bytes = xml.encode('utf-8') + "\r\n"
        # +4 for the length field itself (section 4 mandates that)
        length = _int32_to_net(len(xml_bytes) + 4)
        self.ssl.send(length)
        return self.ssl.send(xml_bytes)

    def login(self, user, password):
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
        xml = commands.login % dict(user=user, password=password)
        return self.cmd(xml, silent=True)

    def logout(self):
        cmd = commands.logout
        return self.cmd(cmd, silent=True)

    def poll(self):
        cmd = commands.poll
        return self.cmd(cmd)


class EPPError(RuntimeError):
    """
    Error response returned by the server.
    """
    def __init__(self, code, message):
        super(EPPError, self).__init__(message)
        self.code = code
        self.message = message


def _mask_sensitive_fields(cmd):
    cmd = RE_CL_ID.sub('<clID>***</clID>', cmd)
    cmd = RE_PW.sub('<pw>***</pw>', cmd)
    return cmd


def _get_int32_format():
    """
    Get the struct pack/unpack syntax for 32 bit integers.
    """
    # http://www.bortzmeyer.org/4934.html
    # Get the size of C integers. We need 32 bits unsigned.
    format_32 = ">I"
    if struct.calcsize(format_32) < 4:
        format_32 = ">L"
        if struct.calcsize(format_32) != 4:
            raise Exception("Cannot find a 32 bits integer")
    elif struct.calcsize(format_32) > 4:
        format_32 = ">H"
        if struct.calcsize(format_32) != 4:
            raise Exception("Cannot find a 32 bits integer")
    else:
        pass
    return format_32


INT32_FORMAT = _get_int32_format()


def _int32_from_net(data):
    return struct.unpack(INT32_FORMAT, data)[0]


def _int32_to_net(value):
    return struct.pack(INT32_FORMAT, value)
