from gate3.nonphysical.G3_C5_threat_models.execute_threat_tests import listed_tests

def test_threats_have_tests():
    tests = listed_tests()
    assert len(tests) >= 5
    assert all("::" in t or t.endswith(".py") or "test_" in t for t in tests)
