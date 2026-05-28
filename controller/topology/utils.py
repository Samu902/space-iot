from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from controller.app import SpaceIoTController
    

def get_switch_by_host(cont: SpaceIoTController, mac):
    return cont.switches[cont.host_links.get(mac, (None, None))[0]]
