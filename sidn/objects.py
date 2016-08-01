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
    # Status values
    CLIENT_DELETE_PROHIBITED = "clientDeleteProhibited"
    CLIENT_HOLD = "clientHold"
    CLIENT_RENEW_PROHIBITED = "clientRenewProhibited"
    CLIENT_TRANSFER_PROHIBITED = "clientTransferProhibited"
    CLIENT_UPDATE_PROHIBITED = "clientUpdateProhibited"
    INACTIVE = "inactive"
    OK = "ok"
    PENDING_CREATE = "pendingCreate"
    PENDING_DELETE = "pendingDelete"
    PENDING_RENEW = "pendingRenew"
    PENDING_TRANSFER = "pendingTransfer"
    PENDING_UPDATE = "pendingUpdate"
    SERVER_DELETE_PROHIBITED = "serverDeleteProhibited"
    SERVER_HOLD = "serverHold"
    SERVER_RENEW_PROHIBITED = "serverRenewProhibited"
    SERVER_TRANSFER_PROHIBITED = "serverTransferProhibited"
    SERVER_UPDATE_PROHIBITED = "serverUpdateProhibited"

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

    def update(self, registrant=None, admin=None, tech=None, ns=None):
        """
        Update all domain settings at once.
        # TODO: Add dnssec fields here as well.
        """
        kwargs = {}

        if registrant:
            kwargs['registrant'] = registrant

        if admin and admin != self.admin:
            kwargs['remove_admin'] = self.admin
            kwargs['add_admin'] = admin

        if tech and tech != self.tech:
            kwargs['remove_tech'] = self.tech
            kwargs['add_tech'] = tech

        if ns and set(ns) != set(self.ns):
            current = set(self.ns)
            new = set(ns)
            kwargs['remove_ns'] = sorted(current - new)
            kwargs['add_ns'] = sorted(new - current)

        return self._epp.domains.update(self.name, **kwargs)

    def update_registrant(self, new_handle):
        # This could also be done by property assignment,
        # but instead it's a bit more explicit that something big happens due to an assignment.
        if self.registrant == new_handle:
            return None
        else:
            return self._epp.domains.update(registrant=new_handle)

    def update_admin(self, new_handle):
        """
        Replace the admin handle for the domain (DRS5 only allows one admin handle)
        """
        if new_handle == self.admin:
            return None
        else:
            response = self._epp.domains.update(remove_techs=(self.admin,), add_techs=(new_handle,))
            self.admin = new_handle
            return response

    def update_tech(self, new_handle):
        """
        Replace the tech handle for the domain.
        """
        if new_handle == self.tech:
            return None
        else:
            response = self._epp.domains.update(remove_techs=(self.tech,), add_techs=(new_handle,))
            self.tech = new_handle
            return response

    def update_nameservers(self, ns):
        """
        Assign new nameservers to the domain
        """
        current = set(self.ns)
        new = set(ns)
        response = self._epp.domains.update(
            name=self.name,
            remove_ns=sorted(current - new),
            add_ns=sorted(new - current)
        )
        self.ns = ns
        return response

    def renew(self, period, period_unit='y'):
        """
        Renew the registration period of the domain.

        :param period: integer, the number of months or years depending on the ``period_unit``.
        :type period: int
        :param period_unit: ``y`` (years) or ``m`` (months)
        """
        return self._epp.domains.renew(expiration_date=self.expire_date, period=period, period_unit=period_unit)


class DomainExt(object):
    """
    Domain extension information by SIDN
    """

@python_2_unicode_compatible
class DSKey(object):
    """
    Delegation Signer key

    SIDN doesn't use the ``dsData`` fields.
    It only reads the ``keyData`` field.
    """

    def __init__(self, keyTag, alg, digestType, digest, keyData=()):
        """
        :type keyTag: int
        :type alg: int
        :param digestType: See https://tools.ietf.org/html/rfc4034#appendix-A.2
        :type digestType: int
        :type digest: str
        :type keyData: Tuple[KeyData]
        """
        self.keyTag = keyTag  # unsignedShort
        self.alg = alg  # unsignedByte
        self.digestType = digestType  # unsignedByte
        self.digest = digest  # hexBinary
        self.keyData = keyData  # secDNS:keyDataType

    def __repr__(self):
        return '<DSKey {0}>'.format(self)

    def __str__(self):
        return self.digest


@python_2_unicode_compatible
class KeyData(object):
    """
    DNSSec client key data
    """
    PROTOCOL3 = 3

    #: DSA/SHA-1
    ALG_DSA = 3
    #: Elliptic Curve
    ALG_ECC = 4
    #: RSA/SHA-1
    ALG_SHA1 = 5
    #: RSA/SHA-256
    ALG_SHA256 = 8

    #: Zone signing key
    FLAG_ZSK = 256
    #: Key signing key
    FLAG_KSK = 257

    def __init__(self, flags, protocol, alg, pubKey):
        """
        :param flags: Values 256 (ZSK) en 257 (KSK) are allowed.
        :type flags: int
        :param protocol: Fixed value 3, see
        :type protocol: int
        :param alg: See http://www.iana.org/assignments/dns-sec-alg-numbers/dns-sec-alg-numbers.xhtml
        :type alg: int
        :param pubKey: Base64 encoded public key
        :type pubKey: str
        """
        # https://tools.ietf.org/html/rfc4034#section-2.1.1
        self.flags = flags  # unsignedShort
        self.protocol = protocol  # unsignedByte
        self.alg = alg  # unsignedByte
        self.pubKey = pubKey  # secDNS:keyType

    def __repr__(self):
        return '<KeyData: {0}>'.format(self)

    def __str__(self):
        return " ".join(map(str, (self.flags, self.protocol, self.alg, self.pubKey)))


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


class TransferStatus(object):
    """
    EPP Transfer status response object
    """

    def __init__(self, name, trStatus, reID, reDate, acID, acDate, exDate=None):
        # Some fields are renamed for easier referencing,
        # while the constructor arguments map to the XML field names.
        self.name = name
        self.status = trStatus
        self.request_id = reID
        self.request_date = reDate
        self.act_id = acID
        self.act_date = acDate
        self.expire_date = exDate

    def __repr__(self):
        return '<TransferStatus {0}: {1}>'.format(self.name, self.status)

    def __str__(self):
        return self.name
