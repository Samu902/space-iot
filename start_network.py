from network.topology import build_network
from network.cli import start_cli

def main():
    net = build_network()
    net.start()

    start_cli(net)

    net.stop()

if __name__ == "__main__":
    main()