from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.topo import Topo
from mininet.cli import CLI
from mininet.log import setLogLevel


class SimpleTopo(Topo):
    def build(self):
        # 2 host
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')

        # 1 switch
        s1 = self.addSwitch('s1')

        # link host-switch
        self.addLink(h1, s1)
        self.addLink(h2, s1)


def run():
    topo = SimpleTopo()

    net = Mininet(
        topo=topo,
        switch=OVSSwitch,
        controller=lambda name: RemoteController(
            name,
            ip='127.0.0.1',
            port=6633   # POX default
        ),
        autoSetMacs=True
    )

    net.start()

    print("\n🚀 Topologia avviata con controller remoto\n")
    CLI(net)

    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    run()