from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib import hub
from ryu.lib.packet import packet, ethernet, lldp

from controller.topology import learn_host_link, learn_switch_link, print_topology, draw_topology
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

        for port_no in datapath.ports:

            # skip reserved ports
            if port_no > ofp.OFPP_MAX:
                continue

            pkt = packet.Packet()

            pkt.add_protocol(ethernet.ethernet(
                ethertype=0x88cc,
                dst="ff:ff:ff:ff:ff:ff",
                src="00:00:00:00:00:01"
            ))

            chassis_id = lldp.ChassisID(
                subtype=lldp.ChassisID.SUB_LOCALLY_ASSIGNED,
                chassis_id=str(datapath.id).encode()
            )

            port_id = lldp.PortID(
                subtype=lldp.PortID.SUB_PORT_COMPONENT,
                port_id=str(port_no).encode()
            )

            ttl = lldp.TTL(ttl=10)

            pkt.add_protocol(lldp.lldp(
                tlvs=[
                    chassis_id,
                    port_id,
                    ttl,
                    lldp.End()
                ]
            ))

            pkt.serialize()

            actions = [parser.OFPActionOutput(port_no)]

            out = parser.OFPPacketOut(
                datapath=datapath,
                buffer_id=ofp.OFP_NO_BUFFER,
                in_port=ofp.OFPP_CONTROLLER,
                actions=actions,
                data=pkt.data
            )

            datapath.send_msg(out)


    def _handle_lldp_receive(self, pkt, dst_switch):

        lldp_pkt = pkt.get_protocol(lldp.lldp)

        src_dpid = None
        src_port = None

        for tlv in lldp_pkt.tlvs:

            if isinstance(tlv, lldp.ChassisID):
                src_dpid = int(tlv.chassis_id.decode())

            if isinstance(tlv, lldp.PortID):
                src_port = int(tlv.port_id.decode())

        print("LLDP:", src_dpid, "->", dst_switch.id, "port", src_port)
        
        learn_switch_link(self, self.switches[src_dpid], dst_switch, src_port)

        print_topology(self)

        draw_topology(self)

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

        print("PACKETIN:", eth.ethertype, dp.id, in_port)

        if eth is None:
            return

        if eth.ethertype == 0x88cc:
            self._handle_lldp_receive(pkt, dp)
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