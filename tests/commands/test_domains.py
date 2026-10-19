from fury_registry import commands


def test_build_domain_create():
    xml = commands.epp.build_command("create", commands.domain.create_part(
        name="example.nl",
        ns=["ns1.example.nl", "ns2.example.nl"],
        registrant="REG",
        contacts={
            "admin": "ADMIN",
            "tech": "TECH",
        },
    ))
    assert (
        xml
        == """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
  <command>
    <create>
      <domain:create xmlns:domain="urn:ietf:params:xml:ns:domain-1.0">
        <domain:name>example.nl</domain:name>
        <domain:period unit="y">1</domain:period>
        <domain:ns>
          <domain:hostObj>ns1.example.nl</domain:hostObj>
          <domain:hostObj>ns2.example.nl</domain:hostObj>
        </domain:ns>
        <domain:registrant>REG</domain:registrant>
        <domain:contact type="admin">ADMIN</domain:contact>
        <domain:contact type="tech">TECH</domain:contact>
        <domain:authInfo>
          <domain:pw>unused</domain:pw>
        </domain:authInfo>
      </domain:create>
    </create>
    <clTRID>unused</clTRID>
  </command>
</epp>"""
    )


def test_build_domain_get():
    """Parse contact info response"""
    xml = commands.epp.build_command(
        "info",
        commands.domain.info_part(name="example.nl"),
    )
    assert (
        xml
        == """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
  <command>
    <info>
      <domain:info xmlns:domain="urn:ietf:params:xml:ns:domain-1.0">
        <domain:name hosts="all">example.nl</domain:name>
        <domain:authInfo>
          <domain:pw>unused</domain:pw>
        </domain:authInfo>
      </domain:info>
    </info>
    <clTRID>unused</clTRID>
  </command>
</epp>"""
    )


def test_build_domain_check():
    """Parse contact info response"""
    xml = commands.epp.build_command(
        "check",
        commands.domain.check_part(name="example.nl"),
    )
    assert (
        xml
        == """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
  <command>
    <check>
      <domain:check xmlns:domain="urn:ietf:params:xml:ns:domain-1.0">
        <domain:name>example.nl</domain:name>
      </domain:check>
    </check>
    <clTRID>unused</clTRID>
  </command>
</epp>"""
    )


def test_build_domain_delete():
    """Parse contact info response"""
    xml = commands.epp.build_command(
        "delete",
        commands.domain.delete_part(name="example.nl"),
    )
    assert (
        xml
        == """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
  <command>
    <delete>
      <domain:delete xmlns:domain="urn:ietf:params:xml:ns:domain-1.0">
        <domain:name>example.nl</domain:name>
      </domain:delete>
    </delete>
    <clTRID>unused</clTRID>
  </command>
</epp>"""
    )
