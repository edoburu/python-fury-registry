import pytest

from fury_registry.client import EPP, EPPError


def test_parse_epp_error_ext():
    """Make sure EPP errors are handled, and extensions are read."""
    response = """
    <epp xmlns="urn:ietf:params:xml:ns:epp-1.0" xmlns:fury="urn:ietf:params:xml:ns:fury-2.1">
        <response>
            <result code="2308">
                <msg>Validation of the transaction failed.</msg>
            </result>
            <extValue>
                <value>
                    <fury:ciraCode>8001</fury:ciraCode>
                </value>
                <reason>Invalid domain name format.</reason>
            </extValue>
            <trID>
                <clTRID>unused</clTRID>
                <svTRID>AB95B312-96C6-A2C8-C174-A250A960D016</svTRID>
            </trID>
        </response>
    </epp>"""
    with pytest.raises(EPPError, match="Invalid domain name format.") as exc:
        EPP._parse_response(response)

    assert exc.value.message == "Validation of the transaction failed."
    assert exc.value.ext_code == "8001"
    assert exc.value.ext_reason == "Invalid domain name format."
