from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from fury_registry.client import EPP


class BaseHandler:
    """Internal interface for all handlers.
    """

    def __init__(self, epp: EPP):
        self.epp = epp
