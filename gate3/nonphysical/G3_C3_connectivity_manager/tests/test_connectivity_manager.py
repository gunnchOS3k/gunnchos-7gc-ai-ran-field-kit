from gate3.nonphysical.G3_C3_connectivity_manager.connectivity_manager import ConnectivityManager
from gate3.nonphysical.G3_C3_connectivity_manager.providers import (
    AuthExpiredError,
    CAMARARealProvider,
    CAMARASandboxProvider,
    CapabilityMode,
    LocalMetricsProvider,
    ProviderFailureError,
    ProviderUnavailableError,
    RateLimitError,
    SimulationProvider,
)


def test_prefer_wifi():
    m = ConnectivityManager()
    m.set_link("ntn_abstracted", True, 800)
    m.set_link("wifi", True, 20)
    assert m.select().bearer == "wifi"


def test_ntn_no_real_claim():
    m = ConnectivityManager()
    claim = m.claim_boundary()
    assert claim["real_ntn_claim"] is False
    assert claim["STANDARDIZED_6G"] is False
    assert claim["CARRIER_ACCEPTED"] is False
    assert claim["RM520N_GL_NTN"] is False
    assert claim["ble_is_wan"] is False


def test_ethernet_preferred_over_wifi():
    m = ConnectivityManager()
    m.set_link("wifi", True, 20)
    m.set_link("ethernet", True, 2)
    assert m.select().bearer == "ethernet"


def test_failover_and_reconnect_and_airplane():
    m = ConnectivityManager()
    m.set_link("wifi", True, 20)
    m.set_link("cellular", True, 40)
    assert m.select().bearer == "wifi"
    fail = m.failover("wifi")
    assert fail["to"] == "cellular"
    assert fail["CARRIER_ACCEPTED"] is False
    m.set_link("wifi", True, 20)
    recon = m.reconnect()
    assert recon["ok"] is True
    assert recon["active"] == "wifi"
    air = m.set_airplane(True)
    assert air["airplane"] is True
    assert m.select() is None
    assert m.reconnect()["reason"] == "airplane"


def test_no_provider_unavailable_mode():
    m = ConnectivityManager()
    assert m.capability_mode() == CapabilityMode.UNAVAILABLE
    assert m.claim_boundary()["real_operator_claim"] is False


def test_local_metrics_simulated():
    m = ConnectivityManager(capability_provider=LocalMetricsProvider())
    assert m.capability_mode() == CapabilityMode.SIMULATED
    cap = m.get_network_capability("Connected Network Type")
    assert cap.mode == CapabilityMode.SIMULATED
    assert cap.payload["bearer"] == "wifi"


def test_simulation_failure_path():
    p = SimulationProvider(fail_next=True)
    m = ConnectivityManager(capability_provider=p)
    try:
        m.get_network_capability("Connectivity Insights")
        assert False, "expected failure"
    except ProviderFailureError:
        pass
    # subsequent call succeeds
    cap = m.get_network_capability("Connectivity Insights")
    assert cap.available is True


def test_simulation_unavailable():
    m = ConnectivityManager(capability_provider=SimulationProvider(unavailable=True))
    assert m.capability_mode() == CapabilityMode.UNAVAILABLE
    try:
        m.get_network_capability("Connectivity Insights")
        assert False
    except ProviderUnavailableError:
        pass


def test_camara_sandbox_rate_limit():
    p = CAMARASandboxProvider(rate_limited=True)
    m = ConnectivityManager(capability_provider=p)
    assert m.capability_mode() == CapabilityMode.SANDBOX
    assert m.claim_boundary()["real_operator_claim"] is False
    try:
        m.get_network_capability("Connectivity Insights")
        assert False
    except RateLimitError:
        pass


def test_camara_sandbox_auth_expiry():
    p = CAMARASandboxProvider(auth_expired=True)
    m = ConnectivityManager(capability_provider=p)
    try:
        m.get_network_capability("Simple Edge Discovery")
        assert False
    except AuthExpiredError:
        pass


def test_camara_real_without_credentials_never_real():
    p = CAMARARealProvider(credentials=None)
    m = ConnectivityManager(capability_provider=p)
    assert m.capability_mode() == CapabilityMode.UNAVAILABLE
    claim = m.claim_boundary()
    assert claim["real_operator_claim"] is False
    try:
        m.get_network_capability("Quality on Demand")
        assert False
    except ProviderUnavailableError:
        pass


def test_camara_real_with_credentials():
    p = CAMARARealProvider(
        credentials={"client_id": "cid", "client_secret": "sec", "operator": "lab-op"}
    )
    m = ConnectivityManager(capability_provider=p)
    assert m.capability_mode() == CapabilityMode.REAL_OPERATOR
    assert m.claim_boundary()["real_operator_claim"] is True
    cap = m.get_network_capability("Quality on Demand")
    assert cap.mode == CapabilityMode.REAL_OPERATOR


def test_camara_real_auth_expiry_and_rate_limit():
    p = CAMARARealProvider(
        credentials={"client_id": "cid", "client_secret": "sec"},
        auth_expired=True,
    )
    try:
        p.get_capability("Connectivity Insights")
        assert False
    except AuthExpiredError:
        pass
    p2 = CAMARARealProvider(
        credentials={"client_id": "cid", "client_secret": "sec"},
        rate_limited=True,
    )
    try:
        p2.get_capability("Connectivity Insights")
        assert False
    except RateLimitError:
        pass
