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
    'epp': 'urn:ietf:params:xml:ns:epp-1.0',  # Base EPP; https://tools.ietf.org/html/rfc5730
    'domain': 'urn:ietf:params:xml:ns:domain-1.0',  # Domain name mapping; https://tools.ietf.org/html/rfc5731
    'host': 'urn:ietf:params:xml:ns:host-1.0',  # Host mapping; https://tools.ietf.org/html/rfc5732
    'contact': 'urn:ietf:params:xml:ns:contact-1.0',  # Contact mapping; https://tools.ietf.org/html/rfc5733
    'secDNS': 'urn:ietf:params:xml:ns:secDNS-1.1',  # DNSSec; https://tools.ietf.org/html/rfc5910
    'sidn-ext-epp': 'http://rxsd.domain-registry.nl/sidn-ext-epp-1.0',  # SIDN specific bits
}


class BaseHandler(object):
    def __init__(self, epp):
        """
        :type epp: sidn.client.EPP
        """
        self.epp = epp

    def _build_command(self, command_name, command_xml, command_extensions=(), op=None, transaction_id=None, epp_extensions=()):
        """
        Build a generic command
        """
        return commands.epp.build_command(
            command_name=command_name,
            command_xml=command_xml,
            command_extensions=command_extensions,
            op=op,
            clTRID=transaction_id,
            epp_extensions=epp_extensions
        )


class DomainHandler(BaseHandler):
    """
    Actions for domains.
    """

    def get(self, domain_name):
        """
        Request the info of a domain
        """
        # https://tools.ietf.org/html/rfc5730#section-2.9.2.2
        xml = self._build_command('info', commands.domain.info_part(name=domain_name))
        resData = self.epp.cmd(xml).resData
        domain = self._parse_info(resData)
        domain._epp = self.epp  # Sneak it in
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
            clID=_get_xml_text(infData, 'domain:clID'),  # current registrar
            crID=_get_xml_text(infData, 'domain:crID'),  # initial registrar
            crDate=_get_xml_date(infData, 'domain:crDate'),
            upDate=_get_xml_date(infData, 'domain:upDate'),
            exDate=_get_xml_date(infData, 'domain:exDate'),
            pw=_get_xml_text(authInfo, 'domain:pw'),
        )

    def is_available(self, domain_name):
        """
        Check if a domain is available.
        """
        # https://tools.ietf.org/html/rfc5730#section-2.9.2.1
        xml = self._build_command('check', commands.domain.check_part(name=domain_name))
        res = self.epp.cmd(xml)
        return self._parse_avail(res.resData)

    @staticmethod
    def _parse_avail(resData):
        # Note that the domain:cd element may be repeated
        # The element may also contain a <domain:reason> element.
        status = resData.find('domain:chkData/domain:cd/domain:name', NS).attrib['avail']
        return status in ('1', 'true')

    def create(self, name, registrant, contacts, ns, dskeys=(), keyData=()):
        """
        Create a domain

        :param domain_name: Domain name to register.
        :param registrant: Registrant contact handle
        :param contacts: Contact handles (only supports admin and tech)
        :type contacts: dict
        :param ns: List of nameserver host names
        :type ns: list
        :param dskeys: DNSSec keys (values not read by SIDN, only keyData field is used.)
        :type dskeys: Tuple[sidn.objects.DSKey]
        :param keyData: DNSSec keydata, as alternative for ``keys``, max 4 with SIDN.
        :type keyData: Tuple[sidn.objects.KeyData]
        """
        # https://tools.ietf.org/html/rfc5730#section-2.9.3.1
        # https://tools.ietf.org/html/rfc5731#section-3.2.1
        xml = commands.domain.create_part(
            name=name,
            registrant=registrant,
            admin=contacts['admin'],  # Only supported options by DRS5
            tech=contacts['tech'],
            ns=ns
        )

        if dskeys or keyData:
            # SIDN only looks at the keydata fields.
            # https://tools.ietf.org/html/rfc5910#section-5.2.1
            extensions = (commands.secdns.create(dskeys=dskeys, keyData=keyData),)
        else:
            extensions = ()

        xml = self._build_command('create', xml, extensions=extensions)
        return self.epp.cmd(xml)

    def update_keys(self, name, remove_all=False, remove_keydatas=(), add_keydatas=(), urgent=False):
        """
        Update the DNSSec keys in a domain
        """
        # SIDN only looks at the keydata fields.
        # https://tools.ietf.org/html/rfc5910#section-5.2.5
        secdns_ext = commands.secdns.update(
            remove_all=remove_all,
            remove_keydatas=remove_keydatas,
            add_keydatas=add_keydatas,
            urgent=urgent
        )

        xml = self._build_command('update', commands.domain.update_part(name), command_extensions=(secdns_ext,))
        return self.epp.cmd(xml)

    def delete(self, name):
        """
        Delete a domain
        """
        # https://tools.ietf.org/html/rfc5730#section-2.9.3.2
        # https://tools.ietf.org/html/rfc5731#section-3.2.2
        xml = self._build_command('delete', commands.domain.delete_part(name))
        return self.epp.cmd(xml)

    def update_keys(self, name, remove_all=False, remove_keydatas=(), add_keydatas=(), urgent=False):
        """
        Update the DNSSec keys in a domain
        """
        # SIDN only looks at the keydata fields.
        # https://tools.ietf.org/html/rfc5910#section-5.2.5
        secdns_ext = commands.secdns.update(
            remove_all=remove_all,
            remove_keydatas=remove_keydatas,
            add_keydatas=add_keydatas,
            urgent=urgent
        )

        xml = self._build_command('update', commands.domain.update_part(name), extensions=(secdns_ext,))
        return self.epp.cmd(xml)

    def cancel_delete(self, name):
        """
        Cancel deletion
        """
        # Extension by SIDN
        xml = self._build_command(None, commands.domain.cancel_delete_parts(name))
        return self.epp.cmd(xml)

    def transfer(self, name, token):
        """
        Initiate the domain transfer.
        """
        # https://tools.ietf.org/html/rfc5730#section-2.9.3.4
        xml = self._build_command('transfer', commands.domain.transfer_req_part(name, token), op='request')
        return self.epp.cmd(xml)

    def get_transfer_status(self, name):
        """
        Query the status of current domain transfer.
        """
        # https://tools.ietf.org/html/rfc5730#section-2.9.2.4
        xml = self._build_command('transfer', commands.domain.transfer_query_part(name), op='query')
        res = self.epp.cmd(xml)
        return self._parse_transfer_status(res.resData)

    @staticmethod
    def _parse_transfer_status(resData):
        trnData = resData.find('domain:trnData', NS)

        return objects.TransferStatus(
            name=_get_xml_text(trnData, 'domain:name'),
            trStatus=_get_xml_text(trnData, 'domain:trStatus'),
            reID=_get_xml_text(trnData, 'domain:reID'),  # requested client
            reDate=_get_xml_date(trnData, 'domain:reDate'),
            acID=_get_xml_text(trnData, 'domain:acID'),  # acting client
            acDate=_get_xml_date(trnData, 'domain:acDate'),
            exDate=_get_xml_date(trnData, 'domain:exDate'),
        )



class ContactHandler(BaseHandler):
    """
    Actions for contacts
    """

    def is_available(self, handle):
        """
        Check if a given handle is available.
        """
        xml = self._build_command('check', commands.contact.check_part(handle))

        from sidn.client import EPPError
        try:
            res = self.epp.cmd(xml)
        except EPPError as e:
            if e.code == EPP_DATA_MGMT_POLICY and e.ext_code == SIDN_EXT_HANDLE_NOT_ASSOCIATED:
                return False
            raise
        return self._parse_avail(res.resData)

    @staticmethod
    def _parse_avail(resData):
        status = resData.find('contact:chkData/contact:cd/contact:id', NS).attrib['avail']
        return status in ('1', 'true')

    def create(self, id, name, organisation=None, street=None, city=None, postcode=None, country_code=None,
               phone=None, fax=None, email=None, legalForm='ANDERS', legalFormRegNo=None):
        """
        Create a contact.

        Allowed Dutch legalForm options:

        * ``ANDERS``      - Anders
        * ``BGG``         - Buitenlandse EG vennootschap
        * ``BRO``         - Buitenlandse rechtsvorm/onderneming/nevenvestiging
        * ``BV``          - Besloten Vennootschap
        * ``BVI/O``       - B.V. in oprichting
        * ``COOP``        - Cooperatie
        * ``CV``          - Commanditaire Vennootschap
        * ``EENMANSZAAK`` - Eenmanszaak
        * ``EESV``        - Europees Economisch Samenwerkingsverband
        * ``KERK``        - Kerkgenootschap
        * ``MAATSCHAP``   - Maatschap
        * ``NV``          - Naamloze Vennootschap
        * ``OWM``         - Onderlinge Waarborg Maatschappij
        * ``PERSOON``     - Natuurlijk persoon
        * ``REDR``        - Rederij
        * ``STICHTING``   - Stichting
        * ``VERENIGING  - Vereniging
        * ``VOF         - Vennootschap onder firma

        :param id: object ID, will be ignored.
        :param name: Unicode name for the person.
        :param organisation: Organisation name (department in DRS5)
        :param street: Street + house number. Can also be a list for line1/line2.
        :param city: City of the address.
        :param postcode: Postal code, required for NL.
        :param country_code: ISO Country code.
        :param phone: Phone number, required.
        :param fax: Fax number, optional.
        :param email: Email, optional.
        :returns: The contact handle.
        """
        xml = self._build_command('create', commands.contact.create_part(
            handle=id,  # Mandatory, but will be ignored
            name=name,
            org=organisation,  # department in DRS5
            street=street,
            city=city,
            pc=postcode,
            cc=country_code,
            voice=phone,
            fax=fax,
            email=email,
            legalForm=legalForm,
            legalFormRegNo=legalFormRegNo,
        ))
        res = self.epp.cmd(xml).resData
        return res.find('contact:creData/contact:id', NS).text

    def update(self, handle, name, organisation=None, street=None, city=None, postcode=None, country_code=None, phone=None, fax=None, email=None, legalForm='ANDERS', legalFormRegNo=None):
        """
        Update an existing contact.

        Any omitted fields will be reset, so make sure to pass all data.
        """
        xml = self._build_command('update', commands.contact.update_part(
            handle=handle,
            name=name,
            org=organisation,  # department in DRS5
            street=street,
            city=city,
            pc=postcode,
            cc=country_code,
            voice=phone,
            fax=fax,
            email=email,
            legalForm=legalForm,
            legalFormRegNo=legalFormRegNo,
        ))
        self.epp.cmd(xml)

    def get(self, handle):
        """
        Fetch contact data
        """
        xml = self._build_command('info', commands.contact.info_part(handle))
        resdata = self.epp.cmd(xml).resData
        return self._parse_info(resdata)

    @staticmethod
    def _parse_info(resData):
        infData = resData.find('contact:infData', NS)
        loc = infData.find("contact:postalInfo[@type='loc']", NS)
        addr = loc.find('contact:addr', NS)

        return objects.Contact(
            id=_get_xml_text(infData, 'contact:id'),
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
            crDate=_get_xml_date(infData, 'contact:crDate'),
            upDate=_get_xml_date(infData, 'contact:upDate'),
        )

    def delete(self, name):
        """
        Delete a contact
        """
        xml = self._build_command('delete', commands.contact.delete_part(name))
        return self.epp.cmd(xml)


class HostHandler(BaseHandler):
    """
    Handler for host data

    This is used to register nameservers, with their IPv4 and IPv6 addresses.
    Currently those commands are not implemented, it's assumed the values are configured manually in DRS5.
    """

    def get(self, nameserver):
        xml = commands.host.info_part.format(name=nameserver)
        resdata = self.epp.cmd(xml).resData
        return objects.Host(
            name=nameserver,
            addr=resdata.find('host:addr', NS).text
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


def _get_xml_date(node, name):
    text = _get_xml_text(node, name)
    return _parse_iso_date(text)


def _parse_iso_date(date):
    if date is None:
        return None
    else:
        # Dates like: 1995-12-10T23:00:00.000Z
        return dateutil.parser.parse(date)
