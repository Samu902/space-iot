from mininet.cli import CLI

from events import mesh_down, gateway_down
from status import status


class CustomCLI(CLI):

    def do_mesh_down(self, line):
        mesh_down(self.mn)

    def do_gateway_down(self, line):
        gateway_down(self.mn)

    def do_status(self, line):
        status(self.mn)


def start_cli(net):
    CustomCLI(net)