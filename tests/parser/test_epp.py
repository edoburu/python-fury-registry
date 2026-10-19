from fury_registry import EPP


def test_parse_greeting():
    """Parse the greeting response"""
    greeting = """<?xml version="1.0" encoding="UTF-8"?>
<epp xmlns="urn:ietf:params:xml:ns:epp-1.0" xmlns:fury="urn:ietf:params:xml:ns:fury-1.0" xmlns:droplist="urn:ietf:params:xml:ns:droplist-1.0" xmlns:idn="urn:ietf:params:xml:ns:idn-1.0" xmlns:host="urn:ietf:params:xml:ns:host-1.0" xmlns:contact="urn:ietf:params:xml:ns:contact-1.0" xmlns:domain="urn:ietf:params:xml:ns:domain-1.0" xmlns:secDNS="urn:ietf:params:xml:ns:secDNS-1.1" xmlns:launch="urn:ietf:params:xml:ns:launch-1.0" xmlns:mark="urn:ietf:params:xml:ns:mark-1.0" xmlns:smd="urn:ietf:params:xml:ns:signedMark-1.0" xmlns:ds="http://www.w3.org/2000/09/xmldsig#" xmlns:rgp="urn:ietf:params:xml:ns:rgp-1.0" xmlns:fee="urn:ietf:params:xml:ns:fee-0.11">
    <greeting>
        <svID>Version: 10.3</svID>
        <svDate>2026-10-19T14:11:40.813Z</svDate>
        <svcMenu>
            <version>1.0</version>
            <lang>fr</lang>
            <lang>en</lang>
            <objURI>urn:ietf:params:xml:ns:domain-1.0</objURI>
            <objURI>urn:ietf:params:xml:ns:contact-1.0</objURI>
            <objURI>urn:ietf:params:xml:ns:host-1.0</objURI>
            <svcExtension>
                <extURI>urn:ietf:params:xml:ns:rgp-1.0</extURI>
                <extURI>urn:ietf:params:xml:ns:fury-1.0</extURI>
                <extURI>urn:ietf:params:xml:ns:fury-2.0</extURI>
                <extURI>urn:ietf:params:xml:ns:fury-2.1</extURI>
                <extURI>urn:ietf:params:xml:ns:droplist-1.0</extURI>
                <extURI>urn:ietf:params:xml:ns:fury-rgp-1.0</extURI>
                <extURI>urn:ietf:params:xml:ns:idn-1.0</extURI>
                <extURI>urn:ietf:params:xml:ns:secDNS-1.1</extURI>
                <extURI>urn:ietf:params:xml:ns:launch-1.0</extURI>
                <extURI>urn:ietf:params:xml:ns:mark-1.0</extURI>
                <extURI>urn:ietf:params:xml:ns:signedMark-1.0</extURI>
                <extURI>urn:ietf:params:xml:ns:epp:fee-1.0</extURI>
                <extURI>urn:ietf:params:xml:ns:fee-0.11</extURI>
                <extURI>urn:ietf:params:xml:ns:fee-0.9</extURI>
                <extURI>http://www.w3.org/2000/09/xmldsig#</extURI>
                <extURI>urn:ietf:params:xml:ns:epp:org-1.0</extURI>
                <extURI>urn:ietf:params:xml:ns:epp:orgext-1.0</extURI>
            </svcExtension>
        </svcMenu>
        <dcp>
            <access>
                <none/>
            </access>
            <statement>
                <purpose>
                    <admin/>
                </purpose>
                <recipient>
                    <ours/>
                </recipient>
                <retention>
                    <legal/>
                </retention>
            </statement>
        </dcp>
    </greeting>
</epp>"""
    svid, version = EPP._parse_greeting(greeting)
    assert svid == "Version: 10.3"
    assert version == "1.0"


def test_parse_logout():
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<epp xmlns="urn:ietf:params:xml:ns:epp-1.0" xmlns:host="urn:ietf:params:xml:ns:host-1.0" xmlns:contact="urn:ietf:params:xml:ns:contact-1.0" xmlns:domain="urn:ietf:params:xml:ns:domain-1.0" xmlns:rgp="urn:ietf:params:xml:ns:rgp-1.0" xmlns:fury="urn:ietf:params:xml:ns:fury-2.0" xmlns:fury-rgp="urn:ietf:params:xml:ns:fury-rgp-1.0" xmlns:idn="urn:ietf:params:xml:ns:idn-1.0" xmlns:secDNS="urn:ietf:params:xml:ns:secDNS-1.1" xmlns:launch="urn:ietf:params:xml:ns:launch-1.0" xmlns:mark="urn:ietf:params:xml:ns:mark-1.0" xmlns:smd="urn:ietf:params:xml:ns:signedMark-1.0" xmlns:ds="http://www.w3.org/2000/09/xmldsig#" xmlns:fee="urn:ietf:params:xml:ns:fee-0.11" xmlns:org="urn:ietf:params:xml:ns:epp:org-1.0" xmlns:orgext="urn:ietf:params:xml:ns:epp:orgext-1.0">
    <response>
        <result code="1500">
            <msg>Command completed successfully; ending session</msg>
        </result>
        <trID>
            <svTRID>SIDN-000055308850-0000000002</svTRID>
        </trID>
    </response>
</epp>"""
    response = EPP._parse_response(xml)
    assert response.result_code == 1500
