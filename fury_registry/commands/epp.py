from typing import Iterable

from fury_registry.utils import escape, xml_format

# EPP: https://tools.ietf.org/html/rfc5730
#
# clTRID = client transaction id

LOGIN_EXTENSIONS = (
    # See constants.XMLNS for descriptions of these namespaces
    "urn:ietf:params:xml:ns:fury-2.1",
    "urn:ietf:params:xml:ns:fury-rgp-1.0",
    "urn:ietf:params:xml:ns:idn-1.0",
    "urn:ietf:params:xml:ns:secDNS-1.1",
    "urn:ietf:params:xml:ns:launch-1.0",
    "urn:ietf:params:xml:ns:mark-1.0",
    "urn:ietf:params:xml:ns:signedMark-1.0",
    "http://www.w3.org/2000/09/xmldsig#",
    "urn:ietf:params:xml:ns:rgp-1.0",
    "urn:ietf:params:xml:ns:fee-0.9",
    "urn:ietf:params:xml:ns:fee-0.11",
    "urn:ietf:params:xml:ns:epp:org-1.0",
    "urn:ietf:params:xml:ns:epp:orgext-1.0",
)


def build_command(
    command_name: str|None,
    command_xml: str|None=None,
    op: str|None=None,
    command_extensions: Iterable[str]=(),
    clTRID: str|None=None,
    epp_extensions: Iterable[str]=(),
):
    """Construct an EPP command from its parts.

    :param command_name: The command to send, e.g. ``create``, ``info``, ``check``, ``delete``.
    :param command_xml: The XML contents of the command.
    :param op: Optional "op" attribute for the command.
    :param command_extensions: The XML contents for the ``<extension>`` block of the ``<command>``.
    :param clTRID: Optional client transaction ID, to recognize server responses (e.g. in polling).
    :param epp_extensions: The XML for the ``<extension>`` block at ``<epp>`` top level.
                           NOTE: the ``command_xml`` may also contain an ``<extension>`` block!
    """
    if command_name is None:
        # Only an <extension> at top-level. Used for custom commands (e.g. request All Properties)
        main_xml = ""
    else:
        # Allow parts to pass an command + extension via a tuple
        command_ext = ""
        command_extensions = (
            list(filter(None, command_extensions)) if command_extensions else None
        )
        if command_extensions:
            command_ext += ("    <extension>{}\n    </extension>\n").format(
                "\n".join(command_extensions),
            )

        main_xml = (
            "  <command>\n"
            "    <{command_name}{op_attr}>{command_xml}\n"
            "    </{command_name}>\n{ext}"
            "    <clTRID>{clTRID}</clTRID>\n"
            "  </command>\n"
        ).format(
            command_name=command_name,
            command_xml=command_xml or "",
            ext=command_ext,
            op_attr=f' op="{escape(op)}"' if op else "",
            clTRID=clTRID or "unused",
        )

    extensions_xml = list(filter(None, epp_extensions))
    if extensions_xml:
        # Exceptions at top-level.
        # Note an <extension> block can also occur inside the command_xml.
        main_xml += ("  <extension>{}\n  </extension>\n").format(
            "\n".join(extensions_xml),
        )

    return (
        """<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n"""
        f"""<epp xmlns="urn:ietf:params:xml:ns:epp-1.0">\n{main_xml}</epp>"""
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
        <objURI>urn:ietf:params:xml:ns:epp-1.0</objURI>
        <objURI>urn:ietf:params:xml:ns:domain-1.0</objURI>
        <objURI>urn:ietf:params:xml:ns:host-1.0</objURI>
        <objURI>urn:ietf:params:xml:ns:contact-1.0</objURI>"""

    if LOGIN_EXTENSIONS:
        xml += """
        <svcExtension>"""

        for extension in LOGIN_EXTENSIONS:
            xml += f"""
          <extURI>{extension}</extURI>"""

        xml += """
        </svcExtension>"""

    xml += """
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


def poll_req(transaction_id=None):
    xml = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
    <epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
      <command>
        <poll op="req"/>
        <clTRID>{clTRID}</clTRID>
      </command>
    </epp>"""
    return xml_format(xml, clTRID=transaction_id or "unused")


def poll_ack(message_id, transaction_id=None):
    xml = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
    <epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
      <command>
        <poll op="ack" msgID="{msgID}"/>
        <clTRID>{clTRID}</clTRID>
      </command>
    </epp>"""
    return xml_format(xml, msgID=message_id, clTRID=transaction_id or "unused")
