from dataclasses import dataclass


# =====================================================
# REQUISITI DI COMUNICAZIONE
# =====================================================

@dataclass
class QoSProfile:

    bandwidth: str
    # invece di "low / medium / tolerant"
    max_latency: str  # es: "10ms", "100ms", "1.28s"
    reliability: str
    power_consumption: str


# =====================================================
# PROFILI QOS STANDARD
# =====================================================

MONITORING_QOS = QoSProfile(
    bandwidth="low",
    max_latency="200ms",
    reliability="very_high",
    power_consumption="very_low"
)

CONTROL_QOS = QoSProfile(
    bandwidth="medium",
    max_latency="10ms",
    reliability="high",
    power_consumption="medium"
)

M2M_QOS = QoSProfile(
    bandwidth="low",
    max_latency="100ms",
    reliability="high",
    power_consumption="low"
)

BACKBONE_QOS = QoSProfile(
    bandwidth="very_high",
    max_latency="1.28s",
    reliability="very_high",
    power_consumption="medium"
)