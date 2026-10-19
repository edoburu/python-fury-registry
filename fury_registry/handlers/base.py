from __future__ import annotations

import typing

from fury_registry import commands

if typing.TYPE_CHECKING:
    from fury_registry.client import EPP


class BaseHandler:
    """Internal interface for all handlers.
    """

    def __init__(self, epp: EPP):
        self.epp = epp

    def _build_command(
        self,
        command_name: str,
        command_xml: str,
        command_extensions: typing.Iterable[str]=(),
        op: str|None=None,
        transaction_id: str|None=None,
        epp_extensions: typing.Iterable[str]=(),
    ):
        """Build a generic command
        """
        return commands.epp.build_command(
            command_name=command_name,
            command_xml=command_xml,
            command_extensions=command_extensions,
            op=op,
            clTRID=transaction_id,
            epp_extensions=epp_extensions,
        )
