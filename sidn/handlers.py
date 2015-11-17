"""
All specialized commands are performed by these handlers.
"""
from sidn.constants import EPP_DATA_MGMT_POLICY, SIDN_EXT_HANDLE_NOT_ASSOCIATED
from . import commands
from . import objects
import dateutil.parser

NS = {
    # Possible namespaces in the response
    # See greeting message for all possible supported extensions
    'epp': 'urn:ietf:params:xml:ns:epp-1.0',
    'contact': 'urn:ietf:params:xml:ns:contact-1.0',
    'domain': 'urn:ietf:params:xml:ns:domain-1.0',
    'host': 'urn:ietf:params:xml:ns:host-1.0',
    'sidn-ext-epp': 'http://rxsd.domain-registry.nl/sidn-ext-epp-1.0',
}



class BaseHandler(object):
    def __init__(self, epp):
        """
        :type epp: sidn.client.EPP
        """
        self.epp = epp

    def _build_command(self, command, contents, transaction_id=None):
        """
        Build a generic command
        :param command: The command to send, e.g. ``create``, ``info``, ``check``, ``delete``.
        :param contents: The XML contents of the command
        :param transaction_id: Optional client transaction ID, to recognize server responses.
        """
        return commands.epp.generic.format(
            command=command,
            contents=contents,
            clTRID=transaction_id or 'unused',
        )


def _get_xml_text(node, name):
    """
    :type node: xml.etree.ElementTree.Element
    """
    if node is None:
        return None
    # Handling of optional fields
    node = node.find(name, NS)
    return node.text if node is not None else None


class DomainHandler(BaseHandler):
    """
    Actions for domains.
    """

    def get(self, domain_name):
        """
        Request the info of a domain
        """
        cmd = self._build_command('info', commands.domain.info_part(name=domain_name))
        resData = self.epp.cmd(cmd).resData
        domain = self._parse_info(resData)
        domain.epp = self.epp  # Sneak it in
        return domain

    @staticmethod
    def _parse_info(resData):
        infData = resData.find('domain:infData', NS)
        authInfo = infData.find('domain:authInfo', NS)

        ns = []
        for hostobj in infData.find('domain:ns', NS).findall('domain:hostObj', NS):
            ns.append(hostobj.text)

        return objects.Domain(
            name=_get_xml_text(infData, 'domain:name'),
            roid=_get_xml_text(infData, 'domain:roid'),  # Repository object identifier (assigned on creation)
            status=infData.find('domain:status', NS).attrib['s'],
            registrant=_get_xml_text(infData, 'domain:registrant'),
            admin=_get_xml_text(infData, "domain:contact[@type='admin']"),
            tech=_get_xml_text(infData, "domain:contact[@type='tech']"),
            ns=ns,
            cl_id=_get_xml_text(infData, 'domain:clID'),  # current registrar
            cr_id=_get_xml_text(infData, 'domain:crID'),  # initial registrar
            created_date=_parse_iso_date(_get_xml_text(infData, 'domain:crDate')),
            modified_date=_parse_iso_date(_get_xml_text(infData, 'domain:upDate')),
            expire_date=_parse_iso_date(_get_xml_text(infData, 'domain:exDate')),
            pw=_get_xml_text(authInfo, 'domain:pw'),
        )

    def is_available(self, domain_name):
        """
        Check if a domain is available.
        """
        cmd = self._build_command('check', commands.domain.check_part(name=domain_name))
        res = self.epp.cmd(cmd)
        status = res.resData.find('domain:chkData/domain:cd/domain:name', NS).attrib['avail']
        return status in ('1', 'true')

    def create(self, name, registrant, contacts, ns):
        """
        Create a domain

        :param domain_name: Domain name to register.
        :param registrant: Registrant contact handle
        :param contacts: Contact handles (only supports admin and tech)
        :type contacts: dict
        :param ns: List of nameserver host names
        :type ns: list
        """
        cmd = self._build_command('create', commands.domain.create_part(
            name=name,
            registrant=registrant,
            admin=contacts['admin'],  # Only supported options by DRS5
            tech=contacts['tech'],
            ns=ns
        ))
        return self.epp.cmd(cmd)

    def delete(self, name):
        """
        Delete a domain
        """
        cmd = self._build_command('delete', commands.domain.delete_part(name))
        return self.epp.cmd(cmd)

    def cancel_delete(self, name):
        """
        Cancel deletion
        """
        cmd = commands.domain.cancel_delete(name)
        return self.epp.cmd(cmd)

    def transfer(self, name, token):
        """
        Initiate the domain transfer.
        """
        cmd = commands.domain.transfer(name, token)
        return self.epp.cmd(cmd)

    def get_transfer_status(self, name):
        """
        Get status of current domain transfer.
        """
        cmd = commands.domain.transfer_status(name)
        return self.epp.cmd(cmd)


class ContactHandler(BaseHandler):
    """
    Actions for contacts
    """

    def is_available(self, handle):
        """
        Check if a given handle is available.
        """
        cmd = self._build_command('check', commands.contact.check_part(handle))

        from sidn.client import EPPError
        try:
            res = self.epp.cmd(cmd)
        except EPPError as e:
            if e.code == EPP_DATA_MGMT_POLICY and e.ext_code == SIDN_EXT_HANDLE_NOT_ASSOCIATED:
                return False
            raise
        return self._parse_avail(res.resData)

    @staticmethod
    def _parse_avail(resData):
        status = resData.find('contact:chkData/contact:cd/contact:id', NS).attrib['avail']
        return status in ('1', 'true')

    def create(self, name, street, city, pc, cc, org=None, voice=None, fax=None, email=None, legalForm=None, legalFormRegNo=None):
        """
        Create a contact.

        :returns: The contact handle.
        """
        cmd = commands.contact.create(
            handle='',
            name=name,
            org=org,  # department in DRS5
            street=street,
            city=city,
            pc=pc,  # postcode
            cc=cc,  # country code
            voice=voice,
            fax=fax,
            email=email,
            legalForm=legalForm,
            legalFormRegNo=legalFormRegNo,
        )
        res = self.epp.cmd(cmd).resData
        return res.find('contact:id').text

    def update(self, handle, name, street, city, pc, cc, org=None, cr_id=None, voice=None, fax=None, email=None, legalForm=None, legalFormRegNo=None):
        """
        Update an existing contact
        """
        cmd = self._build_command('update', commands.contact.update_part(
            handle=handle,
            name=name,
            org=org,  # department in DRS5
            street=street,
            city=city,
            pc=pc,
            cc=cc,
            voice=voice,
            fax=fax,
            email=email,
            legalForm=legalForm,
            legalFormRegNo=legalFormRegNo,
        ))
        res = self.epp.cmd(cmd).resData
        return res.find('contact:id').text

    def get(self, handle):
        """
        Fetch contact data
        """
        cmd = self._build_command('info', commands.contact.info_part(handle))
        resdata = self.epp.cmd(cmd).resData
        return self._parse_info(resdata)

    @staticmethod
    def _parse_info(resData):
        infData = resData.find('contact:infData', NS)
        loc = infData.find("contact:postalInfo[@type='loc']", NS)
        addr = loc.find('contact:addr', NS)

        return objects.Contact(
            handle=_get_xml_text(infData, 'contact:id'),
            roid=_get_xml_text(infData, 'contact:roid'),
            status=infData.find('contact:status', NS).attrib['s'],
            name=_get_xml_text(loc, 'contact:name'),
            org=_get_xml_text(loc, 'contact:org'),
            street= _get_xml_text(addr, 'contact:street'),
            city=_get_xml_text(addr, 'contact:city'),
            pc=_get_xml_text(addr, 'contact:pc'),
            cc=_get_xml_text(addr, 'contact:cc'),
            voice=_get_xml_text(infData, 'contact:voice'),
            fax=_get_xml_text(infData, 'contact:fax'),
            email=_get_xml_text(infData, 'contact:email'),
            created_date=_parse_iso_date(_get_xml_text(infData, 'contact:crDate')),
            modified_date=_parse_iso_date(_get_xml_text(infData, 'contact:upDate')),
        )

    def delete(self, name):
        """
        Delete a contact
        """
        cmd = self._build_command('delete', commands.contact.delete_part(name))
        return self.epp.cmd(cmd)


class HostHandler(BaseHandler):
    """
    Handler for host data
    """

    def get(self, nameserver):
        cmd = commands.host.info_part.format(name=nameserver)
        resdata = self.epp.cmd(cmd).resData
        return objects.Host(
            name=nameserver,
            addr=resdata.find('host:addr', NS).text
        )


def _parse_iso_date(date):
    # Dates like: 1995-12-10T23:00:00.000Z
    return dateutil.parser.parse(date)
