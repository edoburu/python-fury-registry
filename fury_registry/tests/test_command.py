from unittest import TestCase

from dateutil.tz import tzutc

from fury_registry import commands
from fury_registry.handlers import ContactHandler, DomainHandler
from fury_registry.response import register_namespaces

UTC = tzutc()


class CommandTests(TestCase):
    """Simple test case for parsers
    """

    maxDiff = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        register_namespaces()

    def test_build_domain_create(self):
        xml = commands.domain.create_part(
            name="example.nl",
            ns=["ns1.example.nl", "ns2.example.nl"],
            registrant="REG",
            contacts={
                "admin": "ADMIN",
                "tech": "TECH",
            },
        )

        xml = DomainHandler(None)._build_command("create", xml)
        self.assertEqual(
            xml,
            """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
  <command>
    <create>
      <domain:create xmlns:domain="urn:ietf:params:xml:ns:domain-1.0">
        <domain:name>example.nl</domain:name>
          <domain:ns>
            <domain:hostObj>ns1.example.nl</domain:hostObj>
            <domain:hostObj>ns2.example.nl</domain:hostObj>
          </domain:ns>
        <domain:registrant>REG</domain:registrant>
        <domain:contact type="admin">ADMIN</domain:contact>
        <domain:contact type="tech">TECH</domain:contact>
        <domain:authInfo>
          <domain:pw>unused</domain:pw>
        </domain:authInfo>
      </domain:create>
    </create>
    <clTRID>unused</clTRID>
  </command>
</epp>""",
        )

    def test_build_domain_get(self):
        """Parse contact info response
        """
        xml = DomainHandler(None)._build_command(
            "info", commands.domain.info_part(name="example.nl"),
        )
        self.assertEqual(
            xml,
            """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
  <command>
    <info>
      <domain:info xmlns:domain="urn:ietf:params:xml:ns:domain-1.0">
        <domain:name hosts="all">example.nl</domain:name>
      </domain:info>
    </info>
    <clTRID>unused</clTRID>
  </command>
</epp>""",
        )

    def test_build_domain_check(self):
        """Parse contact info response
        """
        xml = DomainHandler(None)._build_command(
            "check", commands.domain.check_part(name="example.nl"),
        )
        self.assertEqual(
            xml,
            """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
  <command>
    <check>
      <domain:check xmlns:domain="urn:ietf:params:xml:ns:domain-1.0">
        <domain:name>example.nl</domain:name>
      </domain:check>
    </check>
    <clTRID>unused</clTRID>
  </command>
</epp>""",
        )

    def test_build_domain_delete(self):
        """Parse contact info response
        """
        xml = DomainHandler(None)._build_command(
            "delete", commands.domain.delete_part(name="example.nl"),
        )
        self.assertEqual(
            xml,
            """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
  <command>
    <delete>
      <domain:delete xmlns:domain="urn:ietf:params:xml:ns:domain-1.0">
        <domain:name>example.nl</domain:name>
      </domain:delete>
    </delete>
    <clTRID>unused</clTRID>
  </command>
</epp>""",
        )

    def test_build_contact_get(self):
        """Parse contact info response
        """
        xml = ContactHandler(None)._build_command(
            "info", commands.contact.info_part(handle="CONTACT"),
        )
        self.assertEqual(
            xml,
            """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
  <command>
    <info>
      <contact:info xmlns:contact="urn:ietf:params:xml:ns:contact-1.0">
        <contact:id>CONTACT</contact:id>
      </contact:info>
    </info>
    <clTRID>unused</clTRID>
  </command>
</epp>""",
        )

    def test_build_contact_delete(self):
        """Parse contact info response
        """
        xml = ContactHandler(None)._build_command(
            "delete", commands.contact.delete_part(handle="CONTACT"),
        )
        self.assertEqual(
            xml,
            """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
  <command>
    <delete>
      <contact:delete xmlns:contact="urn:ietf:params:xml:ns:contact-1.0">
        <contact:id>CONTACT</contact:id>
      </contact:delete>
    </delete>
    <clTRID>unused</clTRID>
  </command>
</epp>""",
        )
