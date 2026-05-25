from ryu.cmd import manager
import sys

if __name__ == "__main__":
    sys.argv = [
        "ryu-manager",
        "--verbose",
        "controller.app"
    ]

    manager.main()