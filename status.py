from graphviz import Graph


def ascii_status(net):
    for link in net.links:
        n1 = link.intf1.node.name
        n2 = link.intf2.node.name
        state = "UP" if link.intf1.isUp() and link.intf2.isUp() else "DOWN"
        print(f"{n1} --- {state} --- {n2}")


def graph_status(net, filename="status"):

    g = Graph(format="png")

    for link in net.links:

        n1 = link.intf1.node.name
        n2 = link.intf2.node.name

        up = link.intf1.isUp() and link.intf2.isUp()

        g.edge(
            n1, n2,
            color="green" if up else "red",
            style="solid" if up else "dashed"
        )

    g.render(filename, view=False)


def status(net):
    ascii_status(net)
    graph_status(net)