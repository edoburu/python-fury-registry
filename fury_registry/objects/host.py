from fury_registry.constants import XMLNS
from fury_registry.utils import get_node_date, get_node_text

from .base import ParsedObject


class EppHost(ParsedObject):
    """
    Host data object (e.g. for nameservers)
    """

    @classmethod
    def parse_xml_fields(cls, resdata, extension=None):
        infData = resdata.find("host:infData", XMLNS)

        ips = []
        for addr in infData.findall("host:addr", XMLNS):
            ips.append(addr.text)

        return dict(
            name=get_node_text(infData, "host:name"),
            roid=get_node_text(
                infData, "host:roid"
            ),  # Repository object identifier (assigned on creation)
            status=infData.find("host:status", XMLNS).attrib["s"],
            addr=ips,
            clID=get_node_text(infData, "host:clID"),  # current registrar
            crID=get_node_text(infData, "host:crID"),  # initial registrar
            crDate=get_node_date(infData, "host:crDate"),
        )

    def __init__(self, name, roid, status, addr, clID, crID, crDate):
        self.name = name
        self.roid = roid
        self.status = status
        self.addr = addr
        self.cl_id = clID
        self.cr_id = crID
        self.created_date = crDate

    def __repr__(self):
        return "<Host {} {}>".format(self, " ".join(self.addr))

    def __str__(self):
        return self.name
