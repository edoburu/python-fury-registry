

class ParsedObject(object):
    """
    Base interface to parse XML nodes.
    """

    @classmethod
    def from_xml(cls, node, extension=None):
        return cls(**cls.parse_xml_fields(node, extension=extension))

    @classmethod
    def parse_xml_fields(cls, node, extension=None):
        raise NotImplementedError("missing parse_xml_fields")
