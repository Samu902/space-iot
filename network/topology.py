from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.link import TCLink
from network.linktechs import LINK_TECHS

# -- Link creation function

def add_link(net: Mininet, a, b, tech_name: str):

    tech = LINK_TECHS[tech_name]

    net.addLink(
        a,
        b,
        bw=tech.bw_mbps,
        delay=f"{tech.delay_ms}ms",
        loss=tech.loss_percent
    )


# =====================================================
# PHYSICAL NETWORK
# =====================================================

PHYSICAL_LINKS = [

    # =================================================
    # ENVIRONMENT SEGMENT
    # =================================================

    ("env1", "s_env", "wifi"),
    ("env2", "s_env", "wifi"),

    # =================================================
    # ROVER SEGMENT
    # =================================================

    ("rover1", "s_rover", "zigbee"),
    ("rover2", "s_rover", "zigbee"),

    # =================================================
    # GATEWAY SEGMENT
    # =================================================

    ("gw", "s_gw", "wifi"),

    # =================================================
    # EARTH BACKBONE
    # =================================================

    ("earth", "s_earth", "fso"),

    # =================================================
    # INTER-SWITCH NETWORK
    # =================================================

    ("s_env", "s_rover", "zigbee"),

    ("s_rover", "s_gw", "lora"),

    ("s_env", "s_gw", "wifi"),

    ("s_gw", "s_earth", "fso"),
]


# =====================================================
# BUILD NETWORK
# =====================================================

def build_network():

    net = Mininet(
        controller=RemoteController,
        link=TCLink
    )

    # =================================================
    # CONTROLLER
    # =================================================

    net.addController(
        "c0",
        controller=RemoteController,
        ip="127.0.0.1",
        port=6653
    )

    # =================================================
    # HOSTS
    # =================================================

    hosts = {}

    for host_name in [
        "env1",
        "env2",
        "rover1",
        "rover2",
        "gw",
        "earth"
    ]:
        hosts[host_name] = net.addHost(host_name)

    # =================================================
    # OPENFLOW SWITCHES
    # =================================================

    SWITCH_DPID = {
        "s_env": "000000000001",
        "s_rover": "000000000002",
        "s_gw": "000000000003",
        "s_earth": "000000000004",
    }

    switches = {}

    for switch_name in [
        "s_env",
        "s_rover",
        "s_gw",
        "s_earth"
    ]:
        switches[switch_name] = net.addSwitch(
            switch_name,
            dpid=SWITCH_DPID[switch_name],
            protocols="OpenFlow13"
        )

    # =================================================
    # NODE REGISTRY
    # =================================================

    nodes = {}

    nodes.update(hosts)
    nodes.update(switches)

    # =================================================
    # BUILD LINKS
    # =================================================

    for a, b, tech in PHYSICAL_LINKS:
        add_link(
            net,
            nodes[a],
            nodes[b],
            tech
        )

    return net