from ryu.cmd import manager
import sys

if __name__ == "__main__":
    sys.argv = [
        "ryu-manager",
        "--verbose",
        "controller.ryu_controller"
    ]

    manager.main()