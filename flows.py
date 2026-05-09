from dataclasses import dataclass
from qos import QoSProfile, MONITORING_QOS, CONTROL_QOS, M2M_QOS, BACKBONE_QOS
from linktechs import LINK_TECHS

# =====================================================
# MODELLO FLUSSO
# =====================================================

@dataclass
class TrafficFlow:

    name: str
    source: str
    destination: str
    qos: QoSProfile


# =====================================================
# FLUSSI LUNARI
# =====================================================

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


# =====================================================
# FUNZIONI DI UTILITA'
# =====================================================

def score_match(flow: TrafficFlow, tech):

    score = 0

    # bandwidth (più alto = meglio)
    if tech.bandwidth_level >= flow.qos.bandwidth_level:
        score += 1

    # latency (più basso = meglio)
    if tech.latency_ms <= flow.qos.max_latency_ms:
        score += 1

    # reliability
    if tech.reliability_level >= flow.qos.reliability_level:
        score += 1

    # power (flow deve essere compatibile)
    if tech.power_level <= flow.qos.max_power_level:
        score += 1

    return score


def validate_flow(flow):

    return {
        tech_name: score_match(flow, tech)
        for tech_name, tech in LINK_TECHS.items()
    }


def best_tech(flow):

    scores = validate_flow(flow)

    return max(scores, key=scores.get)