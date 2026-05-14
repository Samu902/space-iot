from ryu.base import app_manager

from ryu.controller import ofp_event

from ryu.controller.handler import (
    MAIN_DISPATCHER,
    CONFIG_DISPATCHER,
    set_ev_cls
)

from ryu.ofproto import ofproto_v1_3

from network.flows import FLOWS

from controller.tech_selector import select_best_technology
from controller.routing_engine import compute_path


# =====================================================
# Ryu SDN CONTROLLER
# =====================================================

class LunarQoSController(app_manager.RyuApp):

    OFP_VERSIONS = [
        ofproto_v1_3.OFP_VERSION
    ]

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.flows = FLOWS

    # =================================================
    # FLOW LOOKUP
    # =================================================

    def find_flow(self, src, dst):

        for flow in self.flows:
            if (flow.source == src and flow.destination == dst):
                return flow

        return None

    # =================================================
    # PACKET HANDLER
    # =================================================

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):

        msg = ev.msg

        datapath = msg.datapath

        # placeholder addresses
        src = "env1"
        dst = "gw"

        flow = self.find_flow(src, dst)

        if not flow:
            return

        tech = select_best_technology(flow)

        path = compute_path(flow)

        print("\n=== FLOW DETECTED ===")

        print(f"Flow: {flow.name}")

        print(f"QoS: {flow.qos.name}")

        print(f"Technology selected: {tech.name}")

        print(f"Path: {path}")


    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):

        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        match = parser.OFPMatch()

        actions = [
            parser.OFPActionOutput(
                ofproto.OFPP_CONTROLLER,
                ofproto.OFPCML_NO_BUFFER
            )
        ]

        instructions = [
            parser.OFPInstructionActions(
                ofproto.OFPIT_APPLY_ACTIONS,
                actions
            )
        ]

        mod = parser.OFPFlowMod(
            datapath=datapath,
            priority=0,
            match=match,
            instructions=instructions
        )

        datapath.send_msg(mod)

        print("Table-miss rule installed")