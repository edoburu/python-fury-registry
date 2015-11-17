from __future__ import unicode_literals
from sidn.utils import xml_format

# EPP: https://tools.ietf.org/html/rfc5730
#
# clTRID = client transaction id

generic = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
  <command>
    <{command}>{contents}</{command}>
    <clTRID>{clTRID}</clTRID>
  </command>
</epp>"""

check = """<?xml version="1.0" encoding="UTF-8"?>
<epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
  <command>
    <check>{0}</check>
  </command>
</epp>"""

def login(username, password):
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
  <command>
    <login>
      <clID>{username}</clID>
      <pw>{password}</pw>
      <options>
        <version>1.0</version>
        <lang>en</lang>
      </options>
      <svcs>
        <objURI>urn:ietf:params:xml:ns:contact-1.0</objURI>
        <objURI>urn:ietf:params:xml:ns:host-1.0</objURI>
        <objURI>urn:ietf:params:xml:ns:domain-1.0</objURI>
        <svcExtension>
          <extURI>urn:ietf:params:xml:ns:sidn-ext-epp-1.0</extURI>
        </svcExtension>
      </svcs>
    </login>
  </command>
</epp>"""
    return xml_format(xml, username=username, password=password)

logout = """<?xml version="1.0" encoding="UTF-8"?>
<epp xmlns="urn:ietf:params:xml:ns:epp-1.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="urn:ietf:params:xml:ns:epp-1.0 epp-1.0.xsd">
  <command>
    <logout/>
  </command>
</epp>"""

def poll(transaction_id=None):
    xml  = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
    <epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
      <command>
        <poll op="req"/>
        <clTRID>{clTRID}</clTRID>
      </command>
    </epp>"""
    return xml_format(xml, clTRID=transaction_id or 'unused')
