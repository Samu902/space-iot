from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from controller.app import SpaceIoTController

from controller.topology.status import print_topology, draw_topology


def learn_switch(cont: SpaceIoTController, switch):
    
    cont.switch_link_graph.add_node(switch.id)
    cont.switches[switch.id] = switch

    print_topology(cont)
    draw_topology(cont)


def learn_host_link(cont: SpaceIoTController, host_mac, switch, switch_port):

    cont.switch_link_graph.add_node(switch.id)
    cont.host_links[host_mac] = (switch.id, switch_port)

    print_topology(cont)
    draw_topology(cont)


def learn_switch_link(cont: SpaceIoTController, src_switch, dst_switch, src_port, bw=1, delay=0, loss=0):

    cont.switch_link_graph.add_node(src_switch.id)
    cont.switch_link_graph.add_node(dst_switch.id)

    cont.switch_link_graph.add_edge(
        src_switch.id, 
        dst_switch.id,
        src_port=src_port,
        bw=bw,
        delay=delay,
        loss=loss
    )

    print_topology(cont)
    draw_topology(cont)