from __future__ import unicode_literals
from xml.sax.saxutils import escape
import re

RE_PHONE_START = re.compile(r'^(?P<prefix>\+|0+)(?P<country>[0-9]{1,2})[- .]')
RE_PHONE = re.compile("^(\+[0-9]{1,3}\.[0-9]{1,14})?$")

available = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
  <command>
    <check>
      <contact:check xmlns:contact="urn:ietf:params:xml:ns:contact-1.0">
        <contact:id>%(handle)s</contact:id>
      </contact:check> 
     </check>
    <clTRID>ABC-12345</clTRID>
  </command>
</epp>"""


def create(data):
    xml = """<?xml version='1.0' encoding='UTF-8' standalone='no'?>
<epp xmlns="urn:ietf:params:xml:ns:epp-1.0" xmlns:sidn-ext-epp="http://rxsd.domain-registry.nl/sidn-ext-epp-1.0">
  <command>
    <create>
      <contact:create xmlns:contact="urn:ietf:params:xml:ns:contact-1.0">
        <contact:id>{handle}</contact:id>"""

    xml += _contact_info(data)

    xml += """
      </contact:create>
    </create>"""

    xml += _contact_ext(data)
    xml += """
    <clTRID>ABC-12345</clTRID>
  </command>
</epp>"""

    return _xml_format(xml, data)

info = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
  <command>
    <info>
      <contact:info xmlns:contact="urn:ietf:params:xml:ns:contact-1.0">
        <contact:id>%(handle)s</contact:id>
      </contact:info>
    </info>
    <clTRID>ABC-12345</clTRID>
  </command>
</epp>"""


def update(data):
    """
    Update an contact.
    """
    xml = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
  <command>
    <update>
    <contact:update xmlns:contact="urn:ietf:params:xml:ns:contact-1.0">
      <contact:id>{handle}</contact:id>
        <contact:chg>"""

    xml += _contact_info(data)   # TODO: only add included fields?
    xml += """
        </contact:chg>   
      </contact:update>
    </update>"""

    xml += _contact_ext(data)
    xml += """
    <clTRID>ABC-12345</clTRID>
  </command>
</epp>"""

    return _xml_format(xml, data)


def _contact_info(data):
    if 'voice' in data:
        data['voice'] = _fix_phone(data['voice'])
    if 'fax' in data:
        data['fax'] = _fix_phone(data['fax'])

    xml = """
        <contact:postalInfo type="loc">
          <contact:name>{name}</contact:name>
          <contact:org>{org}</contact:org>
          <contact:addr>
            <contact:street>{street}</contact:street>
            <contact:city>{city}</contact:city>
            <contact:pc>{pc}</contact:pc>
            <contact:cc>{cc}</contact:cc>
          </contact:addr>
        </contact:postalInfo>
        <contact:voice>{voice}</contact:voice>
        <contact:fax>{fax}</contact:fax>
        <contact:email>{email}</contact:email>
        <contact:authInfo>
          <contact:pw>unused</contact:pw>
        </contact:authInfo>"""
    return _xml_format(xml, data)

def _contact_ext(data):
    xml = """
    <extension>
      <sidn-ext-epp:ext>
        <sidn-ext-epp:create>
          <sidn-ext-epp:contact>"""

    if 'legalForm' in data:
      xml += """
            <sidn-ext-epp:legalForm>{legalForm}</sidn-ext-epp:legalForm>
            <sidn-ext-epp:legalFormRegNo>{legalFormRegNo}</sidn-ext-epp:legalFormRegNo>"""

    xml += """
          </sidn-ext-epp:contact>
        </sidn-ext-epp:create>
      </sidn-ext-epp:ext>
    </extension>"""
    return _xml_format(xml, data)


def _fix_phone(value):
    # A fax or phone number is a string that starts with a '+', followed by the country code, followed by a '.'
    # and then followed by a series of numbers being the fax or telephone.
    value = RE_PHONE_START.sub('+\g<country>.', value)
    value = value.replace(' ', '').replace('-', '')
    assert RE_PHONE.match(value)
    return value


def _xml_format(xml, data):
    data = _xml_escape(data)
    return xml.format(**data)

def _xml_escape(data):
    return dict((k, escape(v)) for k, v in data.iteritems())
