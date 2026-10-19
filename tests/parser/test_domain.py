from copy import copy

from fury_registry.client import EPP
from fury_registry.objects import FuryDomain, KeyData


def test_parse_domain():
    """Parse domain info response."""
    domain_info = """
    <epp xmlns="urn:ietf:params:xml:ns:epp-1.0" xmlns:domain="urn:ietf:params:xml:ns:domain-1.0" xmlns:secDNS="urn:ietf:params:xml:ns:secDNS-1.1">
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
    </epp>"""
    response = EPP._parse_response(domain_info)
    domain = FuryDomain.from_xml(response.resData, response.extension)
    assert domain.name == "computel.nl"
    assert domain.ns == ["ns2.computel.nl", "ns1.computel.nl"]
    assert domain.admin == "COM017325-NLCOM"
    assert domain.tech == "WAL002352-NLCOM"
    assert domain.dnssec.keydatas[0].alg == KeyData.ALG_SHA256
    assert domain.dnssec.keydatas[0].protocol == KeyData.PROTOCOL3
    assert domain.dnssec.keydatas[0].flags == KeyData.FLAG_KSK
    assert domain.dnssec.keydatas[0].pubKey.startswith("AwEAAao2zeD")
    assert domain.rgp_status_end.isoformat() == "2020-12-28T22:00:00+00:00"
    dnssec = domain.dnssec
    assert copy(dnssec.keydatas[0]) in domain.dnssec
