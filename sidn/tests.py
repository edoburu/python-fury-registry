from unittest import TestCase

from datetime import datetime
from dateutil.tz import tzutc

from sidn.client import EPP, EPPError, EPPPollResponse
from sidn.constants import EPP_QUEUE_NOT_EMPTY, EPP_QUEUE_EMPTY
from sidn.handlers import ContactHandler, DomainHandler
from sidn.response import get_node_text, register_namespaces


class ParserTests(TestCase):
    """
    Simple test case for parsers
    """

    @classmethod
    def setUpClass(cls):
        super(ParserTests, cls).setUpClass()
        register_namespaces()

    def test_parse_contact(self):
        """
        Parse contact info response
        """
        contact_info = '''
    <epp xmlns="urn:ietf:params:xml:ns:epp-1.0" xmlns:contact="urn:ietf:params:xml:ns:contact-1.0" xmlns:sidn-ext-epp="http://rxsd.domain-registry.nl/sidn-ext-epp-1.0">
        <response>
            <result code="1000">
                <msg>The contact person has been queried.</msg>
            </result>
            <resData>
                <contact:infData>
                    <contact:id>WAL002352-NLCOM</contact:id>
                    <contact:roid>CPN_1338408-SIDN</contact:roid>
                    <contact:status s="linked" />
                    <contact:status s="ok" />
                    <contact:postalInfo type="loc">
                        <contact:name>S.J. de Wal</contact:name>
                        <contact:addr>
                            <contact:street>Schumanpark 29-31</contact:street>
                            <contact:city>Apeldoorn</contact:city>
                            <contact:pc>7336AM</contact:pc>
                            <contact:cc>NL</contact:cc>
                        </contact:addr>
                    </contact:postalInfo>
                    <contact:voice>+31.555772890</contact:voice>
                    <contact:email>nobody@domain-registry.nl</contact:email>
                    <contact:clID>NLCOM</contact:clID>
                    <contact:crID>NLCOM</contact:crID>
                    <contact:crDate>1979-12-31T23:00:00.000Z</contact:crDate>
                    <contact:upID>SIDN1</contact:upID>
                    <contact:upDate>2011-03-14T15:49:34.000Z</contact:upDate>
                </contact:infData>
            </resData>
            <extension>
                <sidn-ext-epp:ext>
                    <sidn-ext-epp:infData>
                        <sidn-ext-epp:contact>
                            <sidn-ext-epp:legalForm>ANDERS</sidn-ext-epp:legalForm>
                            <sidn-ext-epp:limited>false</sidn-ext-epp:limited>
                        </sidn-ext-epp:contact>
                    </sidn-ext-epp:infData>
                </sidn-ext-epp:ext>
            </extension>
            <trID>
                <clTRID>unused</clTRID>
                <svTRID>6442820A-3393-5B84-422B-9ED566B6042B</svTRID>
            </trID>
        </response>
    </epp>'''
        resData = EPP._parse_response(contact_info).resData
        contact = ContactHandler._parse_info(resData)
        self.assertEqual(contact.handle, 'WAL002352-NLCOM')
        self.assertEqual(contact.name, 'S.J. de Wal')

    def test_parse_domain(self):
        """
        Parse domain info response.
        """
        domain_info = '''
    <epp xmlns="urn:ietf:params:xml:ns:epp-1.0" xmlns:domain="urn:ietf:params:xml:ns:domain-1.0" xmlns:sidn-ext-epp="http://rxsd.domain-registry.nl/sidn-ext-epp-1.0">
        <response>
            <result code="1000">
                <msg>The domain name has been queried.</msg>
            </result>
            <resData>
                <domain:infData>
                    <domain:name>computel.nl</domain:name>
                    <domain:roid>DNM_1496-SIDN</domain:roid>
                    <domain:status s="ok"/>
                    <domain:registrant>COM017325-NLCOM</domain:registrant>
                    <domain:contact type="admin">COM017325-NLCOM</domain:contact>
                    <domain:contact type="tech">WAL002352-NLCOM</domain:contact>
                    <domain:ns>
                        <domain:hostObj>ns2.computel.nl</domain:hostObj>
                        <domain:hostObj>ns1.computel.nl</domain:hostObj>
                    </domain:ns>
                    <domain:host>ns1.computel.nl</domain:host>
                    <domain:host>ns.computel.nl</domain:host>
                    <domain:host>ns2.computel.nl</domain:host>
                    <domain:host>ns3.computel.nl</domain:host>
                    <domain:clID>NLCOM</domain:clID>
                    <domain:crID>NLCOM</domain:crID>
                    <domain:crDate>1995-12-10T23:00:00.000Z</domain:crDate>
                    <domain:upID>NLCOM</domain:upID>
                    <domain:upDate>2010-10-25T09:13:51.000Z</domain:upDate>
                    <domain:exDate>2016-02-17T15:30:42.000Z</domain:exDate>
                    <domain:authInfo>
                        <domain:pw>C6NtcSfYx2ZM</domain:pw>
                    </domain:authInfo>
                </domain:infData>
            </resData>
            <extension>
                <sidn-ext-epp:ext>
                    <sidn-ext-epp:infData>
                        <sidn-ext-epp:domain>
                            <sidn-ext-epp:optOut>false</sidn-ext-epp:optOut>
                            <sidn-ext-epp:limited>false</sidn-ext-epp:limited>
                            <sidn-ext-epp:period>3</sidn-ext-epp:period>
                        </sidn-ext-epp:domain>
                    </sidn-ext-epp:infData>
                </sidn-ext-epp:ext>
            </extension>
        </response>
    </epp>'''

        resData = EPP._parse_response(domain_info).resData
        domain = DomainHandler._parse_info(resData)
        self.assertEqual(domain.name, 'computel.nl')
        self.assertEqual(domain.ns, ['ns2.computel.nl', 'ns1.computel.nl'])
        self.assertEqual(domain.admin, 'COM017325-NLCOM')
        self.assertEqual(domain.tech, 'WAL002352-NLCOM')

    def test_parse_contact_avail(self):
        """
        Handle avail response for contacts.
        """
        avail_response = '''<epp xmlns="urn:ietf:params:xml:ns:epp-1.0" xmlns:contact="urn:ietf:params:xml:ns:contact-1.0">
        <response>
            <result code="1000">
                <msg>The availability of the contact person has been checked.</msg>
            </result>
            <resData>
                <contact:chkData>
                    <contact:cd>
                        <contact:id avail="false">WAL002352-NLCOM</contact:id>
                    </contact:cd>
                </contact:chkData>
            </resData>
            <trID>
                <clTRID>unused</clTRID>
                <svTRID>DBD51C56-8635-544F-E1AF-0AA7501C04F4</svTRID>
            </trID>
        </response>
    </epp>'''

        resData = EPP._parse_response(avail_response).resData
        is_available = ContactHandler._parse_avail(resData)
        self.assertFalse(is_available)

    def test_parse_epp_error_ext(self):
        """
        Make sure EPP errors are handled, and extensions are read.
        """
        response = '''
    <epp xmlns="urn:ietf:params:xml:ns:epp-1.0" xmlns:sidn-ext-epp="http://rxsd.domain-registry.nl/sidn-ext-epp-1.0">
        <response>
            <result code="2308">
                <msg>Validation of the transaction failed.</msg>
            </result>
            <extension>
                <sidn-ext-epp:ext>
                    <sidn-ext-epp:response>
                        <sidn-ext-epp:msg code="C0115" field="Message">The specified handle is not associated with this account.</sidn-ext-epp:msg>
                    </sidn-ext-epp:response>
                </sidn-ext-epp:ext>
            </extension>
            <trID>
                <clTRID>unused</clTRID>
                <svTRID>AB95B312-96C6-A2C8-C174-A250A960D016</svTRID>
            </trID>
        </response>
    </epp>'''
        try:
            EPP._parse_response(response)
        except EPPError as e:
            self.assertEqual(e.code, 2308)
            self.assertEqual(e.message, 'Validation of the transaction failed.')
            self.assertEqual(e.ext_code, 'C0115')
            self.assertEqual(e.ext_message, 'The specified handle is not associated with this account.')
        else:
            self.assertTrue(False, "EPPError not raised")

    def test_parse_poll(self):
        """
        Test parsing for poll responses
        """
        raw_response = '''
    <epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
      <response>
        <result code="1301">
          <msg>Command completed successfully; ack to dequeue</msg>
        </result>
        <msgQ count="5" id="12345">
          <qDate>2000-06-08T22:00:00.0Z</qDate>
          <msg>Transfer requested.</msg>
        </msgQ>
        <resData>
          <obj:trnData xmlns:obj="urn:ietf:params:xml:ns:obj-1.0">
            <obj:name>example.com</obj:name>
            <obj:trStatus>pending</obj:trStatus>
            <obj:reID>ClientX</obj:reID>
            <obj:reDate>2000-06-08T22:00:00.0Z</obj:reDate>
            <obj:acID>ClientY</obj:acID>
            <obj:acDate>2000-06-13T22:00:00.0Z</obj:acDate>
            <obj:exDate>2002-09-08T22:00:00.0Z</obj:exDate>
          </obj:trnData>
        </resData>
        <trID>
          <clTRID>ABC-12345</clTRID>
          <svTRID>54321-XYZ</svTRID>
        </trID>
      </response>
    </epp>'''
        response = EPP._parse_response(raw_response, response_class=EPPPollResponse)
        self.assertEqual(response.result_code, EPP_QUEUE_NOT_EMPTY)
        self.assertEqual(response.message_count, 5)
        self.assertEqual(response.message_date, datetime(2000, 6, 8, 22, 0, 0, tzinfo=tzutc()))
        self.assertEqual(response.message, 'Transfer requested.')
        self.assertEqual(response.result_msg, 'Command completed successfully; ack to dequeue')
        self.assertEqual(get_node_text(response.resData, 'obj:trnData/obj:name'), 'example.com')
        self.assertEqual(response.clTRID, 'ABC-12345')
        self.assertEqual(response.svTRID, '54321-XYZ')

    def test_parse_empty_poll(self):
        """
        Handle nodes without msgQ element.
        """
        raw_response = '''
    <epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
        <response>
            <result code="1300">
                <msg>There are no messages in the queue.</msg>
            </result>
            <trID>
                <clTRID>unused</clTRID>
                <svTRID>5A220D87-F00D-A8B3-BE74-076FE7B50149</svTRID>
            </trID>
        </response>
    </epp>'''
        response = EPP._parse_response(raw_response, response_class=EPPPollResponse)
        self.assertEqual(response.result_code, EPP_QUEUE_EMPTY)
        self.assertEqual(response.message_count, 0)
        self.assertEqual(response.message_date, None)
        self.assertEqual(response.message, None)
        self.assertEqual(response.result_msg, 'There are no messages in the queue.')
