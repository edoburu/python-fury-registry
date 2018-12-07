from sidn import commands


class BaseHandler(object):
    """
    Internal interface for all handlers.
    """

    def __init__(self, epp):
        """
        :type epp: sidn.client.EPP
        """
        self.epp = epp

    def _build_command(self, command_name, command_xml, command_extensions=(), op=None, transaction_id=None, epp_extensions=()):
        """
        Build a generic command
        """
        return commands.epp.build_command(
            command_name=command_name,
            command_xml=command_xml,
            command_extensions=command_extensions,
            op=op,
            clTRID=transaction_id,
            epp_extensions=epp_extensions
        )
