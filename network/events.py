def mesh_down(net):
    link = net.linksBetween(net.get("iot1"), net.get("iot2"))[0]
    link.intf1.ifconfig("down")
    link.intf2.ifconfig("down")


def gateway_down(net):
    gw = net.get("gw")
    for intf in gw.intfList():
        if intf.name != "lo":
            intf.ifconfig("down")