from __future__ import unicode_literals
from sidn.utils import xml_format, escape


def info_part(name):
    xml = """
      <domain:info xmlns:domain="urn:ietf:params:xml:ns:domain-1.0">
        <domain:name hosts="all">{name}</domain:name>
      </domain:info>"""
    return xml_format(xml, name=name)


def check_part(name):
    xml = """
      <domain:check xmlns:domain="urn:ietf:params:xml:ns:domain-1.0">
        <domain:name>{name}</domain:name>
      </domain:check>"""
    return xml_format(xml, name=name)


def create_part(name, registrant, admin, tech, ns, pw='unused'):
    xml = """
      <domain:create xmlns:domain="urn:ietf:params:xml:ns:domain-1.0">
        <domain:name>{name}</domain:name>
        <domain:ns>"""

    for host in ns:
        xml += """
          <domain:hostObj>{ns}</domain:hostObj>""".format(ns=escape(host))

    xml += """
        </domain:ns>
        <domain:registrant>{registrant}</domain:registrant>
        <domain:contact type="admin">{admin}</domain:contact>
        <domain:contact type="tech">{tech}</domain:contact>
        <domain:authInfo>
          <domain:pw>{pw}</domain:pw>
        </domain:authInfo>
      </domain:create>"""
    return xml_format(
        xml,
        name=name,
        registrant=registrant,
        admin=admin,
        tech=tech,
        pw=pw,
    )


def transfer(name, token, clTRID=None):
    xml = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
  <command>
    <transfer op="request">
      <domain:transfer xmlns:domain="urn:ietf:params:xml:ns:domain-1.0">
        <domain:name>{name}</domain:name>
        <domain:authInfo>
          <domain:pw>{pw}</domain:pw>
        </domain:authInfo>
      </domain:transfer>
    </transfer>
    <clTRID>{clTRID}</clTRID>
  </command>
</epp>"""
    return xml_format(xml, name=name, pw=token, clTRID=clTRID or 'unused')


def transfer_status(name, clTRID=None):
    # Difference is op="query"
    xml = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
  <command>
    <transfer op="query">
      <domain:transfer xmlns:domain="urn:ietf:params:xml:ns:domain-1.0">
        <domain:name>{name}</domain:name>
      </domain:transfer>
    </transfer>
    <clTRID>{clTRID}</clTRID>
  </command>
</epp>"""
    return xml_format(xml, name=name, clTRID=clTRID or 'unused')


def cancel_delete(name, clTRID=None):
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<epp xmlns="urn:ietf:params:xml:ns:epp-1.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:domain="urn:ietf:params:xml:ns:domain-1.0">
  <extension>
    <sidn-ext-epp:command xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:sidn-ext-epp="http://rxsd.domain-registry.nl/sidn-ext-epp-1.0">
      <sidn-ext-epp:domainCancelDelete>
        <sidn-ext-epp:name>{name}</sidn-ext-epp:name>
      </sidn-ext-epp:domainCancelDelete>
      <sidn-ext-epp:clTRID>{clTRID}</sidn-ext-epp:clTRID>
    </sidn-ext-epp:command>
  </extension>
</epp>"""
    return xml_format(xml, name=name, clTRID=clTRID or 'unused')

def delete_part(name):
    xml = """
      <domain:delete xmlns:domain="urn:ietf:params:xml:ns:domain-1.0">
        <domain:name>%s</domain:name>
      </domain:delete>"""
    return xml_format(xml, name=name)
