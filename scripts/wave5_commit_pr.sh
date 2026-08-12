#!/usr/bin/env bash
# Wave 5 DRAFT commit + PR helper — run from a shell with full access to gunnchos-device-os.
set -euo pipefail
ROOT="/Users/gunnchos/Downloads/gunnchos-7gc-research-product-spine/repos/gunnchos-device-os"
cd "$ROOT"

git checkout -B operating-cycle-2/wp-011-device-lab-wave5-ecosystem 187e39e797fa5347fe55580025afa7ba7a21eab5
git checkout -- artifacts/continuation_ix/ || true

git add \
  gunnchos_device_os/device_lab/ecosystem/ \
  gunnchos_device_os/device_lab/chaos/ \
  gunnchos_device_os/device_lab/twin/ \
  gunnchos_device_os/device_lab/scenarios/ \
  gunnchos_device_os/device_lab/cli.py \
  gunnchos_device_os/device_lab/apps/runner.py \
  gunnchos_device_os/device_lab/session.py \
  gunnchos_device_os/device_lab/TOKENS_WP011.json \
  gunnchos_device_os/device_lab/device_lab_v1/DEVICE_LAB_COMPLETION_REGISTER.yaml \
  tests/device_lab/test_wp011_wave5_ecosystem.py \
  tests/device_lab/test_wp011_wave4_dual_ring.py \
  scripts/device_lab_score_from_register.py

git status -sb
git commit -m "$(cat <<'EOF'
feat(device-lab): Wave 5 ecosystem, games, chaos, score, twin handoff

Add gunnchctl ecosystem start|status|stop|test|graph with isolated Lab vnet;
ECO-001 continuity depth plus ECO-002..010 (010 honest PARTIAL); four-game and
gunnchAI process-proof workloads; unified chaos engine; Golden G01/G05/G09 Lab
wiring; gunnchctl score from register; pre-EVT twin handoff docs. Master complete
token remains false.
EOF
)"

git push -u origin HEAD

# Stack DRAFT on #101 tip / main — prefer base main if #101 still open as draft stack note.
if gh pr view 101 --json state,isDraft,headRefName -q . >/dev/null 2>&1; then
  BASE="main"
else
  BASE="main"
fi

gh pr create --draft --base "$BASE" --head operating-cycle-2/wp-011-device-lab-wave5-ecosystem \
  --title "feat(device-lab): Wave 5 ecosystem topology, ECO, games, chaos, score" \
  --body "$(cat <<'EOF'
## Summary
- **Ecosystem CLI:** `gunnchctl ecosystem start|status|stop|test|graph|topology` with isolated Lab vnet (10.88.0.0/24).
- **ECO-001..010:** ECO-001 Student→DS-XL continuity PASS; ECO-002..009 digitally executable; ECO-010 honest PARTIAL (light simultaneous — not full soak).
- **Games + AI:** four in-tree web games via real `http.server` process proof (+ optional Godot for foot-racing sibling); gunnchAI Lab workload process.
- **Chaos engine:** process/network/storage/display/audio/AI/Ring/update/resource with inject+cleanup+evidence.
- **Golden expand:** G01 student day, G05 handheld play→dock, G09 update rollback wired through Lab.
- **Score:** `gunnchctl score` from completion register (no hardcoded 10s) + claim firewall.
- **Pre-EVT twin:** handoff schema/docs; VF4/5/6 remain PHYSICAL_PENDING.
- **Master token:** `GUNNCHDEVICE_LAB_FULL_ECOSYSTEM_DIGITAL_COMPLETE=false` (ECO-010 full soak incomplete).

## Test plan
- [ ] `PYTHONPATH=. python3 -m pytest tests/device_lab/test_wp011_wave5_ecosystem.py tests/device_lab/test_wp011_wave4_dual_ring.py -q`
- [ ] `gunnchctl ecosystem test ECO-001` and `gunnchctl score`
- [ ] Confirm draft + auto-merge off; do not merge

EOF
)"

gh pr ready --undo 2>/dev/null || true
# ensure draft
echo "PR:"; gh pr view --json url,isDraft,headRefOid,number -q .
