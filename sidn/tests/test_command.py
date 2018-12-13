from unittest import TestCase

from dateutil.tz import tzutc

from sidn import commands
from sidn.handlers import DomainHandler, ContactHandler
from sidn.response import register_namespaces

UTC = tzutc()


class CommandTests(TestCase):
    """
    Simple test case for parsers
    """
    maxDiff = None

    @classmethod
    def setUpClass(cls):
        super(CommandTests, cls).setUpClass()
        register_namespaces()

    def test_build_domain_get(self):
        """
        Parse contact info response
        """
        xml = DomainHandler(None)._build_command('info', commands.domain.info_part(name='example.nl'))
        self.assertEqual(
            xml,
            '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
  <command>
    <info>
      <domain:info xmlns:domain="urn:ietf:params:xml:ns:domain-1.0">
        <domain:name hosts="all">example.nl</domain:name>
      </domain:info>
    </info>
    <clTRID>unused</clTRID>
  </command>
</epp>''')

    def test_build_contact_get(self):
        """
        Parse contact info response
        """
        xml = ContactHandler(None)._build_command('info', commands.contact.info_part(handle='CONTACT'))
        self.assertEqual(
            xml,
            '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
  <command>
    <info>
      <contact:info xmlns:contact="urn:ietf:params:xml:ns:contact-1.0">
        <contact:id>CONTACT</contact:id>
      </contact:info>
    </info>
    <clTRID>unused</clTRID>
  </command>
</epp>''')
