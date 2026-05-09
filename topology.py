from mininet.net import Mininet
from mininet.node import Controller
from mininet.link import TCLink

from tech import add_link


def build_network():

    net = Mininet(controller=Controller, link=TCLink)

    net.addController("c0")

    # nodi
    iot1 = net.addHost("iot1")
    iot2 = net.addHost("iot2")
    gw = net.addHost("gw")
    earth = net.addHost("earth")

    # link tecnologici
    add_link(net, iot1, iot2, "zigbee")
    add_link(net, iot2, gw, "lora")
    add_link(net, gw, earth, "fso")

    return net