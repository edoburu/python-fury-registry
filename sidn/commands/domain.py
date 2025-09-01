from datetime import date, datetime

import idna
from sidn.utils import escape, xml_format


def _idna_encode(name):
    # Make sure the object is returned as string in Python 3
    return idna.encode(name).decode()


def info_part(name):
    xml = """
      <domain:info xmlns:domain="urn:ietf:params:xml:ns:domain-1.0">
        <domain:name hosts="all">{name}</domain:name>
      </domain:info>"""
    return xml_format(xml, name=_idna_encode(name))


def check_part(name):
    # Note that the <domain:name> may be repeated in EPP to check multiple objects at once.
    xml = """
      <domain:check xmlns:domain="urn:ietf:params:xml:ns:domain-1.0">
        <domain:name>{name}</domain:name>
      </domain:check>"""
    return xml_format(xml, name=_idna_encode(name))


def renew_part(name, curExpDate, period, unit):
    # Note that the <domain:name> may be repeated in EPP to check multiple objects at once.
    xml = """
      <domain:renew xmlns:domain="urn:ietf:params:xml:ns:domain-1.0">
        <domain:name>{name}</domain:name>
        <domain:curExpDate>{curExpDate}</domain:curExpDate>
        <domain:period unit="{unit}">{period}</domain:period>
      </domain:renew>"""
    if curExpDate is None:
        curExpDate = date.today().strftime("%Y-%m-%d")  # e.g. registered today
    elif isinstance(curExpDate, (date, datetime)):
        curExpDate = curExpDate.strftime("%Y-%m-%d")
    return xml_format(xml, name=_idna_encode(name), curExpDate=curExpDate, period=str(int(period)), unit=unit)


def create_part(name, registrant, admin, tech, ns, pw='unused'):
    xml = xml_format("""
      <domain:create xmlns:domain="urn:ietf:params:xml:ns:domain-1.0">
        <domain:name>{name}</domain:name>""", name=_idna_encode(name))

    xml += _ns_list(ns)

    xml += xml_format("""
        <domain:registrant>{registrant}</domain:registrant>
        <domain:contact type="admin">{admin}</domain:contact>
        <domain:contact type="tech">{tech}</domain:contact>
        <domain:authInfo>
          <domain:pw>{pw}</domain:pw>
        </domain:authInfo>
      </domain:create>""", registrant=registrant, admin=admin, tech=tech, pw=pw)

    return xml


def update_part(name, registrant=None, pw=None, remove_ns=(), remove_admins=(), remove_techs=(), remove_statuses=(), add_ns=(), add_admins=(), add_techs=(), add_statuses=()):
    xml = xml_format("""
      <domain:update xmlns:domain="urn:ietf:params:xml:ns:domain-1.0">
        <domain:name>{name}</domain:name>""", name=_idna_encode(name))

    if add_ns or add_admins or add_techs or add_statuses:
        xml += """
        <domain:add>"""

        if add_ns:
            xml += _ns_list(add_ns)

        for admin in add_admins:
            xml += xml_format("""
          <domain:contact type="admin">{admin}</domain:contact>""", admin=admin)

        for tech in add_techs:
            xml += xml_format("""
          <domain:contact type="tech">{tech}</domain:contact>""", tech=tech)

        for status in add_statuses:
            xml += xml_format("""
          <domain:status>{status}</domain:status>""", status=status)

        xml += """
        </domain:add>"""

    if remove_ns or remove_admins or remove_techs or remove_statuses:
        xml += """
        <domain:rem>"""

        if remove_ns:
            xml += _ns_list(remove_ns)

        for admin in remove_admins:
            xml += xml_format("""
          <domain:contact type="admin">{admin}</domain:contact>""", admin=admin)

        for tech in remove_techs:
            xml += xml_format("""
          <domain:contact type="tech">{tech}</domain:contact>""", tech=tech)

        for status in remove_statuses:
            xml += xml_format("""
          <domain:status>{status}</domain:status>""", status=status)

        xml += """
        </domain:rem>"""

    if registrant is not None or pw is not None:
        xml += """
        <domain:chg>"""

        if registrant is not None:
            xml += xml_format("""
          <domain:registrant>{registrant}</domain:registrant>""", registrant=registrant)

        if pw is not None:
            xml += xml_format("""
          <domain:authInfo>
            <domain:pw>{pw}</domain:pw>
          </domain:authInfo>""", pw=pw)

        xml += """
        </domain:chg>"""

    xml += """
      </domain:update>"""
    return xml


def _ns_list(ns):
    """
    Produce a list of nameservers.
    """
    xml = ''
    xml += """
          <domain:ns>"""

    for host in ns:
        xml += """
            <domain:hostObj>{ns}</domain:hostObj>""".format(ns=escape(host))

    xml += """
          </domain:ns>"""

    return xml


def transfer_req_part(name, token):
    xml = """
      <domain:transfer xmlns:domain="urn:ietf:params:xml:ns:domain-1.0">
        <domain:name>{name}</domain:name>
        <domain:authInfo>
          <domain:pw>{pw}</domain:pw>
        </domain:authInfo>
      </domain:transfer>"""
    return xml_format(xml, name=_idna_encode(name), pw=token)


def transfer_query_part(name):
    # Needs op="query"
    xml = """
      <domain:transfer xmlns:domain="urn:ietf:params:xml:ns:domain-1.0">
        <domain:name>{name}</domain:name>
      </domain:transfer>"""
    return xml_format(xml, name=_idna_encode(name))


def cancel_delete_part(name, clTRID=None):
    xml = """
      <sidn-ext-epp:command xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:sidn-ext-epp="http://rxsd.domain-registry.nl/sidn-ext-epp-1.0">
        <sidn-ext-epp:domainCancelDelete>
          <sidn-ext-epp:name>{name}</sidn-ext-epp:name>
        </sidn-ext-epp:domainCancelDelete>
        <sidn-ext-epp:clTRID>{clTRID}</sidn-ext-epp:clTRID>
      </sidn-ext-epp:command>"""

    # No command, only extension bit.
    return xml_format(xml, name=_idna_encode(name), clTRID=clTRID or 'unused')


def delete_part(name):
    xml = """
      <domain:delete xmlns:domain="urn:ietf:params:xml:ns:domain-1.0">
        <domain:name>{name}</domain:name>
      </domain:delete>"""
    return xml_format(xml, name=_idna_encode(name))
