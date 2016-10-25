import logging
import idna
from itertools import chain

from sidn.constants import NS

from .utils import python_2_unicode_compatible, get_node_text, get_node_date

logger = logging.getLogger(__name__)


class ParsedObject(object):
    """
    Base interface to parse XML noptes.
    """

    @classmethod
    def from_xml(cls, node, extension=None):
        return cls(**cls.parse_xml_fields(node, extension=extension))

    @classmethod
    def parse_xml_fields(cls, node, extension=None):
        raise NotImplementedError("missing parse_xml_fields")


@python_2_unicode_compatible
class EppContact(ParsedObject):
    """
    Contact data object
    """

    @classmethod
    def parse_xml_fields(cls, resData, extension=None):
        infData = resData.find('contact:infData', NS)
        postalInfo = infData.find("contact:postalInfo[@type='loc']", NS)
        addr = postalInfo.find('contact:addr', NS)

        return dict(
            id=get_node_text(infData, 'contact:id'),
            roid=get_node_text(infData, 'contact:roid'),
            status=infData.find('contact:status', NS).attrib['s'],
            name=get_node_text(postalInfo, 'contact:name'),
            org=get_node_text(postalInfo, 'contact:org'),
            street= get_node_text(addr, 'contact:street'),
            city=get_node_text(addr, 'contact:city'),
            pc=get_node_text(addr, 'contact:pc'),
            cc=get_node_text(addr, 'contact:cc'),
            voice=get_node_text(infData, 'contact:voice'),
            fax=get_node_text(infData, 'contact:fax'),
            email=get_node_text(infData, 'contact:email'),
            crDate=get_node_date(infData, 'contact:crDate'),
            upDate=get_node_date(infData, 'contact:upDate'),
        )

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
class EppDomain(ParsedObject):
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

    @classmethod
    def parse_xml_fields(cls, resdata, extension=None):
        infData = resdata.find('domain:infData', NS)
        authInfo = resdata.find('domain:authInfo', NS)

        ns = []
        for hostobj in infData.find('domain:ns', NS).findall('domain:hostObj', NS):
            ns.append(hostobj.text)

        return dict(
            name=idna.decode(get_node_text(infData, 'domain:name')),
            roid=get_node_text(infData, 'domain:roid'),  # Repository object identifier (assigned on creation)
            status=infData.find('domain:status', NS).attrib['s'],
            registrant=get_node_text(infData, 'domain:registrant'),
            admin=get_node_text(infData, "domain:contact[@type='admin']"),
            tech=get_node_text(infData, "domain:contact[@type='tech']"),
            ns=ns,
            clID=get_node_text(infData, 'domain:clID'),  # current registrar
            crID=get_node_text(infData, 'domain:crID'),  # initial registrar
            crDate=get_node_date(infData, 'domain:crDate'),
            upDate=get_node_date(infData, 'domain:upDate'),
            exDate=get_node_date(infData, 'domain:exDate'),
            pw=get_node_text(authInfo, 'domain:pw'),
        )

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
        return '<{0} {0}>'.format(self.__class__.__name__, self)

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

    def update(self, registrant=None, admin=None, tech=None, ns=None, keydatas=None, dnssec_urgent=False):
        """
        Update all domain settings at once.
        This operation only changes the fields which need to change.
        Returns ``None`` when no settings had to be changed.
        """
        kwargs = {}

        if registrant:
            kwargs['registrant'] = registrant

        if admin and admin != self.admin:
            kwargs['remove_admins'] = self.admin
            kwargs['add_admins'] = admin

        if tech and tech != self.tech:
            kwargs['remove_techs'] = self.tech
            kwargs['add_techs'] = tech

        if ns:
            current = set(self.ns)
            new = set(ns)
            if set(ns) != set(self.ns):
                kwargs['remove_ns'] = sorted(current - new)
                kwargs['add_ns'] = sorted(new - current)

        if keydatas:
            # The remove all / add everything is a quick implementation choice.
            # TODO: only remove the DNSSec data that have to be removed.
            kwargs['remove_all_keys'] = True
            kwargs['add_keydatas'] = keydatas
            kwargs['dnssec_urgent'] = dnssec_urgent

        if not kwargs:
            return None

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


class SidnDomain(EppDomain):
    """
    Domain data object with SIDN extension fields
    """
    @classmethod
    def parse_xml_fields(cls, resdata, extension=None):
        # Base EPP base fields
        fields = super(SidnDomain, cls).parse_xml_fields(resdata, extension)

        # Parse extension fields
        if extension is not None:
            sidn_ext = extension.find('sidn-ext-epp:ext/sidn-ext-epp:infData/sidn-ext-epp:domain', NS)
            dnssec = extension.find('secDNS:infData', NS)

            if sidn_ext is not None:
                fields.update(dict(
                    optOut = get_node_text(sidn_ext, 'sidn-ext-epp:optOut') == 'true',
                    limited = get_node_text(sidn_ext, 'sidn-ext-epp:limited') == 'true',
                    period = int(get_node_text(sidn_ext, 'sidn-ext-epp:period', 0)) or None,
                ))

            if dnssec is not None:
                fields['dnssec'] = DNSSec.from_xml(dnssec)

        return fields

    def __init__(self, name, roid, status, registrant, admin, tech, ns, clID, crID, crDate, upDate, exDate, pw,
                 optOut=None, limited=None, period=None, dnssec=None):
        super(SidnDomain, self).__init__(
            name=name,
            roid=roid,
            status=status,
            registrant=registrant,
            admin=admin,
            tech=tech,
            ns=ns,
            clID=clID,
            crID=crID,
            crDate=crDate,
            upDate=upDate,
            exDate=exDate,
            pw=pw
        )

        # SIDN extension fields
        self.opt_out = optOut
        self.limited = limited
        self.period = period

        # DNSSec extension field
        self.dnssec = dnssec


class DNSSec(ParsedObject):
    """
    DNSSec info
    """

    @classmethod
    def parse_xml_fields(cls, node, extension=None):
        keydatas = []
        dskeys = []
        for node in node.findall('secDNS:keyData', NS):
            keydatas.append(KeyData.from_xml(node))
        for node in node.findall('secDNS:dsData', NS):
            dskeys.append(DSKey.from_xml(node))
        return dict(
            keydatas=keydatas,
            dskeys=dskeys
        )

    def __init__(self, keydatas=(), dskeys=()):
        self.keydatas = keydatas
        self.dskeys = dskeys

    def __repr__(self):
        return '<DNSSec[{0}]>'.format(", ".join(repr(x) for x in chain(self.dskeys, self.keydatas)))


@python_2_unicode_compatible
class DSKey(ParsedObject):
    """
    Delegation Signer key

    SIDN doesn't use the ``dsData`` fields.
    It only reads the ``keyData`` field.
    """

    @classmethod
    def parse_xml_fields(cls, node, extension=None):
        return dict(
            keyTag=get_node_text(node, 'secDNS:keyTag'),
            alg=int(get_node_text(node, 'secDNS:alg')),
            digestType=int(get_node_text(node, 'secDNS:digestType')),
            digest=get_node_text(node, 'secDNS:digest'),
            keyData=KeyData.from_xml(node.find('secDNS:keyData', NS)),
        )

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
class KeyData(ParsedObject):
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

    @classmethod
    def parse_xml_fields(cls, node, extension=None):
        return dict(
            flags=int(get_node_text(node, 'secDNS:flags')),
            protocol=int(get_node_text(node, 'secDNS:protocol')),
            alg=int(get_node_text(node, 'secDNS:alg')),
            pubKey=get_node_text(node, 'secDNS:pubKey'),
        )

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
class EppHost(object):
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


class TransferStatus(ParsedObject):
    """
    EPP Transfer status response object
    """
    CLIENT_APPROVED = "clientApproved"
    CLIENT_CANCELLED = "clientCancelled"
    CLIENT_REJECTED = "clientRejected"
    PENDING = "pending"
    SERVER_APPROVED = "serverApproved"  # Transfer OK
    SERVER_CANCELLED = "serverCancelled'"

    @classmethod
    def parse_xml_fields(cls, trnData, extension=None):
        return dict(
            name=get_node_text(trnData, 'domain:name'),
            trStatus=get_node_text(trnData, 'domain:trStatus'),
            reID=get_node_text(trnData, 'domain:reID'),  # requested client
            reDate=get_node_date(trnData, 'domain:reDate'),
            acID=get_node_text(trnData, 'domain:acID'),  # acting client
            acDate=get_node_date(trnData, 'domain:acDate'),
            exDate=get_node_date(trnData, 'domain:exDate'),
        )

    def __init__(self, name, trStatus, reID, reDate, acID, acDate, exDate=None):
        """
        :param name: the fully qualified name of the domain object.
        :param trStatus: the state of the most recent transfer request.
        :param reID: the identifier of the client that requested the object transfer.
        :param reDate: date and time that the transfer was requested.
        :param acID: the identifier of the client that SHOULD act upon a PENDING transfer request.
                     For all other status types, the value identifies the client that took the indicated action.
        :param acDate: the date and time of a required or completed response.
                       For a PENDING request, the value identifies the date and time by which a response is required
                       before an automated response action will be taken by the server.
                       For all other status types, the value identifies the date and time when the request was completed.
        :param exDate: optional, the end of the domain object's validity period if the transfer command
                       caused or causes a change in the validity period.

        To check whether the transfer is moved away, or is incoming, check the :attr:`request_id` field.
        Note that a query for the transferstatus may also return an old status from a year ago,
        so also check the :attr:`act_date`.
        """
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
        if self.is_pending:
            return '<TransferStatus {0}: {1} by {2} till {3}>'.format(self.name, self.status, self.act_id, self.act_date)
        else:
            return '<TransferStatus {0}: {1} by {2} on {3}>'.format(self.name, self.status, self.act_id, self.act_date)

    def __str__(self):
        return self.name

    @property
    def is_approved(self):
        return self.status in (self.CLIENT_APPROVED, self.SERVER_APPROVED)

    @property
    def is_declined(self):
        return self.status in (self.CLIENT_CANCELLED, self.SERVER_CANCELLED, self.CLIENT_REJECTED)

    @property
    def is_pending(self):
        return self.status == self.PENDING
