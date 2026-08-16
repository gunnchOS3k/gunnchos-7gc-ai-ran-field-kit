# REPRODUCE — Digital Ecosystem Baseline V1

Generated: 2026-08-16T16:15:56Z

## Fetch accepted mains

```bash
REPOS_ROOT=/Users/gunnchos/Downloads/gunnchos-7gc-research-product-spine/repos
for r in gunnchos-device-os gunnchAI3k waike-research-ops gunnchos-7gc-ai-ran-field-kit \
  gunnchos-hardware-industrial-design edge-io-measurement-node anime-aggressors \
  pedestrian-pursuit archive-of-life-artifact-world beatlink-party 7gc-digital-twin \
  spectrumx-ai-ran-gary ntn-resilience-sim readygary-6g-beam-selection \
  gunnchos-gpu-nr-baseband-platform gunnchos-emergent-service-intent-protocols; do
  git -C "$REPOS_ROOT/$r" fetch origin --prune
  git -C "$REPOS_ROOT/$r" rev-parse origin/main
done
```

## Confirm target PR merges

```bash
gh pr view 116 --repo gunnchOS3k/gunnchos-device-os --json state,mergeCommit,mergedAt
gh pr view 36 --repo gunnchOS3k/gunnchAI3k --json state,mergeCommit,mergedAt
gh pr view 38 --repo gunnchOS3k/gunnchAI3k --json state,mergeCommit,mergedAt
gh pr view 48 --repo gunnchOS3k/waike-research-ops --json state,mergeCommit,mergedAt
gh pr view 80 --repo gunnchOS3k/gunnchos-7gc-ai-ran-field-kit --json state,mergeCommit,mergedAt
```

## Prove gunnchAI dual-preserve

```bash
AI=$REPOS_ROOT/gunnchAI3k
git -C "$AI" merge-base --is-ancestor 2eb24aeb1cc22f129deb57482e1c27105bcd1703 origin/main && echo mastery_ancestor=YES
git -C "$AI" show origin/main:artifacts/waike-mastery/LARGER_SAMPLE_REAL_RUNTIME.json | jq '{items_attempted,frozen_baseline,does_not_alter_frozen_baseline,used_instructor_keys_during_solve}'
git -C "$AI" show origin/main:artifacts/waike-mastery/BASELINE_INTACT_PROOF.json | jq .
git -C "$AI" show origin/main:artifacts/waike-mastery/AI_WAIKE_MASTERY_EVAL.json | jq '{discoverable: .corpus.discoverable_courses, no_key_leak: .tokens.WAIKE_AI_NO_KEY_LEAK_PASS, mastery_pass: .tokens.WAIKE_AI_DIGITAL_MASTERY_PASS}'
git -C "$AI" ls-tree -r --name-only origin/main -- src/user-ready/ | rg 'cowrite|custom_agents|computer_use|audio_overview|companion'
```

## Enumerate open PRs

```bash
for repo in gunnchOS3k/gunnchos-device-os gunnchOS3k/gunnchAI3k gunnchOS3k/waike-research-ops \
  gunnchOS3k/gunnchos-7gc-ai-ran-field-kit gunnchOS3k/edge-io-measurement-node \
  gunnchOS3k/anime-aggressors gunnchOS3k/pedestrian-pursuit \
  gunnchOS3k/archive-of-life-artifact-world gunnchOS3k/beatlink-party \
  gunnchOS3k/7gc-digital-twin gunnchOS3k/spectrumx-ai-ran-gary \
  gunnchOS3k/ntn-resilience-sim gunnchOS3k/readygary-6g-beam-selection \
  gunnchOS3k/gunnchos-emergent-service-intent-protocols gunnchOS3k/gunnchos-research-portal; do
  gh pr list --repo "$repo" --state open --limit 50
done
```

## Derived percent

Only from `COMPLETION_LEDGER.json` → `totals.DIGITAL_CONTROLLABLE_COMPLETION_PERCENT`.
