"""
All specialized commands are performed by these handlers.
"""
from fury_registry import commands, objects
from fury_registry.constants import XMLNS

from .base import BaseHandler


class DomainHandler(BaseHandler):
    """
    Actions for domains.
    """

    def get(self, domain_name):
        """
        Request the info of a domain

        It raises an :class:`~fury_registry.client.EPPError` when:
        * the domain does not exist: code 2303 (``EPP_OBJECT_DOES_NOT_EXIST``, with ``SIDN_EXT_DOMAIN_DOES_NOT_EXIST``).
        * the domain is managed by other accounts: code 2308 (``EPP_DATA_MGMT_POLICY``, with ``SIDN_EXT_NOT_MANAGED_BY_ACCOUNT``)
        """
        # https://tools.ietf.org/html/rfc5730#section-2.9.2.2
        xml = self._build_command('info', commands.domain.info_part(name=domain_name))
        response = self.epp.cmd(xml)

        domain = objects.FuryDomain.from_xml(response.resData, response.extension)
        domain._epp = self.epp  # Sneak it in
        return domain

    def check(self, domain_name):
        """
        Check if a domain is available.
        """
        # https://tools.ietf.org/html/rfc5730#section-2.9.2.1
        xml = self._build_command('check', commands.domain.check_part(name=domain_name))
        response = self.epp.cmd(xml)
        return self._parse_avail(response)

    @staticmethod
    def _parse_avail(response):
        # Note that the domain:cd element may be repeated
        # The element may also contain a <domain:reason> element.
        return response.resData.find('domain:chkData/domain:cd/domain:name', XMLNS).attrib['avail'] in ('1', 'true')

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
        :type dskeys: Iterator[fury_registry.objects.DSKey]
        :param keyData: DNSSec keydata, as alternative for ``keys``, max 4 with SIDN.
        :type keyData: Iterator[fury_registry.objects.KeyData]
        """
        # https://tools.ietf.org/html/rfc5730#section-2.9.3.1
        # https://tools.ietf.org/html/rfc5731#section-3.2.1
        xml = commands.domain.create_part(
            name=name,
            ns=ns,
            registrant=registrant,
            contacts=contacts,
        )

        if dskeys or keyData:
            # SIDN only looks at the keydata fields.
            # https://tools.ietf.org/html/rfc5910#section-5.2.1
            extensions = (commands.secdns.create(dskeys=dskeys, keyData=keyData),)
        else:
            extensions = ()

        xml = self._build_command('create', xml, command_extensions=extensions)
        return self.epp.cmd(xml)

    def update(self, name, registrant=None,
               remove_contacts=None, remove_statuses=(), remove_ns=(),
               remove_all_keys=False, remove_keydatas=(),
               add_contacts=None, add_statuses=(), add_ns=(),
               add_keydatas=(), dnssec_urgent=False):
        """
        Update the domain.

        :param name: The domain name
        :param registrant: New registrant handle, if given.
        :param remove_contacts: dict of contact handles to remove (admin: ..., tech: ...)
        :param remove_ns: iterable of nameservers to remove.
        :param add_contacts: iterable of contact handles to add.
        :param add_ns: iterable of nameservers to add.

        Note that DRS5 only allows one admin handle;
        after the removal/adding of handles there should be 1 handle again.
        You can use the convenience methods on the :class:`~fury_registry.objects.Domain` class
        to remove existing handles, and assign new ones.
        """
        command_extensions = ()
        if remove_all_keys or remove_keydatas or add_keydatas or dnssec_urgent:
            command_extensions = (commands.secdns.update(
                remove_all=remove_all_keys,
                remove_keydatas=remove_keydatas,
                add_keydatas=add_keydatas,
                urgent=dnssec_urgent
            ),)

        # https://tools.ietf.org/html/rfc5730#section-2.9.3.5
        # https://tools.ietf.org/html/rfc5731#section-3.2.5
        xml = self._build_command('update', commands.domain.update_part(
            name=name,
            registrant=registrant,
            remove_ns=remove_ns,
            remove_contacts=remove_contacts,
            remove_statuses=remove_statuses,
            add_ns=add_ns,
            add_contacts=add_contacts,
            add_statuses=add_statuses,
        ), command_extensions=command_extensions)
        return self.epp.cmd(xml)

    def update_keys(self, name, remove_all=False, remove_keydatas=(), add_keydatas=(), urgent=False):
        """
        Update the DNSSec keys in a domain
        :type remove_keydatas: Iterator[fury_registry.objects.DSKey]
        :type add_keydatas: Iterator[fury_registry.objects.DSKey]
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

    def restore(self, name):
        """
        Cancel deletion
        """
        # Fury extension
        xml = self._build_command('update', commands.domain.update_part(name), command_extensions=(commands.domain.restore_part(name),))
        return self.epp.cmd(xml)

    def renew(self, name, expiration_date, period, period_unit='y'):
        """
        Renew the registration period of the domain.

        :param name: Domain name
        :param expiration_date: The expiration date of the domain.
        :param period: integer, the number of months or years depending on the ``period_unit``.
        :type period: int
        :param period_unit: ``y`` (years) or ``m`` (months)
        """
        xml = self._build_command('renew', commands.domain.renew_part(name, expiration_date, period, period_unit))
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

        When the domain is not in transfer, an :class:`~fury_registry.client.EPPError` will be raised,
        with code 2301 (``EPP_OBJECT_NOT_PENDING_XFR``).

        :rtype: fury_registry.objects.TransferStatus
        """
        # https://tools.ietf.org/html/rfc5730#section-2.9.2.4
        xml = self._build_command('transfer', commands.domain.transfer_query_part(name), op='query')
        response = self.epp.cmd(xml)
        return self._parse_transfer_status(response)

    def approve_transfer(self, name):
        """
        Query the status of current domain transfer.

        :rtype: fury_registry.objects.TransferStatus
        """
        # https://tools.ietf.org/html/rfc5730#section-2.9.2.4
        xml = self._build_command('transfer', commands.domain.transfer_query_part(name), op='approve')
        response = self.epp.cmd(xml)
        return self._parse_transfer_status(response)

    def reject_transfer(self, name):
        """
        Query the status of current domain transfer.

        :rtype: fury_registry.objects.TransferStatus
        """
        # https://tools.ietf.org/html/rfc5730#section-2.9.2.4
        xml = self._build_command('transfer', commands.domain.transfer_query_part(name), op='reject')
        response = self.epp.cmd(xml)
        return self._parse_transfer_status(response)

    @staticmethod
    def _parse_transfer_status(response):
        trnData = response.resData.find('domain:trnData', XMLNS)
        return objects.TransferStatus.from_xml(trnData)
