EPP Python client for SIDN
==========================

This is a Python client to communicate with the DRS5 interface of SIDN, the Dutch domain registrar.

The communication happens over the generic EPP protocol, which each registrar can extend.
This package has the potential to be generic, but currently the EPP commands are written
with DRS5 variations in mind.

Usage
-----

Install it:

.. code-block:: bash

    pip install sidn

Code:

.. code-block:: python

    from sidn import EPP

    client = EPP(
        host='testdrs.domain-registry.nl',
        username='..',  # your DRS user name
        password='..',  # your DRS password
        certfile="/path/to/certfile.pem",  # Optional parameter
    )

    handle = client.contacts.create(
        name="John Doe",
        street="Ergens 1",
        city="Amsterdam",
        postcode="1100AA",
        country_code="NL"
    )

    domain = client.domains.create(
        name='example.nl',
        registrant=handle,
        contacts=dict(
            admin=handle,
            tech=handle,
        )
        ns=[
            'ns1.example.nl',
            'ns2.example.nl',
        ]
    )

    domain = client.domains.get('example.nl')
    print domain.auth_token

    contact = client.contacts.get(handle="FOOBAR01")
    print contact.name
