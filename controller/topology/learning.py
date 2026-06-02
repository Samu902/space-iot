from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from controller.app import SpaceIoTController

from controller.topology.status import print_topology, draw_topology
import time


def learn_switch(cont: SpaceIoTController, switch):
    
    cont.switch_link_graph.add_node(switch.id, last_seen=time.time())
    cont.switches[switch.id] = switch

    print_topology(cont)
    draw_topology(cont)


def learn_host_link(cont: SpaceIoTController, host_mac, switch, switch_port):

    cont.switch_link_graph.add_node(switch.id, last_seen=time.time())
    cont.host_links[host_mac] = {
        "switch_id": switch.id,
        "switch_port": switch_port,
        "last_seen": time.time()
    }

    print_topology(cont)
    draw_topology(cont)


def learn_switch_link(cont: SpaceIoTController, src_switch, dst_switch, src_port, bw=1, delay=0, loss=0):

    cont.switch_link_graph.add_node(src_switch.id, last_seen=time.time())
    cont.switch_link_graph.add_node(dst_switch.id, last_seen=time.time())

    cont.switch_link_graph.add_edge(
        src_switch.id, 
        dst_switch.id,
        src_port=src_port,
        bw=bw,
        delay=delay,
        loss=loss,
        last_seen=time.time()
    )

    print_topology(cont)
    draw_topology(cont)


def age_topology(cont: SpaceIoTController):

    now = time.time()
    topology_changed = False

    for src, dst, data in list(cont.switch_link_graph.edges(data=True)):
        age = now - data.get("last_seen", now)

        if age > cont.link_timeout:
            print(f"[AGING] link s{src} -> s{dst} expired")
            cont.switch_link_graph.remove_edge(src, dst)
            topology_changed = True

    for host, info in list(cont.host_links.items()):
        age = now - info["last_seen"]

        if age > cont.node_timeout:
            print(f"[AGING] host {host} expired")
            del cont.host_links[host]
            topology_changed = True

    for sw in list(cont.switches.keys()):

        if not cont.switch_link_graph.has_node(sw):
            continue

        node_data = cont.switch_link_graph.nodes[sw]
        age = now - node_data.get("last_seen", now)

        if age > cont.node_timeout:
            print(f"[AGING] switch s{sw} expired")
            del cont.switches[sw]
            cont.switch_link_graph.remove_node(sw)
            topology_changed = True

    if topology_changed:
        print_topology(cont)
        draw_topology(cont)