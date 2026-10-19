"""
Serialize DNSSec objects to EPP XML
"""
from __future__ import annotations

from collections.abc import Iterable

from fury_registry.objects import DSKey, KeyData
from fury_registry.utils import xml_format


def create(dskeys: Iterable[DSKey]=(), keyData: Iterable[KeyData]=()):
    """
    The DNSSec create extension
    """
    xml = """
          <secDNS:create xmlns:secDNS="urn:ietf:params:xml:ns:secDNS-1.1">"""

    # Not used by Hello/SIDN
    # if maxSigLife:
    #    xml += """
    #    <secDNS:maxSigLife>{0}</secDNS:maxSigLife>""".format(int(maxSigLife))

    # Can use either keys or keyData, but not both.
    if dskeys:
        for dskey in dskeys:
            xml += dskey_to_xml(dskey)
    elif keyData:
        for dskey in keyData:
            xml += keydata_to_xml(dskey)

    xml += """
          </secDNS:create>"""
    return xml


def update(remove_all=False, remove_dskeys=(), remove_keydatas=(), add_dskeys=(), add_keydatas=(), urgent=False):
    if not remove_all and not remove_dskeys and not remove_keydatas and \
            not add_dskeys and not add_keydatas:
        raise ValueError("At least one DNSSec argument should be provided to update()!")

    urgent_attr = ''
    if urgent:
        urgent_attr = ' urgent="true"'

    xml = f"""
      <secDNS:update{urgent_attr} xmlns:secDNS="urn:ietf:params:xml:ns:secDNS-1.1">"""

    # the server MUST first remove the existing elements prior to adding the new elements.
    if remove_dskeys or remove_keydatas or remove_all:
        xml += """
        <secDNS:rem>"""

        if remove_all:
            xml += """
          <secDNS:all>true</secDNS:all>"""
        elif remove_dskeys:
            for key in remove_dskeys:
                xml += dskey_to_xml(key)
        else:
            for keydata in remove_keydatas:
                xml += keydata_to_xml(keydata)
        xml += """
        </secDNS:rem>"""

    if add_dskeys or add_keydatas:
        xml += """
        <secDNS:add>"""
        if add_dskeys:
            for key in add_dskeys:
                xml += dskey_to_xml(key)
        else:
            for keydata in add_keydatas:
                xml += keydata_to_xml(keydata)
        xml += """
        </secDNS:add>"""

    # Not used by Hello/SIDN
    # if maxSigLife:
    #    ext_xml += """
    #    <secDNS:chg>
    #      <secDNS:maxSigLife>{0}</secDNS:maxSigLife>
    #    </secDNS:chg>""".format(int(maxSigLife))

    xml += """
      </secDNS:update>"""
    return xml


def dskey_to_xml(dskey: DSKey):
    """
    :type dskey: fury_registry.objects.DSKey
    """
    # Delegation Signer key information
    xml = """
          <secDNS:dsData>
            <secDNS:keyTag>{keyTag}</secDNS:keyTag>
            <secDNS:alg>{alg}</secDNS:alg>
            <secDNS:digestType>{digestType}</secDNS:digestType>
            <secDNS:digest>{digest}</secDNS:digest>"""

    xml = xml_format(
        xml,
        keyTag=dskey.keyTag,
        alg=dskey.alg,
        digestType=dskey.digestType,
        digest=dskey.digest,
    )

    for keyData in dskey.keyData:
        xml += keydata_to_xml(keyData)

    xml += """
          </secDNS:dsData>"""
    return xml


def keydata_to_xml(keyData: KeyData):
    """
    :type keyData: fury_registry.objects.KeyData
    """
    # Client key information
    xml = """
            <secDNS:keyData>
              <secDNS:flags>{flags}</secDNS:flags>
              <secDNS:protocol>{protocol}</secDNS:protocol>
              <secDNS:alg>{alg}</secDNS:alg>
              <secDNS:pubKey>{pubKey}</secDNS:pubKey>
            </secDNS:keyData>"""
    return xml_format(
        xml,
        flags=keyData.flags,
        protocol=keyData.protocol,
        alg=keyData.alg,
        pubKey=keyData.pubKey
    )
