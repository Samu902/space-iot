from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet

from controller.topology import learn_host_link
from controller.routing import compute_path
from controller.flow import install_path

import networkx as nx
import time

class SpaceIoTController(app_manager.RyuApp):

    # supported OpenFlow versions
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    # state variables
    switch_link_graph = nx.DiGraph()        # src_switch_id + dst_switch_id + src_port + link_metadata
    switches = {}                           # switch_id -> switch_object
    host_links = {}                         # host_mac -> (switch_id, switch_port, link_metadata)
    paths = {}                              # (src_host_mac, dst_host_mac) -> path (list di switch_id)

    # init base Ryu controller
    def __init__(self, *args, **kwargs):
        super(SpaceIoTController, self).__init__(*args, **kwargs)


    # switch default flow rule (table-miss): let controller decide what to do
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):

        # extract data from switch object (datapath)
        dp = ev.msg.datapath
        ofp = dp.ofproto
        parser = dp.ofproto_parser

        # match: all packets
        match = parser.OFPMatch()

        # actions: send full packet to controller 
        actions = [parser.OFPActionOutput(ofp.OFPP_CONTROLLER, ofp.OFPCML_NO_BUFFER)]

        # instructions: apply actions immediately
        inst = [parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]

        # build flow modification message (table-miss flow entry)
        mod = parser.OFPFlowMod(
            datapath=dp,
            priority=0,
            match=match,
            instructions=inst
        )

        # send rule and install on the switch
        dp.send_msg(mod)


    # main controller packet-in event handler
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):

        # extract msg data
        msg = ev.msg
        dp = msg.datapath
        dpid = dp.id
        in_port = msg.match['in_port']

        # learn_switch: da spostare in topology in qualche modo
        self.switches[dpid] = dp

        # parse packet and eth frame
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)

        if eth is None:
            return
        
        # 🔥 1. LINK DISCOVERY (LLDP)
        if eth.ethertype == 0x88cc:  # LLDP
            src_dpid = extract_lldp_switch(pkt)
            links[(src_dpid, dpid)] = in_port
            links[(dpid, src_dpid)] = out_port_from_lldp(pkt)
            return

        src = eth.src
        dst = eth.dst

        # learn topology
        learn_host_link(self, src, dp, in_port)

        # compute path between src and dst
        path = compute_path(self, src, dst)

        if not path:
            return

        # log
        print("\n[SPACE ROUTE]")
        print(f"{src} → {dst}")
        print(path)

        # install flow on switches in path
        install_path(self, src, dst, path)