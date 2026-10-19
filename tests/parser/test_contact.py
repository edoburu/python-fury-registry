from fury_registry.client import EPP
from fury_registry.handlers import ContactHandler
from fury_registry.objects import EppContact


def test_parse_contact():
    """Parse contact info response"""
    contact_info = """
    <epp xmlns="urn:ietf:params:xml:ns:epp-1.0" xmlns:contact="urn:ietf:params:xml:ns:contact-1.0">
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
    </epp>"""
    response = EPP._parse_response(contact_info)
    contact = EppContact.from_xml(response.resData, response.extension)
    assert contact.handle == "WAL002352-NLCOM"
    assert contact.name == "S.J. de Wal"


def test_parse_contact_avail():
    """Handle avail response for contacts."""
    avail_response = """<epp xmlns="urn:ietf:params:xml:ns:epp-1.0" xmlns:contact="urn:ietf:params:xml:ns:contact-1.0">
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
    </epp>"""
    response = EPP._parse_response(avail_response)
    is_available = ContactHandler._parse_avail(response)
    assert not is_available
