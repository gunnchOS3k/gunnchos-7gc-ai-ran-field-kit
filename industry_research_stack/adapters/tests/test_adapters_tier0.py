"""Tier-0 fixtures always pass without GPU/external tools."""
from industry_research_stack.adapters.sionna import SionnaAdapter
from industry_research_stack.adapters.nyusim import NyusimAdapter
from industry_research_stack.adapters.lena_ns3 import LenaNs3Adapter
from industry_research_stack.adapters.oai_flexric import OaiFlexricAdapter
from industry_research_stack.adapters.oran_sc import OranScAdapter
from industry_research_stack.adapters.open5gs import Open5gsAdapter
from industry_research_stack.adapters.camara import CamaraAdapter

ADAPTERS = [
    SionnaAdapter(),
    NyusimAdapter(),
    LenaNs3Adapter(),
    OaiFlexricAdapter(),
    OranScAdapter(),
    Open5gsAdapter(),
    CamaraAdapter(),
]


def test_all_tier0_fixtures_pass():
    for a in ADAPTERS:
        result = a.run(prefer_real=False)
        assert result.available is True
        assert result.mode == "FIXTURE"
        assert result.license
        assert result.source_url
        assert result.provenance["tier"] == 0
        assert result.provenance["physical_execution_freeze"] == "ACTIVE"
        assert result.provenance["false_claim_guard"] is True


def test_lena_not_linked_into_product():
    r = LenaNs3Adapter().run()
    assert r.payload["linked_into_product"] is False
    assert "GPL" in r.license or "GPL" in "GPL-2.0"


def test_open5gs_not_embedded():
    r = Open5gsAdapter().run()
    assert r.payload["embedded_in_product"] is False


def test_camara_no_false_real_operator():
    r = CamaraAdapter().run()
    assert r.payload["real_operator_without_credentials"] is False
    assert "REAL_OPERATOR" in r.payload["modes"]
