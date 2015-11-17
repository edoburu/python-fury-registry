from __future__ import unicode_literals
import re
from .xml import xml_format

RE_PHONE_START = re.compile(r'^(?P<prefix>\+|0+)(?P<country>[0-9]{1,2})[- .]')
RE_PHONE = re.compile("^(\+[0-9]{1,3}\.[0-9]{1,14})?$")


def check_part(handle):
    xml = """
      <contact:check xmlns:contact="urn:ietf:params:xml:ns:contact-1.0">
        <contact:id>{handle}</contact:id>
      </contact:check>
"""
    return xml_format(xml, handle=handle)


def create(**data):
    xml = """<?xml version='1.0' encoding='UTF-8' standalone='no'?>
<epp xmlns="urn:ietf:params:xml:ns:epp-1.0" xmlns:sidn-ext-epp="http://rxsd.domain-registry.nl/sidn-ext-epp-1.0">
  <command>
    <create>
      <contact:create xmlns:contact="urn:ietf:params:xml:ns:contact-1.0">
        <contact:id>{handle}</contact:id>"""

    xml += _contact_info(**data)

    xml += """
      </contact:create>
    </create>"""

    xml += _contact_ext(**data)
    xml += """
    <clTRID>ABC-12345</clTRID>
  </command>
</epp>"""

    return xml_format(xml, **data)


def info_part(handle):
    xml = """
      <contact:info xmlns:contact="urn:ietf:params:xml:ns:contact-1.0">
        <contact:id>%(handle)s</contact:id>
      </contact:info>
"""
    return xml_format(xml, handle=handle)


def update_part(**data):
    """
    Update an contact.
    """
    xml = """
    <contact:update xmlns:contact="urn:ietf:params:xml:ns:contact-1.0">
      <contact:id>{handle}</contact:id>
        <contact:chg>"""

    xml += _contact_info(**data)   # TODO: only add included fields?
    xml += """
        </contact:chg>   
      </contact:update>
    </update>"""

    xml += _contact_ext(**data)
    return xml_format(xml, **data)


def _contact_info(**data):
    if data.get('voice', None):
        data['voice'] = _fix_phone(data['voice'])
    if data.get('fax', None):
        data['fax'] = _fix_phone(data['fax'])

    # DRS5 note: only unrestricted utf-8 is allowed, not 7-bit US-ASCII
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
    return xml_format(xml, **data)


def _contact_ext(**data):
    xml = """
    <extension>
      <sidn-ext-epp:ext>
        <sidn-ext-epp:create>
          <sidn-ext-epp:contact>"""

    if data.get('legalForm', None):
      xml += """
            <sidn-ext-epp:legalForm>{legalForm}</sidn-ext-epp:legalForm>
            <sidn-ext-epp:legalFormRegNo>{legalFormRegNo}</sidn-ext-epp:legalFormRegNo>"""

    xml += """
          </sidn-ext-epp:contact>
        </sidn-ext-epp:create>
      </sidn-ext-epp:ext>
    </extension>"""
    return xml_format(xml, **data)


def _fix_phone(value):
    # A fax or phone number is a string that starts with a '+', followed by the country code, followed by a '.'
    # and then followed by a series of numbers being the fax or telephone.
    value = RE_PHONE_START.sub('+\g<country>.', value)
    value = value.replace(' ', '').replace('-', '')
    assert RE_PHONE.match(value)
    return value
