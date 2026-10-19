from fury_registry.constants import XMLNS
from fury_registry.utils import get_node_date, get_node_text

from .base import ParsedObject


class EppContact(ParsedObject):
    """
    Contact data object
    """

    @classmethod
    def parse_xml_fields(cls, resData, extension=None):
        infData = resData.find('contact:infData', XMLNS)
        postalInfo = infData.find("contact:postalInfo[@type='loc']", XMLNS)
        addr = postalInfo.find('contact:addr', XMLNS)

        return dict(
            id=get_node_text(infData, 'contact:id'),
            roid=get_node_text(infData, 'contact:roid'),
            status=infData.find('contact:status', XMLNS).attrib['s'],
            name=get_node_text(postalInfo, 'contact:name'),
            org=get_node_text(postalInfo, 'contact:org'),
            street=get_node_text(addr, 'contact:street'),
            city=get_node_text(addr, 'contact:city'),
            pc=get_node_text(addr, 'contact:pc'),
            cc=get_node_text(addr, 'contact:cc'),
            voice=get_node_text(infData, 'contact:voice'),
            fax=get_node_text(infData, 'contact:fax'),
            email=get_node_text(infData, 'contact:email'),
            crDate=get_node_date(infData, 'contact:crDate'),
            upDate=get_node_date(infData, 'contact:upDate'),
        )

    def __init__(self, id, roid, status, name, org, street, city, pc, cc, voice, fax, email, crDate, upDate):
        # Some fields are renamed for easier referencing,
        # while the constructor arguments map to the XML field names.
        self.handle = id
        self.roid = roid
        self.status = status
        self.name = name
        self.organisation = org
        self.street = street
        self.city = city
        self.postcode = pc
        self.country_code = cc
        self.phone = voice
        self.fax = fax
        self.email = email
        self.created_date = crDate
        self.updated_date = upDate

    def __repr__(self):
        return f'<Contact {self}>'

    def __str__(self):
        return f"[{self.handle}] {self.name}, {self.street}, {self.postcode} {self.city} ({self.country_code})"
