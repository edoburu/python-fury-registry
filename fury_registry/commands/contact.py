import re

from fury_registry.utils import escape, xml_format

RE_PHONE_COUNTRY = re.compile(r"^(?P<prefix>\+|0+)(?P<country>[0-9]{1,2})[- .]")
RE_PHONE = re.compile(r"^(\+[0-9]{1,3}\.[0-9]{1,14})?$")


def info_part(handle):
    xml = """
      <contact:info xmlns:contact="urn:ietf:params:xml:ns:contact-1.0">
        <contact:id>{handle}</contact:id>
      </contact:info>"""
    return xml_format(xml, handle=handle)


def check_part(handle):
    xml = """
      <contact:check xmlns:contact="urn:ietf:params:xml:ns:contact-1.0">
        <contact:id>{handle}</contact:id>
      </contact:check>"""
    return xml_format(xml, handle=handle)


def create_part(handle, **data):
    xml = xml_format(
        """
      <contact:create xmlns:contact="urn:ietf:params:xml:ns:contact-1.0">
        <contact:id>{handle}</contact:id>""",
        handle=handle,
    )

    xml += _contact_info(**data)

    xml += """
      </contact:create>"""
    return xml


def update_parts(handle, **data):
    """
    Update an contact.
    """
    xml = xml_format(
        """
      <contact:update xmlns:contact="urn:ietf:params:xml:ns:contact-1.0">
        <contact:id>{handle}</contact:id>
          <contact:chg>""",
        handle=handle,
    )

    xml += _contact_info(**data)  # TODO: only add included fields?
    xml += """
        </contact:chg>
      </contact:update>"""


def _contact_info(**data):
    if data.get("voice", None):
        data["voice"] = _fix_phone(data["voice"])
    else:
        data["voice"] = ""

    if data.get("fax", None):
        data["fax"] = _fix_phone(data["fax"])
    else:
        data["fax"] = ""

    # DRS5 notes:
    # - name allows only unrestricted utf-8, not 7-bit US-ASCII
    # - handle is mandatory, but DRS5 will generate a new one server-side in the format XXX999999-YYYYY
    # - street can be 1 field.
    # - postalInfo only supports 'loc'
    # - sp (state/province) is not implemented
    # - pc is mandatory for country NL
    # - voice is mandatory
    # - trDate not implemented (no transfer support)
    # - pw is mandatory, but not used
    # - disclose is not implemented

    xml = """
        <contact:postalInfo type="loc">
          <contact:name>{name}</contact:name>
          <contact:org>{org}</contact:org>
          <contact:addr>"""

    street = data["street"]
    if not isinstance(street, (list, tuple)):
        street = [street]

    for item in street:
        xml += f"""
            <contact:street>{escape(item)}</contact:street>"""

    data["pc"] = data["pc"].replace(" ", "")
    xml += """
            <contact:city>{city}</contact:city>
            <contact:pc>{pc}</contact:pc>
            <contact:cc>{cc}</contact:cc>
          </contact:addr>
        </contact:postalInfo>"""

    if data["voice"]:
        xml += """
        <contact:voice>{voice}</contact:voice>"""

    if data["fax"]:
        xml += """
        <contact:fax>{fax}</contact:fax>"""

    xml += """
        <contact:email>{email}</contact:email>
        <contact:authInfo>
          <contact:pw>2fooBAR</contact:pw>
        </contact:authInfo>"""
    return xml_format(xml, **data)


def delete_part(handle):
    xml = """
      <contact:delete xmlns:contact="urn:ietf:params:xml:ns:contact-1.0">
        <contact:id>{handle}</contact:id>
      </contact:delete>"""
    return xml_format(xml, handle=handle)


def _fix_phone(value):
    # A fax or phone number is a string that starts with a '+', followed by the country code, followed by a '.'
    # and then followed by a series of numbers being the fax or telephone.
    value = RE_PHONE_COUNTRY.sub(r"+\g<country>.", value)
    value = value.replace(" ", "").replace("-", "")
    if not RE_PHONE.match(value):
        raise ValueError(f"Could not format the phone number {value}")
    return value
