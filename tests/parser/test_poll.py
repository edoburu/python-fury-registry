from datetime import datetime

from dateutil.tz import tzutc

from fury_registry.client import EPP, EPPPollResponse
from fury_registry.constants import EPP_QUEUE_EMPTY, EPP_QUEUE_NOT_EMPTY
from fury_registry.utils import get_node_text

UTC = tzutc()


def test_parse_poll():
    """Test parsing for poll responses"""
    raw_response = """
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
    </epp>"""
    response = EPP._parse_response(raw_response, response_class=EPPPollResponse)
    assert response.result_code == EPP_QUEUE_NOT_EMPTY
    assert response.queue_count == 5
    assert response.queue_date == datetime(2000, 6, 8, 22, 0, 0, tzinfo=UTC)
    assert response.message == "Transfer requested."
    assert response.result_msg == "Command completed successfully; ack to dequeue"
    assert get_node_text(response.resData, "obj:trnData/obj:name") == "example.com"
    assert response.clTRID == "ABC-12345"
    assert response.svTRID == "54321-XYZ"
    assert bool(response)


def test_parse_poll_transfer_start():
    """Test the message that a poll returns."""
    raw_response = """<?xml version="1.0" encoding="utf-8"?>
    <epp xmlns="urn:ietf:params:xml:ns:epp-1.0"
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
                <clTRID>900398-1265880242</clTRID>
                <svTRID>C54BF9AD-907C-4C5C-F791-AE0CB997716E</svTRID>
            </trID>
        </response>
    </epp>"""
    response: EPPPollResponse = EPP._parse_response(
        raw_response,
        response_class=EPPPollResponse,
    )
    assert response.result_code == EPP_QUEUE_NOT_EMPTY
    assert response.trnData.name == "for-transfer-03.nl"
    assert response.trnData.status == "pending"


def test_parse_poll_transfer():
    """Test poll notification that a transfer was completed."""
    raw_response = """<?xml version="1.0" encoding="UTF-8"?>
    <epp xmlns="urn:ietf:params:xml:ns:epp-1.0" xmlns:domain="urn:ietf:params:xml:ns:domain-1.0">
        <response>
            <result code="1301">
                <msg>The message has been picked up. Please confirm receipt to remove the message from the queue.</msg>
            </result>
            <msgQ id="2260594" count="1">
                <qDate>2016-10-21T11:45:00.000Z</qDate>
                <msg>1016 Verhuizing domeinnaam for-transfer-05.nl verwerkt</msg>
            </msgQ>
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
                <clTRID>unused</clTRID>
                <svTRID>BF3075DF-05CD-2000-E2DC-126BB1758597</svTRID>
            </trID>
        </response>
    </epp>"""
    response = EPP._parse_response(raw_response, response_class=EPPPollResponse)
    assert response.result_code == EPP_QUEUE_NOT_EMPTY
    assert response.trnData.name == "for-transfer-05.nl"
    assert response.trnData.status == "serverApproved"
    assert response.trnData.request_id == "TRAIP"
    assert response.trnData.request_date == datetime(
        2016, 10, 21, 11, 44, 58, tzinfo=UTC
    )
    assert response.trnData.act_id == "NLCOM"
    assert response.trnData.act_date == datetime(
        2016, 10, 21, 11, 45, 0, 111000, tzinfo=UTC
    )
    assert bool(response)


def test_parse_empty_poll():
    """Handle nodes without msgQ element."""
    raw_response = """
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
    </epp>"""
    response = EPP._parse_response(raw_response, response_class=EPPPollResponse)
    assert response.result_code == EPP_QUEUE_EMPTY
    assert response.queue_count == 0
    assert response.queue_date == None
    assert response.queue_id == None
    assert response.result_msg == "There are no messages in the queue."
    assert not bool(response)
