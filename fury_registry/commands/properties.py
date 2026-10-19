from fury_registry.utils import xml_format


def create_part(properties: dict[str, str]) -> str:
    xml_properties = _fury_properties(properties)
    return f"""
    <fury:create xmlns:fury="urn:ietf:params:xml:ns:fury-2.1">
      {xml_properties}
    </fury:create>"""


def update_part(properties: dict[str, str]) -> str:
    # Changing properties requires a remove + add.
    old_xml_properties = ""
    for key in properties:
        # Remove all various associated with the property.
        # TODO: no support yet for multi-value properties
        old_xml_properties += xml_format(
            """
          <fury:property>
            <fury:key>{key}</fury:key>
            <fury:remAll>true</fury:remAll>
          </fury:property>\n""",
            key=key,
        )

    xml_properties = _fury_properties(properties)
    ext = f"""
    <fury:update xmlns:fury="urn:ietf:params:xml:ns:fury-2.1">
      <fury:rem>
        <fury:properties>{old_xml_properties}</fury:properties>
      </fury:rem>
      <fury:add>
      {xml_properties}
      </fury:add>
    </fury:create>"""

    return ext


def _fury_properties(properties: dict[str, str]) -> str:
    xml = "          <fury:properties>"
    for key, value in properties.items():
        xml += xml_format(
            """
            <fury:property>
              <fury:key>{key}</fury:key>
              <fury:value>{value}</fury:value>
            </fury:property>\n""",
            key=key,
            value=value,
        )
    xml += "          </fury:properties>"
    return xml
