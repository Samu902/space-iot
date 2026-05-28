from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from controller.app import SpaceIoTController

from ryu.lib.packet import packet, ethernet, lldp


def send_lldp(src_switch):

    ofp = src_switch.ofproto
    parser = src_switch.ofproto_parser

    for port_no in src_switch.ports:

        # skip reserved ports
        if port_no > ofp.OFPP_MAX:
            continue

        pkt = packet.Packet()

        pkt.add_protocol(ethernet.ethernet(
            ethertype=0x88cc,
            dst="ff:ff:ff:ff:ff:ff", #va bene?
            src="00:00:00:00:00:01"  #va bene?
        ))

        chassis_id = lldp.ChassisID(
            subtype=lldp.ChassisID.SUB_LOCALLY_ASSIGNED,
            chassis_id=str(src_switch.id).encode()
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
            datapath=src_switch,
            buffer_id=ofp.OFP_NO_BUFFER,
            in_port=ofp.OFPP_CONTROLLER,
            actions=actions,
            data=pkt.data
        )

        src_switch.send_msg(out)


def receive_lldp(cont: SpaceIoTController, dst_switch, pkt):

    lldp_pkt = pkt.get_protocol(lldp.lldp)

    src_dpid = None
    src_port = None

    for tlv in lldp_pkt.tlvs:

        if isinstance(tlv, lldp.ChassisID):
            src_dpid = int(tlv.chassis_id.decode())

        if isinstance(tlv, lldp.PortID):
            src_port = int(tlv.port_id.decode())

    print(f"Ricevuto LLDP: s{src_dpid}:{src_port} -> s{dst_switch.id}")
    
    learn_switch_link(cont, cont.switches[src_dpid], dst_switch, src_port)

    #print_topology(cont)

    #draw_topology(cont)

    for (src, dst) in list(cont.paths.keys()):
        path = compute_path(cont, src, dst)
        if path:
            install_path(cont, src, dst, path)
