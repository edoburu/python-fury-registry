import logging

import idna
from sidn.constants import XMLNS
from sidn.utils import get_node_date, get_node_text, python_2_unicode_compatible

from .base import ParsedObject
from .secdns import DNSSec

if 0:
    from sidn.client import EPP  # For PyCharm type checking


logger = logging.getLogger(__name__)


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
        infData = resdata.find('domain:infData', XMLNS)
        authInfo = infData.find('domain:authInfo', XMLNS)

        ns = []
        for hostobj in infData.find('domain:ns', XMLNS).findall('domain:hostObj', XMLNS):
            ns.append(hostobj.text)

        fields = dict(
            name=idna.decode(get_node_text(infData, 'domain:name')),
            roid=get_node_text(infData, 'domain:roid'),  # Repository object identifier (assigned on creation)
            status=infData.find('domain:status', XMLNS).attrib['s'],
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

        # Parse extension fields
        if extension is not None:
            dnssec = extension.find('secDNS:infData', XMLNS)

            if dnssec is not None:
                fields['dnssec'] = DNSSec.from_xml(dnssec)

        return fields

    def __init__(self, name, roid, status, registrant, admin, tech, ns, clID, crID, crDate, upDate, exDate, pw, dnssec=None):
        """
        :type dnssec: sidn.objects.DNSSec
        """
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

        # DNSSec extension field
        self.dnssec = dnssec

        # Can be assigned by handler
        self._epp = None  # type: EPP

    def __repr__(self):
        return '<{0} {1}>'.format(self.__class__.__name__, self)

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
            kwargs['remove_admins'] = (self.admin,)
            kwargs['add_admins'] = (admin,)

        if tech and tech != self.tech:
            kwargs['remove_techs'] = (self.tech,)
            kwargs['add_techs'] = (tech,)

        if ns:
            current = set(self.ns)
            new = set(ns)
            if current != new:
                kwargs['remove_ns'] = sorted(current - new)
                kwargs['add_ns'] = sorted(new - current)

        if keydatas:
            add = []
            remove = []
            if not self.dnssec:
                # Add all.
                kwargs['remove_all_keys'] = True
                kwargs['add_keydatas'] = keydatas
                kwargs['dnssec_urgent'] = dnssec_urgent
            else:
                # Try a partial add, only remove old keys.
                for keydata in keydatas:
                    # Not in existing!
                    if keydata not in self.dnssec:
                        add.append(keydatas)
                for keydata in self.dnssec.keydatas:
                    if keydata not in keydatas:
                        remove.append(keydata)

                if add or remove:
                    kwargs['remove_keydatas'] = remove
                    kwargs['add_keydatas'] = add
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
            return self._epp.domains.update(self.name, registrant=new_handle)

    def update_admin(self, new_handle):
        """
        Replace the admin handle for the domain (DRS5 only allows one admin handle)
        """
        if new_handle == self.admin:
            return None
        else:
            response = self._epp.domains.update(self.name, remove_techs=(self.admin,), add_techs=(new_handle,))
            self.admin = new_handle
            return response

    def update_tech(self, new_handle):
        """
        Replace the tech handle for the domain.
        """
        if new_handle == self.tech:
            return None
        else:
            response = self._epp.domains.update(self.name, remove_techs=(self.tech,), add_techs=(new_handle,))
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
        return self._epp.domains.renew(self.name, expiration_date=self.expire_date, period=period, period_unit=period_unit)


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
            sidn_ext = extension.find('sidn-ext-epp:ext/sidn-ext-epp:infData/sidn-ext-epp:domain', XMLNS)

            if sidn_ext is not None:
                fields.update(dict(
                    optOut=get_node_text(sidn_ext, 'sidn-ext-epp:optOut') == 'true',
                    limited=get_node_text(sidn_ext, 'sidn-ext-epp:limited') == 'true',
                    period=int(get_node_text(sidn_ext, 'sidn-ext-epp:period', 0)) or None,
                ))

        return fields

    def __init__(self, name, roid, status, registrant, admin, tech, ns, clID, crID, crDate, upDate, exDate, pw,
                 dnssec=None, optOut=None, limited=None, period=None):
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
            pw=pw,
            dnssec=dnssec
        )

        # SIDN extension fields
        self.opt_out = optOut
        self.limited = limited
        self.period = period


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
