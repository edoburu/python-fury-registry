from xml.sax.saxutils import escape


def xml_format(xml, **data):
    """
    Apply a str.format() format for XML, with data escaped.
    """
    data = xml_escape(**data)
    return xml.format(**data)


def xml_escape(**data):
    """
    Escape the data for inclusion in XML
    """
    return dict((k, escape(v)) for k, v in data.iteritems())
