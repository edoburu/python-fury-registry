from datetime import date, datetime

import idna

from fury_registry.utils import escape, xml_format

PRIVATE = {"admin": "agreed2", "tech": "agreed2"}  # TODO: frozendict() in Python 3.15

def _idna_encode(name):
    # Make sure the object is returned as string in Python 3
    return idna.encode(name).decode()


def info_part(name, password="unused"):
    xml = """
      <domain:info xmlns:domain="urn:ietf:params:xml:ns:domain-1.0">
        <domain:name hosts="all">{name}</domain:name>
        <domain:authInfo>
          <domain:pw>{password}</domain:pw>
        </domain:authInfo>
      </domain:info>"""
    return xml_format(xml, name=_idna_encode(name), password=password)


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


def create_part(name, ns, registrant="agreed2", contacts=PRIVATE, pw='unused'):
    """Use admin/tech/ns="agreed2" to create the privacy domain."""
    xml = xml_format("""
      <domain:create xmlns:domain="urn:ietf:params:xml:ns:domain-1.0">
        <domain:name>{name}</domain:name>
        <domain:period unit="y">1</domain:period>""", name=_idna_encode(name))

    xml += _ns_list(ns)

    xml += xml_format("""
        <domain:registrant>{registrant}</domain:registrant>""", registrant=registrant)

    for key, value in contacts.items():
        xml += xml_format("""
            <domain:contact type="admin">{admin}</domain:contact>""", key=key, value=value)

    xml += xml_format("""
        <domain:authInfo>
          <domain:pw>{pw}</domain:pw>
        </domain:authInfo>
      </domain:create>""", pw=pw)

    return xml


def update_part(name, registrant=None, pw=None, remove_ns=(), remove_contacts=None, remove_statuses=(), add_ns=(), add_contacts=(), add_statuses=()):
    xml = xml_format("""
      <domain:update xmlns:domain="urn:ietf:params:xml:ns:domain-1.0">
        <domain:name>{name}</domain:name>""", name=_idna_encode(name))
    
    changed = True

    if add_ns or add_contacts or add_statuses:
        xml += """
        <domain:add>"""

        if add_ns:
            xml += _ns_list(add_ns)

        if add_contacts:
            for kind, handle in add_contacts.items():
                xml += xml_format("""
              <domain:contact type="{kind}">{handle}</domain:contact>""", kind=kind, handle=handle)

        for status in add_statuses:
            xml += xml_format("""
          <domain:status>{status}</domain:status>""", status=status)

        xml += """
        </domain:add>"""
        changed = True

    if remove_ns or remove_contacts or remove_statuses:
        xml += """
        <domain:rem>"""

        if remove_ns:
            xml += _ns_list(remove_ns)

        if remove_contacts:
            for kind, handle in remove_contacts:
                xml += xml_format("""
              <domain:contact type="{kind}">{handle}</domain:contact>""", kind=kind, handle=handle)

        for status in remove_statuses:
            xml += xml_format("""
          <domain:status>{status}</domain:status>""", status=status)

        xml += """
        </domain:rem>"""
        changed = True

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
        changed = True

    if not changed:
        # For restore delete action
        xml += "        <domain:chg/>"

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
        xml += f"""
            <domain:hostObj>{escape(host)}</domain:hostObj>"""

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


def restore_part(op="request"):
    """
    :param op: Either "request or "report"
    """
    return xml_format("""
      <rgp:update xmlns:rgp="urn:ietf:params:xml:ns:rgp-1.0">
        <rgp:restore op="{op}"/>
      </rgp:update>""", op=op)


def delete_part(name):
    xml = """
      <domain:delete xmlns:domain="urn:ietf:params:xml:ns:domain-1.0">
        <domain:name>{name}</domain:name>
      </domain:delete>"""
    return xml_format(xml, name=_idna_encode(name))
