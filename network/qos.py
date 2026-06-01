from dataclasses import dataclass


@dataclass
class QoSProfile:

    name: str
    min_bw_mbps: float
    max_delay_ms: float
    max_loss_percent: float
    max_energy_consumption: int     # 1-5: very low, low, medium, high, very high

# -- QoS standard profiles

QOS_PROFILES = {

    "monitoring": QoSProfile(
        name="monitoring",
        min_bw_mbps=0.1,
        max_delay_ms=500,
        max_loss_percent=3,
        max_energy_consumption=1
    ),

    "control": QoSProfile(
        name="control",
        min_bw_mbps=10,
        max_delay_ms=50,
        max_loss_percent=3,
        max_energy_consumption=3
    ),

    "m2m": QoSProfile(
        name="m2m",
        min_bw_mbps=1,
        max_delay_ms=200,
        max_loss_percent=2,
        max_energy_consumption=2
    ),

    "backbone": QoSProfile(
        name="backbone",
        min_bw_mbps=100,
        max_delay_ms=1280,
        max_loss_percent=3,
        max_energy_consumption=3
    )

}
