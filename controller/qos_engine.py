from network.linktechs import NetworkTechnology
from network.flows import TrafficFlow


# =====================================================
# QoS SCORE
# =====================================================

def evaluate_qos(flow: TrafficFlow, tech: NetworkTechnology):

    score = 0

    details = {}

    # =================================================
    # BANDWIDTH
    # =================================================

    bandwidth_ok = (
        tech.bw_mbps >= flow.qos.min_bandwidth_mbps
    )

    details["bandwidth"] = bandwidth_ok

    if bandwidth_ok:
        score += 1

    # =================================================
    # LATENCY
    # =================================================

    latency_ok = (
        tech.delay_ms <= flow.qos.max_latency_ms
    )

    details["latency"] = latency_ok

    if latency_ok:
        score += 1

    # =================================================
    # RELIABILITY
    # =================================================

    reliability_ok = (
        tech.reliability_level >= flow.qos.reliability_level
    )

    details["reliability"] = reliability_ok

    if reliability_ok:
        score += 1

    # =================================================
    # POWER PROFILE
    # =================================================

    power_ok = (
        tech.energy_profile == flow.qos.power_profile
    )

    # è troppo rigida.

    # Perché:

    # very_low dovrebbe soddisfare anche low
    # low potrebbe soddisfare medium

    # Più avanti puoi usare ranking:

    # POWER_LEVELS = {
    #     "very_low": 1,
    #     "low": 2,
    #     "medium": 3,
    #     "high": 4
    # }

    # e confrontare numericamente.

    details["power"] = power_ok

    if power_ok:
        score += 1

    # =================================================
    # FINAL RESULT
    # =================================================

    return {
        "score": score,
        "details": details
    }


# =====================================================
# QoS VALIDATION
# =====================================================

def is_qos_satisfied(flow: TrafficFlow, tech: NetworkTechnology):

    result = evaluate_qos(flow, tech)

    return result["score"] >= 3