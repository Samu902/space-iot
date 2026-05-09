from dataclasses import dataclass
from mininet.net import Mininet


# =====================================================
# MODELLO TECNOLOGIA
# =====================================================

@dataclass
class LinkTechnology:

    name: str

    # =========================
    # PARAMETRI FISICI (Mininet)
    # =========================
    bw_mbps: float
    delay_ms: float
    loss_percent: float

    # =========================
    # PROPRIETÀ DI SISTEMA
    # =========================
    energy_profile: str     # low / medium / high
    range_type: str         # short / medium / long / space
    reliability_level: int  # 1-3

    # =========================
    # RUOLO NELLA RETE
    # =========================
    role: str               # mesh / access / backbone


# =====================================================
# DATABASE TECNOLOGIE LINK
# =====================================================

LINK_TECHS = {

    "zigbee": LinkTechnology(
        name="zigbee",
        bw_mbps=2,
        delay_ms=20,
        loss_percent=3,

        energy_profile="very_low",
        range_type="short",
        reliability_level=3,

        role="mesh"
    ),

    "lora": LinkTechnology(
            name="lora",
        bw_mbps=0.5,
        delay_ms=200,
        loss_percent=5,

        energy_profile="very_low",
        range_type="long",
        reliability_level=3,

        role="access"
    ),

    "wifi": LinkTechnology(
        name="wifi",
        bw_mbps=100,
        delay_ms=5,
        loss_percent=1,

        energy_profile="high",
        range_type="medium",
        reliability_level=2,

        role="access"
    ),

    "fso": LinkTechnology(
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


# =====================================================
# CREAZIONE LINK
# =====================================================

def add_link(net: Mininet, a, b, tech_name: str):

    tech = LINK_TECHS[tech_name]

    net.addLink(
        a,
        b,
        bw=tech.bw_mbps,
        delay=f"{tech.delay_ms}ms",
        loss=tech.loss_percent
    )