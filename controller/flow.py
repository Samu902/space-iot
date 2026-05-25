from controller.app import SpaceIoTController


def install_flow(switch, src, dst, out_port, priority=10):

    # extract switch attributes
    parser = switch.ofproto_parser
    ofp = switch.ofproto

    match = parser.OFPMatch(
        eth_src=src,
        eth_dst=dst
    )

    # action: send packet to out_port
    actions = [parser.OFPActionOutput(out_port)]

    # instruction: apply action immediately
    inst = [
        parser.OFPInstructionActions(
            ofp.OFPIT_APPLY_ACTIONS,
            actions
        )
    ]

    # build flow modification message
    mod = parser.OFPFlowMod(
        datapath=switch,
        priority=priority,
        match=match,
        instructions=inst
    )

    # send rule and install on switch
    switch.send_msg(mod)


def install_path(cont: SpaceIoTController, src, dst, path):

    # save path to controller state
    cont.paths[(src, dst)] = path

    for i in range(len(path) - 1):

        # get current link data
        node = path[i]
        next_node = path[i + 1]
        link_data = cont.switch_link_graph.get_edge_data(node, next_node)

        if not link_data:
            continue

        #out_port = hash((node, next_node)) % 5 + 1
        #out_port = links[(node, next_node)][0]
        out_port = link_data.get("src_port")

        current_switch = cont.switches[node]

        # install flow for every switch in the path
        install_flow(current_switch, src, dst, out_port)