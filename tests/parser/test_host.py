from datetime import UTC, datetime

from fury_registry import EPP
from fury_registry.objects import EppHost


def test_parse_host():
    raw_response = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
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
    </epp>"""
    response = EPP._parse_response(raw_response)
    host = EppHost.from_xml(response.resData, response.extension)
    assert host.name == "ns0.epp-example.co.uk."
    assert host.addr == ["123.123.123.123", "1080:0:0:0:8:800:200C:417B"]
    assert host.cl_id == "EXAMPLE_TAG"
    assert host.cr_id == "epp-user"
    assert host.created_date == datetime(2008, 6, 12, 6, 46, tzinfo=UTC)
