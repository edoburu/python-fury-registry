import logging
from .utils import python_2_unicode_compatible

logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class Contact(object):
    """
    Contact data object
    """

    def __init__(self, id, roid, status, name, org, street, city, pc, cc, voice, fax, email, crDate, upDate):
        # Some fields are renamed for easier referencing,
        # while the constructor arguments map to the XML field names.
        self.handle = id
        self.roid = roid
        self.status = status
        self.name = name
        self.organisation = org
        self.street = street
        self.city = city
        self.postcode = pc
        self.country_code = cc
        self.phone = voice
        self.fax = fax
        self.email = email
        self.created_date = crDate
        self.updated_date = upDate

    def __repr__(self):
        return '<Contact {0}>'.format(self)

    def __str__(self):
        return "[{handle}] {name}, {street}, {postcode} {city} ({country_code})".format(
            handle=self.handle,
            name=self.name,
            street=self.street,
            postcode=self.postcode,
            city=self.city,
            country_code=self.country_code
        )


@python_2_unicode_compatible
class Domain(object):
    """
    Domain data object
    """

    def __init__(self, name, roid, status, registrant, admin, tech, ns, clID, crID, crDate, upDate, exDate, pw):
        # This may look really stupid, yet it makes tests and self-documentation and code-completion much easier.
        # Before all parameters were magically assigned, making it really hard to use it from other code.
        #
        # Some fields are renamed for easier referencing,
        # while the constructor arguments map to the XML field names.
        self.name = name
        self.roid = roid
        self.status = status
        self.registrant = registrant
        self.admin = admin
        self.tech = tech
        self.ns = ns
        self.cl_id = clID
        self.cr_id = crID
        self.created_date = crDate
        self.updated_date = upDate
        self.expire_date = exDate
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
