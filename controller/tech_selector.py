from network.linktechs import LINK_TECHS
from controller.qos_engine import evaluate_qos

def select_best_technology(flow):

    best_tech = None
    best_score = -1

    for tech in LINK_TECHS.values():

        result = evaluate_qos(flow, tech)

        score = result["score"]

        if score > best_score:

            best_score = score
            best_tech = tech

    return best_tech