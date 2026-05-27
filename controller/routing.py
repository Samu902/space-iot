from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from controller.app import SpaceIoTController

import networkx as nx

def compute_path(cont: SpaceIoTController, src_mac, dst_mac):

    if src_mac not in cont.host_links or dst_mac not in cont.host_links:
        return None

    src_switch_id = cont.host_links[src_mac][0]
    dst_switch_id = cont.host_links[dst_mac][0]

    try:
        return nx.shortest_path(
            cont.switch_link_graph,
            source=src_switch_id,
            target=dst_switch_id,
            weight="cost"
        )
    except nx.NetworkXNoPath:
        return None


def recompute(cont: SpaceIoTController, src_mac, dst_mac):

    return compute_path(cont, src_mac, dst_mac)