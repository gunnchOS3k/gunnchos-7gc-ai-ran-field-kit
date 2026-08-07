from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def test_manual_and_fru():
    assert (ROOT / "repair_manual.md").exists()
    assert (ROOT / "fru_matrix.yaml").exists()
    text = (ROOT / "repair_manual.md").read_text(encoding="utf-8")
    assert "PHYSICAL_PENDING" in text
