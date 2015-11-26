import logging
from .utils import python_2_unicode_compatible

logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class Contact(object):
    """
    Contact data object
    """

    def __init__(self, handle, roid, status, name, org, street, city, pc, cc, voice, fax, email, created_date, updated_date):
        self.handle = handle
        self.roid = roid
        self.status = status
        self.name = name
        self.org = org
        self.street = street
        self.city = city
        self.pc = pc
        self.cc = cc
        self.voice = voice
        self.fax = fax
        self.email = email
        self.created_date = created_date
        self.updated_date = updated_date

    def __repr__(self):
        return '<Contact {0}>'.format(self)

    def __str__(self):
        return "[{handle}] {name}, {street}, {pc} {city} ({cc})".format(
            handle=self.handle,
            name=self.name,
            street=self.street,
            pc=self.pc,
            city=self.city,
            cc=self.cc
        )

    @property
    def postcode(self):
        return self.pc

    @property
    def country_code(self):
        return self.cc

    @property
    def telephone(self):
        return self.voice


@python_2_unicode_compatible
class Domain(object):
    """
    Domain data object
    """

    def __init__(self, name, roid, status, registrant, admin, tech, ns, cl_id, cr_id, created_date, updated_date, expire_date, pw):
        # This may look really stupid, yet it makes tests and self-documentation and code-completion much easier.
        # Before all parameters were magically assigned, making it really hard to use it from other code.
        self.name = name
        self.roid = roid
        self.status = status
        self.registrant = registrant
        self.admin = admin
        self.tech = tech
        self.ns = ns
        self.cl_id = cl_id
        self.cr_id = cr_id
        self.created_date = created_date
        self.updated_date = updated_date
        self.expire_date = expire_date
        self.pw = pw

        # Can be assigned by handler
        self._epp = None

    def __repr__(self):
        return '<Domain {0}>'.format(self)

    def __str__(self):
        return "[{domain}] status: {status}, registrant: {registrant}, admin: {admin}, tech: {tech}".format(
            domain=self.name,
            status=self.status,
            registrant=self.registrant,
            admin=self.admin,
            tech=self.tech
        )

    @property
    def token(self):
        return self.pw

    @property
    def registrant_contact(self):
        return self._epp.contacts.get(self.registrant)

    @property
    def admin_contact(self):
        return self._epp.contacts.get(self.admin)

    @property
    def tech_contact(self):
        return self._epp.contacts.get(self.tech)


@python_2_unicode_compatible
class Host(object):
    """
    Host data object (e.g. for nameservers)
    """

    def __init__(self, name, addr):
        self.name = name
        self.addr = addr

    def __repr__(self):
        return '<Host {0}>'.format(self)

    def __str__(self):
        return self.name
