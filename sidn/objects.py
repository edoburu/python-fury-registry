import logging
from . import commands

logger = logging.getLogger(__name__)


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
        fields = self.__dict__.copy()
        del fields['epp']
        cmd = commands.contact.create(fields)
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
        fields = self.__dict__.copy()
        del fields['epp']

        cmd = commands.contact.update(fields)
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
            return False
        else:
            status = res.resdata.find('domain:name').get('avail')
            return status in ('1', 'true')

    def create(self, contacts, ns):
        cmd = commands.create % {
            'domain': self.domain,
            'ns': ns[0],
            'registrant': contacts['registrant'],
            'admin': contacts['admin'],
            'tech': contacts['tech'],
        }
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
        cmd = commands.transfer % {
            'domain': self.domain,
            'token': token,
        }
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
