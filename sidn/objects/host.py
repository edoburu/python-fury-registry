import logging

from sidn.utils import python_2_unicode_compatible

logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class EppHost(object):
    """
    Host data object (e.g. for nameservers)
    """

    def __init__(self, name, addr):
        self.name = name
        self.addr = addr

    def __repr__(self):
        return '<Host {0}>'.format(self)

    def __str__(self):
        return self.name
