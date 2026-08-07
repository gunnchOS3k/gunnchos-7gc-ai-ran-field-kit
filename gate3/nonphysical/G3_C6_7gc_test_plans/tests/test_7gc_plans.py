from pathlib import Path
try:
    import yaml
except ImportError:
    yaml = None

ROOT = Path(__file__).resolve().parents[1]

def test_plans_and_configs_exist():
    plan = yaml.safe_load((ROOT / "7gc_test_plan.yaml").read_text(encoding="utf-8"))
    for suite in plan["suites"]:
        cfg = ROOT / suite["sim_config"]
        assert cfg.exists(), suite["sim_config"]
