from gate3.nonphysical.G3_C3_connectivity_manager.connectivity_manager import ConnectivityManager

def test_prefer_wifi():
    m = ConnectivityManager()
    m.set_link("ntn_abstracted", True, 800)
    m.set_link("wifi", True, 20)
    assert m.select().bearer == "wifi"

def test_ntn_no_real_claim():
    m = ConnectivityManager()
    assert m.claim_boundary()["real_ntn_claim"] is False
