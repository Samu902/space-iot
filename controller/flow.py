from controller.app import SpaceIoTController


def install_flow(switch, src, dst, out_port, priority=10):

    # extract switch attributes
    parser = switch.ofproto_parser
    ofp = switch.ofproto

    # match: src and dst mac
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


def delete_flows(switch, src, dst):

    parser = switch.ofproto_parser
    ofp = switch.ofproto

    match = parser.OFPMatch(
        eth_src=src,
        eth_dst=dst
    )

    # delete every flow in the switch with this src and dst
    mod = parser.OFPFlowMod(
        datapath=switch,
        command=ofp.OFPFC_DELETE,
        out_port=ofp.OFPP_ANY,
        out_group=ofp.OFPG_ANY,
        match=match
    )

    switch.send_msg(mod)


def install_path(cont: SpaceIoTController, src, dst, path):

    # save path to controller state
    cont.paths[(src, dst)] = path

    # loop over every switch in the path
    for i in range(len(path) - 1):

        # get current link data
        node = path[i]
        next_node = path[i + 1]

        link = cont.switch_link_graph[node][next_node]
        out_port = link["src_port"]

        switch = cont.switches[node]

        # clean old flows related to src and dst (if present)
        delete_flows(switch, src, dst)

        # install new flow in the switch
        install_flow(switch, src, dst, out_port)