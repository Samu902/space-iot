def env_down(net):
    link = net.linksBetween(net.get("env1"), net.get("s_env"))[0]
    link.intf1.ifconfig("down")
    link.intf2.ifconfig("down")

    link = net.linksBetween(net.get("env2"), net.get("s_env"))[0]
    link.intf1.ifconfig("down")
    link.intf2.ifconfig("down")

    print("env links down")

def env_up(net):
    link = net.linksBetween(net.get("env1"), net.get("s_env"))[0]
    link.intf1.ifconfig("up")
    link.intf2.ifconfig("up")

    link = net.linksBetween(net.get("env2"), net.get("s_env"))[0]
    link.intf1.ifconfig("up")
    link.intf2.ifconfig("up")

    print("env links up")



def gateway_down(net):
    gw = net.get("gw")
    for intf in gw.intfList():
        if intf.name != "lo":
            intf.ifconfig("down")
