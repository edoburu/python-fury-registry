from __future__ import unicode_literals
from . import contact

# EPP: https://tools.ietf.org/html/rfc5730
#
# clTRID = client transaction id

available = """<?xml version="1.0" encoding="UTF-8"?>
<epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
  <command>
    <check>
      <domain:check xmlns:domain="urn:ietf:params:xml:ns:domain-1.0">
        <domain:name>%s</domain:name>
      </domain:check>
    </check>
  </command>
</epp>"""

create = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
  <command>
    <create>
      <domain:create  xmlns:domain="urn:ietf:params:xml:ns:domain-1.0">
        <domain:name>%(domain)s</domain:name>
        <domain:ns>
          <domain:hostObj>%(ns)s</domain:hostObj>
        </domain:ns>
        <domain:registrant>%(registrant)s</domain:registrant>
        <domain:contact type="admin">%(admin)s</domain:contact>
        <domain:contact type="tech">%(tech)s</domain:contact>
        <domain:authInfo>
          <domain:pw>unused</domain:pw>
        </domain:authInfo>
      </domain:create>
    </create>
    <clTRID>ABC-12345</clTRID>
  </command>
</epp>"""

canceldelete = """<?xml version="1.0" encoding="UTF-8"?>
<epp xmlns="urn:ietf:params:xml:ns:epp-1.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:domain="urn:ietf:params:xml:ns:domain-1.0">
  <extension>
    <sidn-ext-epp:command xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:sidn-ext-epp="http://rxsd.domain-registry.nl/sidn-ext-epp-1.0">
      <sidn-ext-epp:domainCancelDelete>
        <sidn-ext-epp:name>%s</sidn-ext-epp:name>
      </sidn-ext-epp:domainCancelDelete>
      <sidn-ext-epp:clTRID>ABC-12345</sidn-ext-epp:clTRID>
    </sidn-ext-epp:command>
  </extension>
</epp>"""

delete = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
 <epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
   <command>
     <delete>
       <domain:delete xmlns:domain="urn:ietf:params:xml:ns:domain-1.0">
         <domain:name>%s</domain:name>
       </domain:delete>
     </delete>
     <clTRID>ABC-12345</clTRID>
   </command>
 </epp>"""

info = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
  <command>
    <info>
      <domain:info xmlns:domain="urn:ietf:params:xml:ns:domain-1.0">
        <domain:name hosts="all">%s</domain:name>
      </domain:info>
    </info>
    <clTRID>ABC-12345</clTRID>
  </command>
</epp>"""

login = """<?xml version="1.0" encoding="UTF-8"?>
<epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
  <command>
    <login>
      <clID>%(user)s</clID>
      <pw>%(pass)s</pw>
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

logout = """<?xml version="1.0" encoding="UTF-8"?>
<epp xmlns="urn:ietf:params:xml:ns:epp-1.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="urn:ietf:params:xml:ns:epp-1.0 epp-1.0.xsd">
  <command>
    <logout/>
  </command>
</epp>"""

nameserver = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
  <command>
    <info>
      <host:info xmlns:host="urn:ietf:params:xml:ns:host-1.0">
        <host:name>%s</host:name>
      </host:info>
    </info>
    <clTRID>ABC-12345</clTRID>
  </command>
</epp>"""

poll = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
  <command>
    <poll op="req"/>
    <clTRID>ABC-12345</clTRID>
  </command>
</epp>"""

transfer = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
  <command>
    <transfer op="request">
      <domain:transfer
       xmlns:domain="urn:ietf:params:xml:ns:domain-1.0">
        <domain:name>%(domain)s</domain:name>
        <domain:authInfo>
          <domain:pw>%(token)s</domain:pw>
        </domain:authInfo>
      </domain:transfer>
    </transfer>
    <clTRID>ABC-12345</clTRID>
  </command>
</epp>"""

transferstatus = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
  <command>
    <transfer op="query">
      <domain:transfer xmlns:domain="urn:ietf:params:xml:ns:domain-1.0">
        <domain:name>%s</domain:name>
      </domain:transfer>
    </transfer>
    <clTRID>ABC-12345</clTRID>
  </command>
</epp>"""
