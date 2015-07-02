#!/usr/bin/env python
import logging
import socket
import ssl
import struct
from BeautifulSoup import BeautifulStoneSoup  # TODO: replace this horrable class. It even case insensitive
import re
from . import commands

logger = logging.getLogger(__name__)


class EPP(object):

    def __init__(self, **kwargs):
        self.config = kwargs
        self.connected = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(2)
        self.socket.connect((self.config['host'], self.config['port']))
        try:
            self.ssl = ssl.wrap_socket(self.socket)
        except socket.error:
            logger.error("ERROR: Could not setup a secure connection. Check whether your IP is allowed to connect to the host.")
            raise
        self.format_32 = self.format_32()
        self.login()

    def __del__(self):
        try:
            self.logout()
            self.socket.close()
        except EPPError:
            """ Will occur when not properly connected """
            pass

    # http://www.bortzmeyer.org/4934.html
    def format_32(self):
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

    def int_from_net(self, data):
        return struct.unpack(self.format_32, data)[0]

    def int_to_net(self, value):
        return struct.pack(self.format_32, value)

    def cmd(self, cmd, silent=False):
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("SIDN request: %s", _mask_sensitive_fields(cmd))
        self.write(cmd)
        raw_response = self.read()
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

    def read(self):
        length = self.ssl.read(4)
        if length:
            i = self.int_from_net(length)-4
            return self.ssl.read(i)

    def write(self, xml):
        epp_as_string = xml
        # +4 for the length field itself (section 4 mandates that)
        # +2 for the CRLF at the end
        length = self.int_to_net(len(epp_as_string) + 4 + 2)
        self.ssl.send(length)
        return self.ssl.send(epp_as_string + "\r\n")

    def login(self):
        # Read greeting
        greeting = self.read()
        soup = BeautifulStoneSoup(greeting)
        svid = soup.find('svid')
        version = soup.find('version')
        logger.info("Connected to %s (v%s)\n", svid.text, version.text)

        # Login
        xml = commands.login % self.config
        return self.cmd(xml, silent=True)

    def logout(self):
        cmd = commands.logout
        return self.cmd(cmd, silent=True)

    def poll(self):
        cmd = commands.poll
        return self.cmd(cmd)


class EPPObject(object):
    def __init__(self, epp):
        self.epp = epp

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __getitem__(self, key):
        try:
            return getattr(self, key)
        except AttributeError:
            pass


class Contact(EPPObject):
    def __init__(self, epp, handle='', **kwargs):
        super(Contact, self).__init__(epp)
        self.handle = handle
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __unicode__(self):
        try:
            self.name != ''
            return "[%(handle)s] %(name)s, %(street)s, %(pc)s %(city)s (%(cc)s)" % self
        except:
            return self.handle

    def available(self):
        cmd = commands.contact.available % self
        res = self.epp.cmd(cmd, silent=True)
        return res.resdata.find('contact:id').get('avail') == 'true'

    def create(self):
        cmd = commands.contact.create(self.__dict__)
        res = self.epp.cmd(cmd).resdata
        return res.find('contact:id').text

    def info(self):
        cmd = commands.contact.info % self
        res = self.epp.cmd(cmd).resdata
        self.roid = res.find('contact:roid').text
        self.status = res.find('contact:status').get('s')
        self.name = res.find('contact:name').text
        try:
            self.street = res.find('contact:street').text
        except AttributeError:
            pass
        self.city = res.find('contact:city').text
        try:
            self.pc = res.find('contact:pc').text
        except AttributeError:
            pass
        self.cc = res.find('contact:cc').text
        self.voice = res.find('contact:voice').text
        self.email = res.find('contact:email').text
        return self

    def update(self):
        cmd = commands.contact.update(self.__dict__)
        return self.epp.cmd(cmd)


class Domain(EPPObject):
    def __init__(self, epp, domain):
        self.domain = domain
        self.epp = epp
        self.roid = ""
        self.status = ""
        #self.ns = Nameserver(epp)

    def __unicode__(self):
        return "[%(domain)s] status: %(status)s, registrant: %(registrant)s, admin: %(admin)s, tech: %(tech)s" % self

    def available(self):
        cmd = commands.available % self.domain
        res = self.epp.cmd(cmd)
        if not res:
            # exception would be more fitting
            return False
        return res.resdata.find('domain:name').get('avail') == 'true'

    def create(self, contacts, ns):
        cmd = commands.create % dict({
            'domain': self.domain,
            'ns': ns[0],
            'registrant': contacts['registrant'],
            'admin': contacts['admin'],
            'tech': contacts['tech'],
        })
        return self.epp.cmd(cmd)

    def delete(self, undo=False):
        if undo:
            cmd = commands.canceldelete % self.domain
        else:
            cmd = commands.delete % self.domain
        return self.epp.cmd(cmd)

    def info(self):
        cmd = commands.info % self.domain
        res = self.epp.cmd(cmd).resdata
        self.roid = res.find('domain:roid').text
        self.status = res.find('domain:status').get('s')
        self.registrant = Contact(self.epp, res.find('domain:registrant').text)
        self.admin = Contact(self.epp, res.find('domain:contact', type='admin').text)
        self.tech = Contact(self.epp, res.find('domain:contact', type='tech').text)
        self.ns = []
        for ns in res.findAll('domain:hostobj'):
            self.ns.append(ns.text)
        fields = ['clid', 'crid', 'crdate', 'exdate']
        for f in fields:
            v = res.find('domain:%s' % f).text
            setattr(self, f, v)
        return self

    def token(self):
        cmd = commands.info % self.domain
        res = self.epp.cmd(cmd)
        return res.resdata.find('domain:pw').text

    def transfer(self, token):
        cmd = commands.transfer % dict({
            'domain': self.domain,
            'token': token,
        })
        return self.epp.cmd(cmd)


class Nameserver(EPPObject):
    def __init__(self, epp, nameserver=False):
        self.nameserver = nameserver
        self.epp = epp

    def __unicode__(self):
        return self.nameserver

    def get_ip(self):
        cmd = commands.nameserver % self.nameserver
        res = self.epp.cmd(cmd)
        return res.resdata.find('host:addr').text


class EPPError(RuntimeError):
    """
    Error response returned by the server.
    """
    def __init__(self, code, message):
        super(EPPError, self).__init__(message)
        self.code = code
        self.message = message


RE_CL_ID = re.compile(r'<clID>[^<]+</clID>')
RE_PW = re.compile(r'<pw>[^<]+</pw>')
def _mask_sensitive_fields(cmd):
    cmd = RE_CL_ID.sub('<clID>***</clID>', cmd)
    cmd = RE_PW.sub('<pw>***</pw>', cmd)
    return cmd
