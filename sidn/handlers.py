"""
All specialized commands are performed by these handlers.
"""
from . import commands
from . import objects


class BaseHandler(object):
    def __init__(self, epp):
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
            clTRID=transaction_id or '',
        )


def _get_xml_text(res, name, **attributes):
    # Handling of optional fields
    node = res.find(name, **attributes)
    return node.text if node is not None else None


class DomainHandler(BaseHandler):
    """
    Actions for domains.
    """

    def get(self, domain_name):
        """
        Request the info of a domain
        """
        cmd = self._build_command('info', commands.domain.info_part.format(name=domain_name))
        resdata = self.epp.cmd(cmd).resdata
        ns = []
        for hostobj in resdata.findAll('domain:hostobj'):
            ns.append(hostobj.text)

        domain = objects.Domain(
            name=_get_xml_text(resdata, 'domain:name'),
            pw=_get_xml_text(resdata, 'domain:pw'),
            roid=_get_xml_text(resdata, 'domain:roid'),
            status=_get_xml_text(resdata, 'domain:status').get('s'),
            registrant=_get_xml_text(resdata, 'domain:registrant'),
            admin=_get_xml_text(resdata, 'domain:contact', type='admin'),
            tech=_get_xml_text(resdata, 'domain:contact', type='tech'),
            ns=ns,
            clid=_get_xml_text(resdata, 'domain:clid'),
            crid=_get_xml_text(resdata, 'domain:crid'),
            crdate=_get_xml_text(resdata, 'domain:crdate'),
            exdate=_get_xml_text(resdata, 'domain:exdate')
        )
        domain.epp = self.epp
        return domain

    def is_available(self, domain_name):
        """
        Check if a domain is available.
        """
        cmd = self._build_command('check', commands.domain.check_part(name=domain_name))
        res = self.epp.cmd(cmd)
        if not res:
            return False
        else:
            status = res.resdata.find('domain:name').get('avail')
            return status in ('1', 'true')

    def create(self, name, registrant, admin, tech, ns):
        """
        Create a domain

        :param domain_name: Domain name to register.
        :param registrant: Registrant contact handle
        :param admin: Admin contact handle
        :param tech: Tech contact handle
        :param ns: List of nameserver host names
        :type ns: list
        """
        cmd = self._build_command('create', commands.domain.create_part(
            name=name,
            registrant=registrant,
            admin=admin,
            tech=tech,
            ns=ns
        ))
        return self.epp.cmd(cmd)

    def delete(self, name):
        """
        Delete a domain
        """
        cmd = self._build_command(commands.domain.delete_part(name))
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


class ContactHandler(BaseHandler):
    """
    Actions for contacts
    """

    def is_available(self, handle):
        """
        Check if a given handle is available.
        """
        cmd = self._build_command('check', commands.contact.check_part(handle))
        res = self.epp.cmd(cmd)
        if not res:
            return False
        else:
            status = res.resdata.find('contact:id').get('avail')
            return status in ('1', 'true')

    def create(self, name, street, city, postcode, country_code, department=None, phone=None, fax=None, email=None, legalForm=None, legalFormRegNo=None):
        """
        Create a contact.
        """
        cmd = commands.contact.create(
            handle='',
            name=name,
            org=department,  # in DRS5
            street=street,
            city=city,
            pc=postcode,
            cc=country_code,
            voice=phone,
            fax=fax,
            email=email
        )
        res = self.epp.cmd(cmd).resdata
        return res.find('contact:id').text

    def update(self, handle, name, street, city, postcode, country_code, department=None, phone=None, fax=None, email=None, legalForm=None, legalFormRegNo=None):
        """
        Update an existing contact
        """
        cmd = self._build_command('update', commands.contact.update_part(
            handle=handle,
            name=name,
            org=department,  # in DRS5
            street=street,
            city=city,
            pc=postcode,
            cc=country_code,
            voice=phone,
            fax=fax,
            email=email
        ))
        res = self.epp.cmd(cmd).resdata
        return res.find('contact:id').text

    def get(self, handle):
        """
        Fetch contact data
        """
        cmd = self._build_command('info', commands.contact.info_part(handle))
        resdata = self.epp.cmd(cmd).resdata
        return objects.Contact(
            handle=handle,
            roid=_get_xml_text(resdata, 'contact:roid'),
            status=_get_xml_text(resdata, 'contact:status').get('s'),
            name=_get_xml_text(resdata, 'contact:name'),
            org=_get_xml_text(resdata, 'contact:org'),
            street= _get_xml_text(resdata, 'contact:street'),
            city=_get_xml_text(resdata, 'contact:city'),
            pc=_get_xml_text(resdata, 'contact:pc'),
            cc=_get_xml_text(resdata, 'contact:cc'),
            voice=_get_xml_text(resdata, 'contact:voice'),
            fax=_get_xml_text(resdata, 'contact:fax'),
            email=_get_xml_text(resdata, 'contact:email'),
        )



class HostHandler(BaseHandler):
    """
    Handler for host data
    """

    def get(self, nameserver):
        cmd = commands.host.info_part.format(name=nameserver)
        resdata = self.epp.cmd(cmd).resdata
        return objects.Host(
            name=nameserver,
            addr=resdata.find('host:addr').text
        )
