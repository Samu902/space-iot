# =====================================================
# ROUTING ENGINE
# =====================================================

def compute_path(flow):

    # placeholder routing logic

    # sostituire compute_path() con routing reale su grafo

    # cioè:

    # shortest path
    # multi-hop mesh
    # failover
    # QoS-aware routing

    # usando networkx.

    if flow.destination == "earth":

        return [
            flow.source,
            "gw",
            "earth"
        ]

    return [
        flow.source,
        flow.destination
    ]