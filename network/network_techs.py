from dataclasses import dataclass


@dataclass
class NetworkTechnology:

    name: str
    # Mininet parameters (to be used at runtime)
    bw_mbps: float
    delay_ms: float
    loss_percent: float
    # descriptive parameters (to be used when designing the network)
    energy_consumption: int     # 1-5: very low, low, medium, high, very high
    range_km: float
    role: str

# Defined technologies

NET_TECHS = {

    "local": NetworkTechnology(
        name="local",
        bw_mbps=10000,
        delay_ms=0.01,
        loss_percent=0.0,
        range_km=0.001,
        energy_consumption=1,
        role="local",
    ),

    "zigbee": NetworkTechnology(
        name="zigbee",
        bw_mbps=0.25,
        delay_ms=20,
        loss_percent=2,
        range_km=0.1,
        energy_consumption=1,
        role="mesh",
    ),

    "lora": NetworkTechnology(
        name="lora",
        bw_mbps=0.05,
        delay_ms=150,
        loss_percent=3,
        range_km=15,
        energy_consumption=1,
        role="access",
    ),

    "wifi": NetworkTechnology(
        name="wifi",
        bw_mbps=100,
        delay_ms=5,
        loss_percent=1,
        range_km=0.1,
        energy_consumption=3,
        role="access",
    ),

    "fso": NetworkTechnology(
        name="fso",
        bw_mbps=1000,
        delay_ms=1280,
        loss_percent=0.01,
        range_km=400000,
        energy_consumption=4,
        role="backbone",
    ),
}
