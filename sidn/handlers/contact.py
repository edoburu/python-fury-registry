"""
All specialized commands are performed by these handlers.
"""
from sidn.constants import XMLNS, EPP_DATA_MGMT_POLICY, SIDN_EXT_HANDLE_NOT_ASSOCIATED
from sidn import commands
from sidn import objects

from .base import BaseHandler


class ContactHandler(BaseHandler):
    """
    Actions for contacts
    """

    def check(self, handle):
        """
        Check if a given handle is available.
        """
        xml = self._build_command('check', commands.contact.check_part(handle))

        from sidn.client import EPPError
        try:
            response = self.epp.cmd(xml)
        except EPPError as e:
            if e.code == EPP_DATA_MGMT_POLICY and e.ext_code == SIDN_EXT_HANDLE_NOT_ASSOCIATED:
                return False
            raise

        return self._parse_avail(response)

    @staticmethod
    def _parse_avail(response):
        return response.resData.find('contact:chkData/contact:cd/contact:id', XMLNS).attrib['avail'] in ('1', 'true')

    def get(self, handle):
        """
        Fetch contact data
        """
        xml = self._build_command('info', commands.contact.info_part(handle))
        response = self.epp.cmd(xml)
        return objects.EppContact.from_xml(response.resData, response.extension)

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
        command, ext = commands.contact.create_parts(
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
        )
        xml = self._build_command('create', command, command_extensions=(ext,))
        res = self.epp.cmd(xml).resData
        return res.find('contact:creData/contact:id', XMLNS).text

    def update(self, handle, name, organisation=None, street=None, city=None, postcode=None, country_code=None, phone=None, fax=None, email=None, legalForm='ANDERS', legalFormRegNo=None):
        """
        Update an existing contact.

        Any omitted fields will be reset, so make sure to pass all data.
        """
        command, ext = commands.contact.update_parts(
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
        )
        xml = self._build_command('update', command, command_extensions=(ext,))
        self.epp.cmd(xml)

    def delete(self, name):
        """
        Delete a contact
        """
        xml = self._build_command('delete', commands.contact.delete_part(name))
        return self.epp.cmd(xml)
