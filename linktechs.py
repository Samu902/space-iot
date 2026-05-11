from dataclasses import dataclass
from mininet.net import Mininet


@dataclass
class NetworkTechnology:

    name: str
    # Mininet parameters
    bw_mbps: float
    delay_ms: float
    loss_percent: float
    # Logical/network parameters
    energy_profile: str
    range_type: str
    reliability_level: int
    role: str


# -- Defined link technologies

LINK_TECHS = {

    "zigbee": NetworkTechnology(
        name="zigbee",
        bw_mbps=2,
        delay_ms=20,
        loss_percent=3,
        energy_profile="very_low",
        range_type="short",
        reliability_level=3,
        role="mesh"
    ),

    "lora": NetworkTechnology(
        name="lora",
        bw_mbps=0.5,
        delay_ms=200,
        loss_percent=5,
        energy_profile="very_low",
        range_type="long",
        reliability_level=3,
        role="access"
    ),

    "wifi": NetworkTechnology(
        name="wifi",
        bw_mbps=100,
        delay_ms=5,
        loss_percent=1,
        energy_profile="high",
        range_type="medium",
        reliability_level=2,
        role="access"
    ),

    "fso": NetworkTechnology(
        name="fso",
        bw_mbps=1000,
        delay_ms=1280,
        loss_percent=0.1,
        energy_profile="medium",
        range_type="space",
        reliability_level=3,
        role="backbone"
    )
}


# -- Link creation function

def add_link(net: Mininet, a, b, tech_name: str):

    tech = LINK_TECHS[tech_name]

    net.addLink(
        a,
        b,
        bw=tech.bw_mbps,
        delay=f"{tech.delay_ms}ms",
        loss=tech.loss_percent
    )