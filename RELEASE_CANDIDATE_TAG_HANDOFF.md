# Release Candidate Tag Handoff

Status: `BLOCKED_USER_APPROVAL` — do not push tags until Edmund approves, PRs merge, and required CI is green.

## Proposed tags

```text
oulu-emergent-protocols-v0.2.0-rc.1
nr-baseband-platform-v0.2.0-rc.1
gates-4-6-control-v0.2.0-rc.1
```

## Preconditions

1. Corresponding draft PR reviewed by Edmund
2. Required CI green on the merge commit
3. Branch merged to default (`main` / `master`)
4. Explicit Edmund approval to tag

## Commands (do not run until approved)

```bash
# Field-kit
git checkout master && git pull
git tag -a gates-4-6-control-v0.2.0-rc.1 -m "Gates 4-6 control plane RC1"
# git push origin gates-4-6-control-v0.2.0-rc.1

# Oulu
git checkout main && git pull
git tag -a oulu-emergent-protocols-v0.2.0-rc.1 -m "Oulu emergent protocols RC1"
# git push origin oulu-emergent-protocols-v0.2.0-rc.1

# NVIDIA
git checkout main && git pull
git tag -a nr-baseband-platform-v0.2.0-rc.1 -m "NR baseband platform RC1"
# git push origin nr-baseband-platform-v0.2.0-rc.1
```

DOI / Zenodo deposit remain `GATE5_DOI_PENDING` until an actual deposit exists.
