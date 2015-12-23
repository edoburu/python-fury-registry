from __future__ import unicode_literals
from sidn.utils import xml_format, escape


# EPP: https://tools.ietf.org/html/rfc5730
#
# clTRID = client transaction id


def build_command(command_name, command_xml=None, op=None, command_extensions=(), clTRID=None, epp_extensions=()):
    """
    Construct an EPP command from it's parts.

    :param command_name: The command to send, e.g. ``create``, ``info``, ``check``, ``delete``.
    :param command_xml: The XML contents of the command.
    :param op: Optional "op" attribute for the command.
    :param command_extensions: The XML contents for the ``<extension>`` block of the ``<command>``.
    :param clTRID: Optional client transaction ID, to recognize server responses (e.g. in polling).
    :param epp_extensions: The XML for the ``<extension>`` block at ``<epp>`` top level.
                           NOTE: the ``command_xml`` may also contain an ``<extension>`` block!
    """
    if command_name is None:
        # Only an <extension> at top-level. Used for SIDN domainCancelDelete
        main_xml = ''
    else:
        # Allow parts to pass an command + extension via a tuple
        command_ext = ''
        command_extensions = filter(None, command_extensions)
        if command_extensions:
            command_ext += (u"    <extension>{0}\n"
                            u"    </extension>\n").format("\n".join(command_extensions))

        main_xml = (
          "  <command>\n"
          "    <{command_name}{op_attr}>{command_xml}\n"
          "    </{command_name}>\n{ext}"
          "    <clTRID>{clTRID}</clTRID>\n"
          "  </command>\n").format(
            command_name=command_name,
            command_xml=command_xml or '',
            ext=command_ext,
            op_attr=' op="{0}"'.format(escape(op)) if op else '',
            clTRID=clTRID or 'unused',
        )

    extensions_xml = filter(None, epp_extensions)
    if extensions_xml:
        # Exceptions at top-level.
        # Note an <extension> block can also occur inside the command_xml.
        main_xml += ("  <extension>{0}\n"
                     "  </extension>\n").format("\n".join(extensions_xml))

    return """<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n""" \
           """<epp xmlns="urn:ietf:params:xml:ns:epp-1.0">\n{main_xml}</epp>""".format(
            main_xml=main_xml
    )


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


def poll(op='req', transaction_id=None):
    xml  = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
    <epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
      <command>
        <poll op="{op}"/>
        <clTRID>{clTRID}</clTRID>
      </command>
    </epp>"""
    return xml_format(xml, op=op, clTRID=transaction_id or 'unused')
