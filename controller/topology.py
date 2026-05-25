from controller.app import SpaceIoTController


def learn_host_link(cont: SpaceIoTController, host_mac, switch, switch_port):

    cont.switches[switch.id] = switch
    cont.switch_link_graph.add_node(switch.id)
    cont.host_links[host_mac] = (switch.id, switch_port)


def learn_switch_link(cont: SpaceIoTController, src_switch, dst_switch, src_port):

    cont.switches[src_switch.id] = src_switch
    cont.switches[dst_switch.id] = dst_switch

    cont.switch_link_graph.add_node(src_switch.id)
    cont.switch_link_graph.add_node(dst_switch.id)

    cont.switch_link_graph.add_edge(
        src_switch.id, 
        dst_switch.id,
        src_port=src_port
    )


def get_switch_by_host(cont: SpaceIoTController, mac):
    return cont.switches[cont.host_links.get(mac, (None, None))[0]]
