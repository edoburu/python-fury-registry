from fury_registry import commands


def test_build_contact_get():
    """Parse contact info response"""
    xml = commands.epp.build_command(
        "info",
        commands.contact.info_part(handle="CONTACT"),
    )
    assert (
        xml
        == """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
  <command>
    <info>
      <contact:info xmlns:contact="urn:ietf:params:xml:ns:contact-1.0">
        <contact:id>CONTACT</contact:id>
      </contact:info>
    </info>
    <clTRID>unused</clTRID>
  </command>
</epp>"""
    )


def test_build_contact_delete():
    """Parse contact info response"""
    xml = commands.epp.build_command(
        "delete",
        commands.contact.delete_part(handle="CONTACT"),
    )
    assert (
        xml
        == """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
  <command>
    <delete>
      <contact:delete xmlns:contact="urn:ietf:params:xml:ns:contact-1.0">
        <contact:id>CONTACT</contact:id>
      </contact:delete>
    </delete>
    <clTRID>unused</clTRID>
  </command>
</epp>"""
    )
