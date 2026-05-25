from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib import hub
from ryu.lib.packet import packet, ethernet, lldp

from controller.topology import learn_host_link, learn_switch_link
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

        # start lldp loop (topology discovery refresh)
        self.lldp_thread = hub.spawn(self._lldp_loop)


    def _lldp_loop(self):
        while True:
            for dpid, datapath in self.switches.items():
                self._send_lldp(datapath)
            hub.sleep(2)


    def _send_lldp(self, datapath):

        ofp = datapath.ofproto
        parser = datapath.ofproto_parser

        lldp_chassis_id = lldp.ChassisID(
            subtype=lldp.ChassisID.SUB_LOCALLY_ASSIGNED,
            chassis_id=str(datapath.id).encode()
        )

        pkt = packet.Packet()

        pkt.add_protocol(ethernet.ethernet(
            ethertype=0x88cc,
            dst="ff:ff:ff:ff:ff:ff",
            src="00:00:00:00:00:01"
        ))

        pkt.add_protocol(lldp.lldp(
            tlv_list=[lldp_chassis_id]
        ))

        pkt.serialize()

        data = pkt.data

        actions = [parser.OFPActionOutput(ofp.OFPP_FLOOD)]

        out = parser.OFPPacketOut(
            datapath=datapath,
            buffer_id=ofp.OFP_NO_BUFFER,
            in_port=ofp.OFPP_CONTROLLER,
            actions=actions,
            data=data
        )

        datapath.send_msg(out)


    def _handle_lldp_receive(self, pkt, dst_switch):

        lldp_pkt = pkt.get_protocol(lldp.lldp)

        src_port = None
        src_dpid = None

        for tlv in lldp_pkt.tlvs:

            if isinstance(tlv, lldp.ChassisID):
                src_dpid = int(tlv.chassis_id.decode())

            if isinstance(tlv, lldp.PortID):
                src_port = int(tlv.port_id.decode()) if isinstance(tlv.port_id, bytes) else int(tlv.port_id)

        learn_switch_link(self, src_dpid, dst_switch.id, src_port)

        for (src, dst) in list(self.paths.keys()):
            path = compute_path(self, src, dst)
            if path:
                install_path(self, src, dst, path)


    # -----------------------------
    # SWITCH INIT
    # -----------------------------
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):

        dp = ev.msg.datapath
        ofp = dp.ofproto
        parser = dp.ofproto_parser

        # register datapath
        self.switches[dp.id] = dp

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

        if eth is None:
            return

        if eth.ethertype == 0x88cc:
            self._handle_lldp_receive(pkt, dp, in_port)
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