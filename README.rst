EPP Python client for Fury Registries
=====================================

This is a Python client to communicate with the Fury EPP registry interfaces (such as "Hello registry"),
used by the Dutch domain registrar (SIDN) and others.

The communication happens over the generic EPP protocol, which each registrar can extend.
This package has the potential to be generic, but currently the EPP commands are written
with Fury registry variations in mind.

Features:

* Base EPP objects (domains, contacts, hosts)
* Domain transfers, polling
* International domain name decoding (IDNA)
* DNSSec
* Fury properties


Usage
-----

Install it:

.. code-block:: bash

    pip install fury-registry

Code:

.. code-block:: python

    from fury_registry import EPP

    client = EPP(
        host='epp.ote.nic.nl',
        username='...',  # your EPP user name
        password='...',  # your EPP password
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
    print(domain.token)

    contact = client.contacts.get(handle="FOOBAR01")
    print(contact.name)
