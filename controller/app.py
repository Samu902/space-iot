from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib import hub
from ryu.lib.packet import packet, ethernet

from controller.topology.learning import learn_switch, learn_host_link, learn_switch_link, age_topology
from controller.topology.packets import send_lldp, receive_lldp
from controller.routing import compute_path
from controller.flow import install_path

import networkx as nx


class SpaceIoTController(app_manager.RyuApp):

    # supported OpenFlow versions
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SpaceIoTController, self).__init__(*args, **kwargs)

        # state variables
        self.switch_link_graph = nx.DiGraph()        # src_switch_id + dst_switch_id + src_port + link_metadata
        self.switches = {}                           # switch_id -> switch_object
        self.host_links = {}                         # host_mac -> (switch_id, switch_port, link_metadata)
        self.paths = {}                              # (src_host_mac, dst_host_mac) -> path (list di switch_id)

        self.refresh_topology_period = 30        # every 2 minutes
        self.node_timeout = 1 * 60      # 5 minuti
        self.link_timeout = 1 * 60      # 3 minuti

        # define lldp send loop (topology discovery refresh) as local function, then start it as a thread
        def lldp_send_loop():
            while True:
                for id, switch in self.switches.items():
                    send_lldp(switch)
                hub.sleep(self.refresh_topology_period)

        self.lldp_thread = hub.spawn(lldp_send_loop)

        def topology_aging_loop():
            while True:
                age_topology(self)
                hub.sleep(10)

        self.aging_thread = hub.spawn(topology_aging_loop)


    # -----------------------------
    # SWITCH INIT
    # -----------------------------
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):

        dp = ev.msg.datapath
        ofp = dp.ofproto
        parser = dp.ofproto_parser

        # register datapath
        learn_switch(self, dp)

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
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)

        print(f"PACKETIN from {dp.id}:{in_port}, eth type = {eth.ethertype}")

        if eth is None:
            return

        # LLDP packets for topology discovery
        if eth.ethertype == 0x88cc:
            src_dpid, src_port = receive_lldp(pkt)

            print(f"Ricevuto LLDP: s{src_dpid}:{src_port} -> s{dp.id}")

            learn_switch_link(self, self.switches[src_dpid], dp, src_port, bw=1, delay=0, loss=0)

            for (src, dst) in list(self.paths.keys()):
                path = compute_path(self, src, dst)
                if path:
                    install_path(self, src, dst, path)

            return

        src = eth.src
        dst = eth.dst

        # ignore non mininet host packets
        if not src.startswith("00:00:00:00:00:"):
            return

        # learn topology
        if src not in self.host_links:
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