from mininet.net import Mininet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import setLogLevel, info
from graphviz import Graph

TECH = {

    "lora": {
        "bw": 0.5,
        "delay": "200ms",
        "loss": 5
    },

    "zigbee": {
        "bw": 2,
        "delay": "20ms",
        "loss": 3
    },

    "wifi": {
        "bw": 100,
        "delay": "5ms",
        "loss": 1
    },

    "fso": {
        "bw": 1000,
        "delay": "1ms",
        "loss": 0.1
    }
}

def add_link(net: Mininet, a, b, tech):

    p = TECH[tech]

    net.addLink(
        a, b,
        bw=p["bw"],
        delay=p["delay"],
        loss=p["loss"]
    )


class CustomCLI(CLI):

    # =========================
    # EVENTI CUSTOM
    # =========================

    def do_mesh_down(self, line):
        """
        Disattiva un link mesh
        comando: mesh_down
        """
        mesh_down(self.mn)

    def do_mesh_up(self, line):
        """
        Riattiva il link mesh
        comando: mesh_up
        """
        mesh_up(self.mn)

    def do_gateway_down(self, line):
        """
        Simula guasto gateway
        comando: gateway_down
        """
        gateway_down(self.mn)

    def do_gateway_up(self, line):
        """
        Ripristina gateway
        comando: gateway_up
        """
        gateway_up(self.mn)

    def do_status(self, line):
        """
        Stato rete
        comando: status
        """
        network_status(self.mn)


# =========================================================
# EVENTI
# =========================================================

def mesh_down(net):

    info("\n*** Disattivazione link mesh iot1 <-> iot2\n")

    iot1 = net.get('iot1')
    iot2 = net.get('iot2')

    link = net.linksBetween(iot1, iot2)[0]

    link.intf1.ifconfig('down')
    link.intf2.ifconfig('down')


def mesh_up(net):

    info("\n*** Ripristino link mesh iot1 <-> iot2\n")

    iot1 = net.get('iot1')
    iot2 = net.get('iot2')

    link = net.linksBetween(iot1, iot2)[0]

    link.intf1.ifconfig('up')
    link.intf2.ifconfig('up')


def gateway_down(net):

    info("\n*** Simulazione guasto gateway\n")

    gw1 = net.get('gw1')

    for intf in gw1.intfList():

        if intf.name != 'lo':
            intf.ifconfig('down')


def gateway_up(net):

    info("\n*** Ripristino gateway\n")

    gw1 = net.get('gw1')

    for intf in gw1.intfList():

        if intf.name != 'lo':
            intf.ifconfig('up')


def network_status(net):

    info("\n*** Stato host\n")

    for host in net.hosts:
        info(f"{host.name} -> {host.IP()}\n")

    print_ascii_status(net)
    draw_graphviz(net)


def print_ascii_status(net):

    print("\n*** ASCII TOPOLOGY STATUS ***\n")

    for link in net.links:

        n1 = link.intf1.node.name
        n2 = link.intf2.node.name

        up = link.intf1.isUp() and link.intf2.isUp()

        state = "UP" if up else "DOWN"

        print(f"{n1} --- {state} --- {n2}")

    print()


def draw_graphviz(net, filename="topology_status"):

    g = Graph("topology", format="png")

    # nodi
    nodes = set()

    for link in net.links:

        n1 = link.intf1.node.name
        n2 = link.intf2.node.name

        nodes.add(n1)
        nodes.add(n2)

    for n in nodes:
        shape = "box" if "s" in n else "circle"
        g.node(n, shape=shape)

    # link con stato
    for link in net.links:

        n1 = link.intf1.node.name
        n2 = link.intf2.node.name

        up = link.intf1.isUp() and link.intf2.isUp()

        if up:
            color = "green"
            style = "solid"
        else:
            color = "red"
            style = "dashed"

        g.edge(n1, n2, color=color, style=style)

    path = g.render(filename, view=False)

    print(f"Graph salvato in: {path}\n")

# =========================================================
# TOPOLOGIA
# =========================================================

def topology():

    net = Mininet(
        controller=Controller,
        link=TCLink
    )

    info("*** Creazione controller\n")
    net.addController('c0')

    # =====================================================
    # NODI IoT
    # =====================================================

    info("*** Creazione nodi IoT\n")

    iot1 = net.addHost('iot1', ip='10.0.0.1/24')
    iot2 = net.addHost('iot2', ip='10.0.0.2/24')
    iot3 = net.addHost('iot3', ip='10.0.0.3/24')

    # =====================================================
    # GATEWAY
    # =====================================================

    info("*** Creazione gateway\n")

    gw1 = net.addHost('gw1', ip='10.0.0.254/24')

    # =====================================================
    # CENTRO DI CONTROLLO / TERRA
    # =====================================================

    info("*** Creazione nodo Earth\n")

    earth = net.addHost('earth', ip='10.0.0.100/24')

    # =====================================================
    # SWITCH
    # =====================================================

    info("*** Creazione switch\n")

    s1 = net.addSwitch('s1')

    # =====================================================
    # RETE MESH
    # =====================================================

    info("*** Configurazione mesh\n")

    net.addLink(iot1, iot2, bw=10, delay='5ms')
    net.addLink(iot2, iot3, bw=10, delay='5ms')

    # ridondanza mesh
    net.addLink(iot1, iot3, bw=5, delay='10ms')

    # =====================================================
    # GATEWAY
    # =====================================================

    info("*** Collegamento gateway\n")

    net.addLink(iot3, gw1, bw=20, delay='2ms')

    # =====================================================
    # ACCESSO EARTH
    # =====================================================

    info("*** Collegamento Earth\n")

    net.addLink(gw1, s1)
    net.addLink(earth, s1)

    # =====================================================
    # AVVIO RETE
    # =====================================================

    info("*** Avvio rete\n")

    net.start()

    info("\n*** Rete ibrida Mesh + Gateway pronta\n")
    info("*** Comandi disponibili:\n")
    info("    mesh_down\n")
    info("    mesh_up\n")
    info("    gateway_down\n")
    info("    gateway_up\n")
    info("    status\n\n")

    CustomCLI(net)

    net.stop()


if __name__ == '__main__':

    setLogLevel('info')
    topology()