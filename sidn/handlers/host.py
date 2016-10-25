"""
All specialized commands are performed by these handlers.
"""
from sidn.constants import XMLNS
from sidn import commands
from sidn import objects

from .base import BaseHandler


class HostHandler(BaseHandler):
    """
    Handler for host data

    This is used to register nameservers, with their IPv4 and IPv6 addresses.
    Currently those commands are not implemented, it's assumed the values are configured manually in DRS5.
    """

    def create(self, name, ipv4_addresses=(), ipv6_addresses=()):
        xml = commands.host.create_part(
            name=name,
            ipv4=ipv4_addresses,
            ipv6=ipv6_addresses,
        )

        xml = self._build_command('create', xml)
        return self.epp.cmd(xml)

    def get(self, nameserver):
        xml = commands.host.info_part(name=nameserver)
        resdata = self.epp.cmd(xml).resData
        # TODO: complete this.
        return objects.EppHost(
            name=nameserver,
            addr=resdata.find('host:addr', XMLNS).text
        )

    def delete(self, name):
        """
        Delete a contact
        """
        xml = self._build_command('delete', commands.host.delete_part(name))
        return self.epp.cmd(xml)

    # TODO: update()
    # TODO: check()
