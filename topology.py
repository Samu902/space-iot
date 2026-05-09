from mininet.net import Mininet
from mininet.node import Controller
from mininet.link import TCLink

from linktechs import add_link


# =====================================================
# RETE FISICA LUNARE (PHYSICAL NETWORK LAYER)
# =====================================================

PHYSICAL_LINKS = [

    # =========================
    # MESH IoT (ZigBee)
    # =========================
    ("env1", "env2", "zigbee"),
    ("env2", "rover1", "zigbee"),
    ("rover1", "rover2", "zigbee"),
    ("rover2", "env1", "zigbee"),
    ("env1", "rover1", "zigbee"),  # ridondanza mesh

    # =========================
    # LoRaWAN (long range IoT)
    # =========================
    ("env2", "gw", "lora"),
    ("rover2", "gw", "lora"),

    # =========================
    # Wi-Fi locale (control layer)
    # =========================
    ("rover1", "gw", "wifi"),

    # =========================
    # BACKBONE FSO (Luna ↔ Terra)
    # =========================
    ("gw", "earth", "fso"),
]


# =====================================================
# BUILD TOPOLOGY (Mininet wrapper)
# =====================================================

def build_network():

    net = Mininet(controller=Controller, link=TCLink)

    net.addController("c0")

    # -------------------------
    # NODI (END SYSTEMS)
    # -------------------------
    net.addHost("env1")
    net.addHost("env2")
    net.addHost("rover1")
    net.addHost("rover2")
    net.addHost("gw")
    net.addHost("earth")

    # -------------------------
    # LINK FISICI
    # -------------------------
    for a, b, tech in PHYSICAL_LINKS:
        add_link(net, a, b, tech)

    return net