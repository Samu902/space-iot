from dataclasses import dataclass
from qos import (
    MONITORING_QOS,
    CONTROL_QOS,
    M2M_QOS,
    BACKBONE_QOS,
    QoSProfile
)


@dataclass
class TrafficFlow:

    name: str
    source: str
    destination: str
    qos: QoSProfile


# -- Defined flows

FLOWS = [

    TrafficFlow(
        name="environment_monitoring",
        source="env1",
        destination="gw",
        qos=MONITORING_QOS
    ),

    TrafficFlow(
        name="rover_control",
        source="earth",
        destination="rover1",
        qos=CONTROL_QOS
    ),

    TrafficFlow(
        name="rover_m2m",
        source="rover1",
        destination="rover2",
        qos=M2M_QOS
    ),

    TrafficFlow(
        name="backbone_telemetry",
        source="gw",
        destination="earth",
        qos=BACKBONE_QOS
    )
]