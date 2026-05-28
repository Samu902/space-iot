from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from controller.app import SpaceIoTController

import networkx as nx
import matplotlib.pyplot as plt
import os


def learn_host_link(cont: SpaceIoTController, host_mac, switch, switch_port):

    cont.switches[switch.id] = switch
    cont.switch_link_graph.add_node(switch.id)
    cont.host_links[host_mac] = (switch.id, switch_port)


def learn_switch_link(cont: SpaceIoTController, src_switch, dst_switch, src_port):

    cont.switches[src_switch.id] = src_switch
    cont.switches[dst_switch.id] = dst_switch

    cont.switch_link_graph.add_node(src_switch.id)
    cont.switch_link_graph.add_node(dst_switch.id)

    cont.switch_link_graph.add_edge(
        src_switch.id, 
        dst_switch.id,
        src_port=src_port
    )


def get_switch_by_host(cont: SpaceIoTController, mac):
    return cont.switches[cont.host_links.get(mac, (None, None))[0]]


def print_topology(cont: SpaceIoTController):

    print("\n========== SWITCH LINKS ==========")

    for src, dst, data in cont.switch_link_graph.edges(data=True):

        src_port = data.get("src_port")

        print(f"s{src}:{src_port} --> s{dst}")

    print("\n============ HOST LINKS ===============")

    for host, (switch_id, switch_port) in cont.host_links.items():

        print(f"{host} --> s{switch_id}:{switch_port}")

    print("================================\n")


def draw_topology(cont: SpaceIoTController, out_path="/space-iot/topology.png"):

    g = nx.DiGraph()

    # add switch and host links to the graph

    for src, dst, data in cont.switch_link_graph.edges(data=True):
        g.add_edge(src, dst, label=data.get("src_port"))

    for host, (sw, sw_port) in cont.host_links.items():
        g.add_edge(host, sw, label=sw_port)

    # figure setup

    pos = nx.spring_layout(g, seed=42)

    plt.figure(figsize=(12, 8))

    # graph nodes coloring and drawing (based on device type)

    node_colors = []
    for n in g.nodes():
        if n in cont.switches:
            node_colors.append("lightblue")   # switches
        else:
            node_colors.append("lightgreen")  # hosts

    nx.draw_networkx_nodes(
        g,
        pos,
        node_color=node_colors,
        node_size=2500
    )

    # graph edges coloring and drawing (based on bidirectionality)

    bidir = set()

    for u, v in g.edges():
        if g.has_edge(v, u):
            bidir.add((u, v))
            bidir.add((v, u))

    for u, v in g.edges():
        if (u, v) in bidir:
            style = "solid"
            color = "black"
            width = 2
        else:
            style = "dashed"
            color = "red"
            width = 1.5

        nx.draw_networkx_edges(
            g,
            pos,
            edgelist=[(u, v)],
            edge_color=color,
            style=style,
            width=width,
            arrows=True
        )

    # node labels (macs and dpids)

    nx.draw_networkx_labels(g, pos, font_size=10)

    # edge labels (ports)

    edge_labels = nx.get_edge_attributes(g, "label")

    nx.draw_networkx_edge_labels(
        g,
        pos,
        edge_labels=edge_labels,
        font_size=9,
        label_pos=0.7
    )

    # save figure to image

    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    plt.title("SpaceIoT Topology")
    plt.axis("off")
    plt.tight_layout()

    plt.savefig(out_path, dpi=200)
    plt.close()

    print(f"[TOPOLOGY] saved to {out_path}")