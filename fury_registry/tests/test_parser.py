from copy import copy
from datetime import datetime
from unittest import TestCase

from dateutil.tz import tzutc
from fury_registry.client import EPP, EPPError, EPPPollResponse
from fury_registry.constants import EPP_QUEUE_EMPTY, EPP_QUEUE_NOT_EMPTY
from fury_registry.handlers import ContactHandler
from fury_registry.objects import EppContact, EppHost, KeyData, FuryDomain
from fury_registry.response import register_namespaces
from fury_registry.utils import get_node_text

UTC = tzutc()


class ParserTests(TestCase):
    """
    Simple test case for parsers
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
            <trID>
                <clTRID>unused</clTRID>
                <svTRID>6442820A-3393-5B84-422B-9ED566B6042B</svTRID>
            </trID>
        </response>
    </epp>'''
        response = EPP._parse_response(contact_info)
        contact = EppContact.from_xml(response.resData, response.extension)
        self.assertEqual(contact.handle, 'WAL002352-NLCOM')
        self.assertEqual(contact.name, 'S.J. de Wal')

    def test_parse_domain(self):
        """
        Parse domain info response.
        """
        domain_info = '''
    <epp xmlns="urn:ietf:params:xml:ns:epp-1.0" xmlns:domain="urn:ietf:params:xml:ns:domain-1.0" xmlns:secDNS="urn:ietf:params:xml:ns:secDNS-1.1" xmlns:sidn-ext-epp="http://rxsd.domain-registry.nl/sidn-ext-epp-1.0">
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
                <fury-rgp:rgpInfo xmlns:fury-rgp="urn:ietf:params:xml:ns:fury-rgp-1.0">
                    <fury-rgp:rgpStatusEnd>2020-12-28T22:00:00.0Z</fury-rgp:rgpStatusEnd>
                </fury-rgp:rgpInfo>
                <secDNS:infData>
                    <secDNS:keyData>
                        <secDNS:flags>257</secDNS:flags>
                        <secDNS:protocol>3</secDNS:protocol>
                        <secDNS:alg>8</secDNS:alg>
                        <secDNS:pubKey>AwEAAao2zeD+21pkAt7Aga437btAcpT5xvXfxbneHzYgOW4XyqogQ0d6cAmX0lMrnDw8JuU56QHV9Gm7oSZjOG77RoIRvhaeGgLezizFNZ8PJujyfdKl79ZX02cUjDRkt5dqR2gsqPcEUtv5gARTmM2fCPeDwU+hX/asXTLc/79ukKryaqNEMiQOpOY+Zve4qJKRCUhq1MEcMvMEq5GQuFyOuRUEzif+vIkXQ9tjJr3YeVAvfsSk9UoUk7jNz6NPp/7gx4wK1dAHv8adSTYCMVUbJcvBXj8hq33Gg02W8Fgz0wtFEeu3f4+eK5yOtInDsko8XvhwT7bj1nOYd6ulNsNurlE=</secDNS:pubKey>
                    </secDNS:keyData>
                </secDNS:infData>
            </extension>
        </response>
    </epp>'''

        response = EPP._parse_response(domain_info)
        domain = FuryDomain.from_xml(response.resData, response.extension)
        self.assertEqual(domain.name, 'computel.nl')
        self.assertEqual(domain.ns, ['ns2.computel.nl', 'ns1.computel.nl'])
        self.assertEqual(domain.admin, 'COM017325-NLCOM')
        self.assertEqual(domain.tech, 'WAL002352-NLCOM')
        self.assertEqual(domain.opt_out, False)
        self.assertEqual(domain.limited, False)
        self.assertEqual(domain.period, 3)
        self.assertEqual(domain.dnssec.keydatas[0].alg, KeyData.ALG_SHA256)
        self.assertEqual(domain.dnssec.keydatas[0].protocol, KeyData.PROTOCOL3)
        self.assertEqual(domain.dnssec.keydatas[0].flags, KeyData.FLAG_KSK)
        self.assertTrue(domain.dnssec.keydatas[0].pubKey.startswith('AwEAAao2zeD'))
        self.assertEqual(domain.rgp_status_end.isoformat(), '2020-12-28T22:00:00+00:00')

        # testing DNSSec.__contains() and KeyData.__eq__().
        # This is also used for EppDomain.update()
        dnssec = domain.dnssec
        self.assertTrue(copy(dnssec.keydatas[0]) in domain.dnssec)

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

        response = EPP._parse_response(avail_response)
        is_available = ContactHandler._parse_avail(response)
        self.assertFalse(is_available)

    def test_parse_host(self):
        raw_response = '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
    <epp xmlns="urn:ietf:params:xml:ns:epp-1.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
      <response>
        <result code="1000">
          <msg>Command completed successfully</msg>
        </result>
        <resData>
          <host:infData xmlns:host="urn:ietf:params:xml:ns:host-1.0">
            <host:name>ns0.epp-example.co.uk.</host:name>
            <host:roid>548965487-UK</host:roid>
            <host:status s="ok"/>
            <host:addr ip="v4">123.123.123.123</host:addr>
            <host:addr ip="v6">1080:0:0:0:8:800:200C:417B</host:addr>
            <host:clID>EXAMPLE_TAG</host:clID>
            <host:crID>epp-user</host:crID>
            <host:crDate>2008-06-12T06:46:00Z</host:crDate>
          </host:infData>
        </resData>
        <trID>
          <clTRID>EPP-ABC-12345</clTRID>
          <svTRID>116890</svTRID>
        </trID>
      </response>
    </epp>'''
        response = EPP._parse_response(raw_response)
        host = EppHost.from_xml(response.resData, response.extension)
        self.assertEqual(host.name, 'ns0.epp-example.co.uk.')
        self.assertEqual(host.addr, ['123.123.123.123', '1080:0:0:0:8:800:200C:417B'])
        self.assertEqual(host.cl_id, 'EXAMPLE_TAG')
        self.assertEqual(host.cr_id, 'epp-user')
        self.assertEqual(host.created_date, datetime(2008, 6, 12, 6, 46, tzinfo=UTC))

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
            self.assertEqual(e.ext_reason, 'The specified handle is not associated with this account.')
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
        response = EPP._parse_response(raw_response, response_class=EPPPollResponse)  # type: EPPPollResponse
        self.assertEqual(response.result_code, EPP_QUEUE_NOT_EMPTY)
        self.assertEqual(response.queue_count, 5)
        self.assertEqual(response.queue_date, datetime(2000, 6, 8, 22, 0, 0, tzinfo=UTC))
        self.assertEqual(response.message, 'Transfer requested.')
        self.assertEqual(response.result_msg, 'Command completed successfully; ack to dequeue')
        self.assertEqual(get_node_text(response.resData, 'obj:trnData/obj:name'), 'example.com')
        self.assertEqual(response.clTRID, 'ABC-12345')
        self.assertEqual(response.svTRID, '54321-XYZ')
        self.assertTrue(bool(response))

    def test_parse_poll_ext_transfer_start(self):
        """
        Test the SIDN extended message that a poll on DRS returns.
        """
        raw_response = '''<?xml version="1.0" encoding="utf-8"?>
    <epp xmlns="urn:ietf:params:xml:ns:epp-1.0" xmlns:sidn-ext-epp="http://rxsd.domain-registry.nl/sidn-ext-epp-1.0"
        xmlns:domain="urn:ietf:params:xml:ns:domain-1.0">
        <response>
            <result code="1301">
                <msg>The message has been picked up. Please confirm receipt to remove
                    the message from the queue.</msg>
            </result>
            <msgQ count="1" id="100206">
                <qDate>2010-02-11T09:18:46.000Z</qDate>
                <msg>1014 Verhuizen domeinnaam for-transfer-03.nl in behandeling
                    genomen</msg>
            </msgQ>
            <resData>
                <sidn-ext-epp:pollData>
                    <sidn-ext-epp:command>domain:transfer-start</sidn-ext-epp:command>
                    <sidn-ext-epp:data>
                        <result code="1000">
                            <msg>Transfer of the domain name has begun.</msg>
                        </result>
                        <resData>
                            <domain:trnData>
                                <domain:name>for-transfer-03.nl</domain:name>
                                <domain:trStatus>pending</domain:trStatus>
                                <domain:reID>IWORK</domain:reID>
                                <domain:reDate>2010-02-11T09:18:46.000Z</domain:reDate>
                                <domain:acID>X1140</domain:acID>
                                <domain:acDate>2010-02-11T09:48:46.000Z</domain:acDate>
                            </domain:trnData>
                        </resData>
                        <trID>
                            <svTRID>28096172</svTRID>
                        </trID>
                    </sidn-ext-epp:data>
                </sidn-ext-epp:pollData>
            </resData>
            <trID>
                <clTRID>900398-1265880242</clTRID>
                <svTRID>C54BF9AD-907C-4C5C-F791-AE0CB997716E</svTRID>
            </trID>
        </response>
    </epp>'''

        response = EPP._parse_response(raw_response, response_class=EPPPollResponse)  # type: EPPPollResponse
        self.assertEqual(response.result_code, EPP_QUEUE_NOT_EMPTY)
        self.assertEqual(response.pollData.command, 'domain:transfer-start')
        self.assertEqual(response.pollData.code, 1000)
        self.assertEqual(response.pollData.message, "Transfer of the domain name has begun.")
        self.assertEqual(response.pollData.object.name, 'for-transfer-03.nl')

    def test_parse_poll_ext_transfer(self):
        """
        Test poll notification that a transfer was completed.
        """
        raw_response = '''<?xml version="1.0" encoding="UTF-8"?>
    <epp xmlns="urn:ietf:params:xml:ns:epp-1.0" xmlns:sidn-ext-epp="http://rxsd.domain-registry.nl/sidn-ext-epp-1.0" xmlns:domain="urn:ietf:params:xml:ns:domain-1.0">
        <response>
            <result code="1301">
                <msg>The message has been picked up. Please confirm receipt to remove the message from the queue.</msg>
            </result>
            <msgQ id="2260594" count="1">
                <qDate>2016-10-21T11:45:00.000Z</qDate>
                <msg>1016 Verhuizing domeinnaam for-transfer-05.nl verwerkt</msg>
            </msgQ>
            <resData>
                <sidn-ext-epp:pollData>
                    <sidn-ext-epp:command>domain:transfer</sidn-ext-epp:command>
                    <sidn-ext-epp:data>
                        <result code="1000">
                            <msg>De domeinnaam is verhuisd.</msg>
                        </result>
                        <resData>
                            <domain:trnData>
                                <domain:name>for-transfer-05.nl</domain:name>
                                <domain:trStatus>serverApproved</domain:trStatus>
                                <domain:reID>TRAIP</domain:reID>
                                <domain:reDate>2016-10-21T11:44:58.000Z</domain:reDate>
                                <domain:acID>NLCOM</domain:acID>
                                <domain:acDate>2016-10-21T11:45:00.111Z</domain:acDate>
                            </domain:trnData>
                        </resData>
                        <trID>
                            <svTRID>117307812</svTRID>
                        </trID>
                    </sidn-ext-epp:data>
                </sidn-ext-epp:pollData>
            </resData>
            <trID>
                <clTRID>unused</clTRID>
                <svTRID>BF3075DF-05CD-2000-E2DC-126BB1758597</svTRID>
            </trID>
        </response>
    </epp>'''

        response = EPP._parse_response(raw_response, response_class=EPPPollResponse)  # type: EPPPollResponse
        self.assertEqual(response.result_code, EPP_QUEUE_NOT_EMPTY)
        self.assertEqual(response.pollData.command, 'domain:transfer')
        self.assertEqual(response.pollData.code, 1000)
        self.assertEqual(response.pollData.message, "De domeinnaam is verhuisd.")
        self.assertEqual(response.pollData.object.name, "for-transfer-05.nl")
        self.assertEqual(response.pollData.object.status, "serverApproved")
        self.assertEqual(response.pollData.object.request_id, "TRAIP")  # TransIP
        self.assertEqual(response.pollData.object.request_date, datetime(2016, 10, 21, 11, 44, 58, tzinfo=UTC))
        self.assertEqual(response.pollData.object.act_id, "NLCOM")  # Computel Standby
        self.assertEqual(response.pollData.object.act_date, datetime(2016, 10, 21, 11, 45, 0, 111000, tzinfo=UTC))
        self.assertTrue(bool(response))

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
        response = EPP._parse_response(raw_response, response_class=EPPPollResponse)  # type: EPPPollResponse
        self.assertEqual(response.result_code, EPP_QUEUE_EMPTY)
        self.assertEqual(response.queue_count, 0)
        self.assertEqual(response.queue_date, None)
        self.assertEqual(response.queue_id, None)
        self.assertEqual(response.result_msg, 'There are no messages in the queue.')
        self.assertFalse(bool(response))
