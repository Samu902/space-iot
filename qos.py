from dataclasses import dataclass

@dataclass
class QoSProfile:

    name: str
    min_bandwidth_mbps: float
    max_latency_ms: float
    reliability_level: int
    power_profile: str


# -- QoS standard profiles

MONITORING_QOS = QoSProfile(
    name="monitoring",
    min_bandwidth_mbps=0.1,
    max_latency_ms=500,
    reliability_level=3,
    power_profile="very_low"
)

CONTROL_QOS = QoSProfile(
    name="control",
    min_bandwidth_mbps=10,
    max_latency_ms=50,
    reliability_level=3,
    power_profile="medium"
)

M2M_QOS = QoSProfile(
    name="m2m",
    min_bandwidth_mbps=1,
    max_latency_ms=200,
    reliability_level=2,
    power_profile="low"
)

BACKBONE_QOS = QoSProfile(
    name="backbone",
    min_bandwidth_mbps=100,
    max_latency_ms=1280,
    reliability_level=3,
    power_profile="medium"
)