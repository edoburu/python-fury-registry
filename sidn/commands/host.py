from __future__ import unicode_literals

from sidn.utils import escape, xml_format


def create_part(name, ipv4, ipv6):
    xml = xml_format("""
      <host:create xmlns:host="urn:ietf:params:xml:ns:host-1.0">
        <host:name>{name}</host:name>""", name=name)

    for addr in ipv4:
        xml += xml_format("""
        <host:addr ip="v4">{addr}</host:addr>""", addr=addr)

    for addr in ipv6:
        xml += xml_format("""
        <host:addr ip="v6">{addr}</host:addr>""", addr=addr)

    xml += """
      </host:create>"""

    return xml


def info_part(name):
    xml = """
      <host:info xmlns:host="urn:ietf:params:xml:ns:host-1.0">
        <host:name>{name}</host:name>
      </host:info>"""
    return xml_format(xml, name=name)


def delete_part(name):
    xml = """
      <host:delete xmlns:host="urn:ietf:params:xml:ns:host-1.0">
        <host:name>{name}</host:name>
      </host:delete>"""
    return xml_format(xml, name=name)
