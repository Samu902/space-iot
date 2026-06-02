from mininet.cli import CLI

from network.events import env_down, env_up, gateway_down
from network.status import status


class CustomCLI(CLI):

    def do_env_down(self, line):
        env_down(self.mn)

    def do_env_up(self, line):
        env_up(self.mn)

    def do_gateway_down(self, line):
        gateway_down(self.mn)

    def do_status(self, line):
        status(self.mn)


def start_cli(net):
    CustomCLI(net)