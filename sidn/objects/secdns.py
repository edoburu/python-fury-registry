from itertools import chain

from sidn.constants import XMLNS
from sidn.utils import get_node_date, get_node_text, python_2_unicode_compatible

from .base import ParsedObject


class DNSSec(ParsedObject):
    """
    DNSSec info
    """

    @classmethod
    def parse_xml_fields(cls, node, extension=None):
        keydatas = []
        dskeys = []
        for node in node.findall('secDNS:keyData', XMLNS):
            keydatas.append(KeyData.from_xml(node))
        for node in node.findall('secDNS:dsData', XMLNS):
            dskeys.append(DSKey.from_xml(node))
        return dict(
            keydatas=keydatas,
            dskeys=dskeys
        )

    def __init__(self, keydatas=(), dskeys=()):
        self.keydatas = keydatas
        self.dskeys = dskeys

    def __contains__(self, item):
        return item in self.keydatas or item in self.dskeys

    def __repr__(self):
        return '<DNSSec[{0}]>'.format(", ".join(repr(x) for x in chain(self.dskeys, self.keydatas)))


@python_2_unicode_compatible
class DSKey(ParsedObject):
    """
    Delegation Signer key

    SIDN doesn't use the ``dsData`` fields.
    It only reads the ``keyData`` field.
    """

    @classmethod
    def parse_xml_fields(cls, node, extension=None):
        return dict(
            keyTag=get_node_text(node, 'secDNS:keyTag'),
            alg=int(get_node_text(node, 'secDNS:alg')),
            digestType=int(get_node_text(node, 'secDNS:digestType')),
            digest=get_node_text(node, 'secDNS:digest'),
            keyData=KeyData.from_xml(node.find('secDNS:keyData', XMLNS)),
        )

    def __init__(self, keyTag, alg, digestType, digest, keyData=()):
        """
        :type keyTag: int
        :type alg: int
        :param digestType: See https://tools.ietf.org/html/rfc4034#appendix-A.2
        :type digestType: int
        :type digest: str
        :type keyData: Tuple[KeyData]
        """
        self.keyTag = keyTag  # unsignedShort
        self.alg = alg  # unsignedByte
        self.digestType = digestType  # unsignedByte
        self.digest = digest  # hexBinary
        self.keyData = keyData  # secDNS:keyDataType

    def __repr__(self):
        return '<DSKey {0}>'.format(self)

    def __str__(self):
        return self.digest

    def __eq__(self, other):
        return (
            isinstance(other, DSKey) and
            self.keyTag == other.keyTag and
            self.alg == other.alg and
            self.digestType == other.digestType and
            self.digest == other.digest and
            self.keyData == other.keyData
        )

    def __ne__(self, other):
        return not self.__eq__(other)


@python_2_unicode_compatible
class KeyData(ParsedObject):
    """
    DNSSec client key data
    """
    PROTOCOL3 = 3

    #: DSA/SHA-1
    ALG_DSA = 3
    #: Elliptic Curve
    ALG_ECC = 4
    #: RSA/SHA-1
    ALG_SHA1 = 5
    #: RSA/SHA-256
    ALG_SHA256 = 8

    #: Zone signing key
    FLAG_ZSK = 256
    #: Key signing key
    FLAG_KSK = 257

    @classmethod
    def parse_xml_fields(cls, node, extension=None):
        return dict(
            flags=int(get_node_text(node, 'secDNS:flags')),
            protocol=int(get_node_text(node, 'secDNS:protocol')),
            alg=int(get_node_text(node, 'secDNS:alg')),
            pubKey=get_node_text(node, 'secDNS:pubKey'),
        )

    def __init__(self, flags, protocol, alg, pubKey):
        """
        :param flags: Values 256 (ZSK) en 257 (KSK) are allowed.
        :type flags: int
        :param protocol: Fixed value 3, see
        :type protocol: int
        :param alg: See http://www.iana.org/assignments/dns-sec-alg-numbers/dns-sec-alg-numbers.xhtml
        :type alg: int
        :param pubKey: Base64 encoded public key
        :type pubKey: str
        """
        # https://tools.ietf.org/html/rfc4034#section-2.1.1
        self.flags = flags  # unsignedShort
        self.protocol = protocol  # unsignedByte
        self.alg = alg  # unsignedByte
        self.pubKey = pubKey  # secDNS:keyType

    def __repr__(self):
        return '<KeyData: {0}>'.format(self)

    def __str__(self):
        return " ".join(map(str, (self.flags, self.protocol, self.alg, self.pubKey)))

    def __eq__(self, other):
        return (
            isinstance(other, KeyData) and
            self.flags == other.flags and
            self.protocol == other.protocol and
            self.alg == other.alg and
            self.pubKey == other.pubKey
        )

    def __ne__(self, other):
        return not self.__eq__(other)
