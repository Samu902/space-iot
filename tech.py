TECH = {
    "zigbee": {"bw": 2, "delay": "20ms", "loss": 3},
    "lora":   {"bw": 0.5, "delay": "200ms", "loss": 5},
    "wifi":   {"bw": 100, "delay": "5ms", "loss": 1},
    "fso":    {"bw": 1000, "delay": "1ms", "loss": 0.1}
}


def add_link(net, a, b, tech):

    p = TECH[tech]

    net.addLink(
        a, b,
        bw=p["bw"],
        delay=p["delay"],
        loss=p["loss"]
    )