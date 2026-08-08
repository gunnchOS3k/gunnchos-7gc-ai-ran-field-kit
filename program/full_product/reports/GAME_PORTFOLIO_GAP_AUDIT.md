# GAME PORTFOLIO GAP AUDIT

Updated: 2026-08-08T00:09:01Z  
Mode: `FULL_PRODUCT_ENTIRETY_MODE`  
Repos audited:

| Game | Repo path |
|------|-----------|
| Anime Aggressors | `/Users/gunnchos/Downloads/gunnchos-7gc-research-product-spine/repos/anime-aggressors` |
| Pedestrian Pursuit | `/Users/gunnchos/Downloads/gunnchos-7gc-research-product-spine/repos/pedestrian-pursuit` |
| Archive of Life | `/Users/gunnchos/Downloads/gunnchos-7gc-research-product-spine/repos/archive-of-life-artifact-world` |
| BeatLink Party | `/Users/gunnchos/Downloads/gunnchos-7gc-research-product-spine/repos/beatlink-party` |

Cross-matrix: `program/full_product/game_release_matrix.yaml` (all four remain `POST_G2_PRE_ALPHA`, `content_complete: false`, `rc_digital: false`).

## Forbidden claims (audit rules)

Do **not** treat any of the following as content-complete:

- one stage / one map / one greybox layout
- one racer / one character skin / one proxy GLB set
- one cup track data file without authored presentation
- fixture taxonomy presented as global live coverage
- MVP party roles presented as five distinct launch modes

---

## 1) Anime Aggressors (Godot)

**Engine path of record:** `anime-aggressors/game-godot/` (Godot 4).  
Legacy/web/Unity paths exist under the same repo (`apps/`, `unity/`, `packages/`) and are **not** counted as the ship path for this audit.

### Fighters

| Metric | Count | Evidence |
|--------|------:|----------|
| Roster IDs in `game-godot/data/fighters/roster.json` | **7** | ember-vale, rook-ironside, juno-spark, kaia-windrow, nix-calder, orion-vell, vesper-nyx |
| Per-fighter JSON + animation manifest | **7 / 7** | `data/fighters/*` |
| Per-fighter move lists (23 moves each) | **7 / 7** unique file hashes | `data/moves/*.json` |
| Distinct combat-stat signatures | **7 / 7** | run/dash/jump/fall/air + damage/shield multipliers differ |
| Distinct archetypes / elements / CPU tags | **7 / 7** | e.g. Rushdown/Flame, Bruiser/Impact, Trickster/Void |
| `productionStatus` | **proxy × 7** | none are final art |
| Final authored GLB + animation clips | **0 / 7** | known limitation: shared geometric proxy GLBs |

**Differentiation verdict:** Data-level differentiation is **present** (stats, move data, archetypes, CPU tags). Presentation-level differentiation is **not** launch-ready (proxy art). Matrix field `fighters_fully_differentiated` should move from `UNKNOWN_AUDIT_REQUIRED` → **`DATA_YES_ART_NO`**.

### Stages

| Metric | Count | Notes |
|--------|------:|-------|
| Production stage IDs | **3** | `training-grid`, `skyline-arena`, `neon-rooftops` |
| Stage JSON with platforms/blast/spawns | **3** | distinct layouts (flat / threePlatform / casual) |
| Authored stage art / hazards | **0** | greybox ColorRect platforms only |
| Stage launch target in matrix | **ADR_REQUIRED** | undefined |

**Forbidden:** calling the 3 greybox stages content-complete.

### Modes

| Mode | Status |
|------|--------|
| Versus (local P1/P2 or P1 vs CPU) | Implemented (`ModeSelectScene` → ruleset → fight) |
| Training (+ dummy modes: idle/shield/jump/attack/cpu/di_in/di_out) | Implemented |
| Arcade / story / tournament / online lobby | **Missing** from Godot mode select |

Modes complete for launch matrix: **false** (2 modes shipped; competitive suite incomplete).

### AI

| Item | Status |
|------|--------|
| CPU controller | Implemented — 4 levels (`cpu_controller.gd`) |
| Archetype tags used at level 4 | Partial (zoner/rushdown/acrobat strings; fighter tags are broader: tank, trickster, etc.) |
| Competitive balance / tuning | Blocked as P2 in `core_implementation_status.json` |
| Matrix `competitive_ai` | **PARTIAL** (honest) |

### Online

| Item | Status |
|------|--------|
| Godot netplay / lobby / rollback transport | **Not implemented** |
| Web-package local rollback harness | Exists under `packages/rollback` (legacy/web track); **not** Godot RC online |
| Roadmap online lobby (A5) / online playtest (B6) | Not started |
| Matrix `online` | **NOT_RC** |

### AA blockers (content / feature)

1. Final fighter art + animations (P1).
2. Stage art beyond greybox; launch stage count undefined.
3. Online / rollback netplay on ship path.
4. Mode suite beyond Versus + Training.
5. CPU competitive tuning.

### Proposed launch-content ADR (AA) — undefined today

| ID (proposed) | Decision | Proposed value | Rationale |
|---------------|----------|----------------|-----------|
| **ADR-GAME-AA-001** | Launch playable fighters | **7** (all roster) | Already defined; require art-differentiated, not proxy-only |
| **ADR-GAME-AA-002** | Launch stages | **6** (5 competitive + 1 training) | 3 greybox ≠ launch; industry-floor for platform-fighter shelf presence |
| **ADR-GAME-AA-003** | Launch modes | Versus, Training, **Local Free-for-all or Stocks variants via ruleset**, Online private lobby | Online required for RC digital |
| **ADR-GAME-AA-004** | Online RC bar | Private lobby 1v1 rollback, desync tools, playtest pass | Matches existing roadmap B-track |

---

## 2) Pedestrian Pursuit

**Engine:** Godot (`project.godot` at repo root).

### Racers

| Metric | Count | Evidence |
|--------|------:|----------|
| Named runners in `data/racers/runner_roster.json` | **8** | Dash Reed, Nova Quill, Sierra Flux, Mira Lane, Bolt Harbor, Zig Riven, Solen Pike, Kai Volt |
| Distinct archetypes | **8** | all_terrain, sprinter, parkour, endurance, uphill, trick, cornering, kinetic |
| Visual/personality fields | Present (silhouette, gait scales, poses) | Data-complete for identity |
| Legacy single-racer `data/racers/dash.json` | 1 | Test/balanced stats file — **not** a second roster |
| Matrix `racers_launch_count` | **ADR_REQUIRED** | undefined |

Race spawn uses **1 player + 3 AI** (`RaceScene.gd`), drawn from the 8-profile roster.

**Forbidden:** calling a single racer or the legacy `dash` entry content-complete.

### Tracks

| Metric | Count | Notes |
|--------|------:|-------|
| Track JSON files | **5** | verdant, cloverwind, prism, emberkeep, sneaker_city |
| Cup-listed tracks (`sole_surge_cup`) | **4** | path_points + checkpoints present |
| Legacy scene-authored track | **1** | `scenes/tracks/SneakerCitySprintway.tscn` only; **0** path_points in JSON |
| Distinct themes among cup tracks | **4** | cascade_garden, windy_ranch, prism_void, ember_fortress |
| Authored art / unique mesh courses | Procedural `CourseTrack.gd` builder | Functional courses, not art-complete |
| Matrix `tracks_launch_count` | **ADR_REQUIRED** | undefined |

**Forbidden:** calling one map (or only Sneaker City) content-complete.

### Items / loadout

| Category | Count | IDs |
|----------|------:|-----|
| Items | **3** | lace_trap, sole_shield, turbo_toes |
| Shoes | **3** | starter_soles, grip_soles, speed_sneakers |
| Cups | **1** | sole_surge_cup |

### Modes

| Mode | Status |
|------|--------|
| Single race | Implemented |
| Cup / grand prix (Sole Surge) | Implemented |
| Time trial / multiplayer online / ghost race | **Not found** |

### AI

| Item | Status |
|------|--------|
| Path-following AI racers | Implemented (`AIPathFollower` + `AIRacerController`) |
| Concurrent AI on course | **3** |
| Per-archetype AI strategies / difficulty tiers | **Thin** — shared path follower + `speed_multiplier` (~0.88); not competitive mastery AI |
| Matrix / AI capability | `pedestrian_ai_racers: PARTIAL` |

### PP blockers

1. Launch racer/track counts not ADR-frozen.
2. Track presentation is data-built primitives, not content-complete courses.
3. Item/shoe pools are slice-sized (3/3).
4. AI is path-follow, not differentiated racer AI.
5. No online / ghost / time-trial modes.

### Proposed launch-content ADR (PP) — undefined today

| ID (proposed) | Decision | Proposed value | Rationale |
|---------------|----------|----------------|-----------|
| **ADR-GAME-PP-001** | Launch racers | **8** | Roster already authored; freeze as launch floor |
| **ADR-GAME-PP-002** | Launch tracks | **8** (2 cups × 4) | 4 cup tracks exist; double for launch shelf without claiming one map done |
| **ADR-GAME-PP-003** | Launch items | **8** | Expand beyond 3-item slice |
| **ADR-GAME-PP-004** | Launch modes | Single, Cup, Time Trial | Online deferred unless RC requires it |
| **ADR-GAME-PP-005** | AI bar | 3 difficulty tiers + archetype bias | Path-follow alone ≠ competitive AI |

---

## 3) Archive of Life (artifact world)

**Engine:** Vite/TS web (`src/`, Capacitor Android shell present).

### Biomes / regions

| Layer | Count | Status breakdown |
|-------|------:|------------------|
| Playable regions (`public/data/bundles/regions.json`) | **7** | 1 hub (museum) + 5 explore + 1 expedition |
| Region biome tags | museum, savanna, forest, wetland, coastal, fossil_bed, ancient_swamp | Hub + 6 expedition biomes |
| Coverage biome registry | **11** | represented 6 · partial 3 · not_yet_ingested 1 · missing 1 |
| Ecoregion registry | **4** | partial 3 · not_yet_ingested 1 |

Playable regions: `museum`, `savanna`, `forest`, `wetland`, `coastal`, `fossil_site`, `indiana_ancient_swamp`.

Coverage gaps: **polar_ice = missing**; **subterranean_cave = not_yet_ingested**; marine/atmospheric/urban only **partial**.

**Forbidden:** claiming biome/ecoregion registries are globally covered.

### Taxonomy coverage (fixture vs live)

| Dataset | Count | Claim honesty |
|---------|------:|---------------|
| Gate1 scientific fixture organisms | **2** | Explicitly `fixture_sample_not_complete_coverage` |
| Hero species bundle | **23** | All tagged `tier: hero` / representationTier **6**; COL IDs include `MOCK-COL-*` |
| Search index entries | **39** | Curated snapshot, not global COL |
| Species IDs referenced by regions | **22** unique | Subset of playable content |
| ArchiveDex profiles | **10** | Partial catalog UI |
| Live adapters | COL / GBIF / NASA EONET / PBDB paths with fixture fallback | Live when reachable; Smithsonian **fixture unavailable** (not live) |
| Matrix `taxonomy_scale` | **FIXTURE_AND_ADAPTER_NOT_GLOBAL** | Confirmed |

Representation model in code is tiers **0–6** (Archive record → Hero taxon), not the coarser R/E/F labels in `game_release_matrix.yaml`. Map for program language:

| Program shorthand | Code tiers | Launch honesty |
|-------------------|------------|----------------|
| R_Record | 0–1 | Fixture/search snapshots exist; not global |
| E_Encounter | 2–4 | Region-mapped playable set ~22–23 taxa |
| F_Flagship | 5–6 | 23 hero taxa (authored), not Earth-complete |

### Companion

| Capability | Status |
|------------|--------|
| Lifeling companion state + UI | Implemented (`companionUI.ts`, `game/companion.ts`) |
| Progression (XP, level, bond, traits) | Implemented (`companionProgression.ts`) |
| Full trait economy / long-tail content | Partial (16 traits in game-config) |

### Journal / notebook

| Capability | Status |
|------------|--------|
| Field notebook entries | Implemented (`notebookUI.ts`) |
| Provenance citations on collect | Implemented (tests assert license/citation round-trip) |
| Sources & evidence panel (live/cached/fixture banners) | Implemented — truthful fixture labeling |

### Archive blockers

1. Taxonomy is **not** global; fixture + curated snapshots + adapters.
2. Biome/ecoregion coverage incomplete (polar missing; several partial).
3. Hero/MOCK provenance must not be sold as live Catalogue of Life totality.
4. Companion/journal loops exist but content depth is expedition-scale, not planet-scale.

### Proposed launch-content ADR (Archive) — undefined today

| ID (proposed) | Decision | Proposed value | Rationale |
|---------------|----------|----------------|-----------|
| **ADR-GAME-AOL-001** | Launch playable regions | **12** (hub + 11 biomes aligning registry) | Close polar + subterranean + deepen marine |
| **ADR-GAME-AOL-002** | Launch encounter taxa (E) | **≥ 120** provenanced | 23 heroes ≠ encounter shelf |
| **ADR-GAME-AOL-003** | Launch flagship taxa (F) | **≥ 24** | Keep ~current hero set, no MOCK-COL in player-facing citations without label |
| **ADR-GAME-AOL-004** | Live vs fixture policy | UI must label fixture/cached/live; no completeness claim | Already coded — freeze as launch rule |
| **ADR-GAME-AOL-005** | Companion + journal RC | Progression + provenance notebook required | Systems exist; content volume ADR-bound |

---

## 4) BeatLink Party

**Engine:** Node/pnpm monorepo (`apps/server`, `apps/web`, `packages/game-engine`, `packages/shared`).

### Room lifecycle

| Phase / action | Status |
|----------------|--------|
| create → lobby | Implemented |
| join players (max **6**) | Implemented |
| join audience (max **20**) | Implemented |
| song_select → calibrating → countdown → playing → results | Implemented (`stateMachine.ts`) |
| rematch | Implemented (`rematchRound`) |
| host migration / token reclaim | Implemented |
| close / expire (TTL **2h**) | Implemented |
| Redis/Postgres persistence | **Not** (in-memory MVP) |

Lifecycle for MVP party loop: **functional**. Production durability: **not RC**.

### Five required modes (matrix)

| Required mode | In repo as distinct mode? | Closest reality |
|---------------|---------------------------|-----------------|
| **BeatTap** | Partial | Role `beat_tapper` + `scoreBeatTap` inside one party round |
| **CallAndResponse** | **No** | Only vocal prompt text “Call and response!” in demo beatmaps; roadmap Phase 7 |
| **Karaoke** | Partial | Prompt-phase karaoke (`karaoke.ts`); no mic pitch detection; placeholder lyrics |
| **BandRoles** | **No** | Three MVP roles only; “Band Room” is future roadmap |
| **PredictionTrivia** | **No** | No mode/types/tests |

MVP roles present: `beat_tapper`, `vocalist`, `hype_captain` — **roles ≠ five launch modes**.  
`modes_complete: false` — confirmed. Honest mode score: **~2/5 partial, 0/5 fully distinct**.

### Music rights pipeline

| Path | Status |
|------|--------|
| Approved demo catalog | **3** songs / **3** beatmaps (`demo_generated`) |
| Link resolver (metadata only, no rip) | Implemented |
| Playback status taxonomy | Implemented (`PLAYABLE_APPROVED` … `BLOCKED_BY_POLICY`) |
| User upload + rights attestation | Planned (Phase 3) |
| Licensed packs / lyric licensing / platform SDKs | Future |
| Matrix `music_rights_pipeline` | **PARTIAL** |

### Audience

| Capability | Status |
|------------|--------|
| Audience seats separate from players | Implemented |
| Influence (hype/vote) + cooldown + mute/sandbox | Implemented |
| Soft cap per round | Implemented |
| Event-scale crowd (100+) | Design-only (GDD future) |

### BeatLink blockers

1. Five matrix modes not implemented as selectable modes.
2. Music rights path stops at demo catalog + metadata resolver.
3. Karaoke is prompt/timing, not licensed lyrics + pitch.
4. Room state is in-memory only.
5. Audience is moderated spectator, not a complete event product.

### Proposed launch-content ADR (BeatLink) — undefined today

| ID (proposed) | Decision | Proposed value | Rationale |
|---------------|----------|----------------|-----------|
| **ADR-GAME-BL-001** | Launch modes | Exactly the five matrix modes as first-class selectable modes | Roles inside one round do not satisfy matrix |
| **ADR-GAME-BL-002** | Approved catalog floor | **≥ 12** rights-cleared tracks | 3 demos ≠ launch music shelf |
| **ADR-GAME-BL-003** | Rights pipeline RC | Catalog + user-upload attestation + NEEDS_LICENSE UX | No platform ripping ever |
| **ADR-GAME-BL-004** | Audience RC | 20 seats, influence, host moderation | Already coded; freeze as floor |
| **ADR-GAME-BL-005** | Room persistence | Redis (or equivalent) for RC | In-memory forbidden for operate |

---

## Portfolio scoreboard (honest)

| Game | Content floor | Feature floor | Content-complete? | Feature-complete? | RC digital? |
|------|---------------|---------------|-------------------|-------------------|-------------|
| Anime Aggressors | 7 fighters (data), 3 greybox stages | Versus+Training, partial CPU, no online | **No** | **No** | **No** |
| Pedestrian Pursuit | 8 racers, 4 cup tracks (+1 legacy), 3 items | Single+Cup, thin AI | **No** | **No** | **No** |
| Archive of Life | 7 regions, ~23 heroes, fixture≠global | Companion+journal+adapters | **No** | **No** | **No** |
| BeatLink Party | 3 demo songs; 3 roles ≠ 5 modes | Room+audience+partial rights | **No** | **No** | **No** |

## Open ADRs required before Beta content-complete claims

1. **ADR-GAME-AA-002** — stage launch count (propose **6**).
2. **ADR-GAME-PP-001 / PP-002** — racers **8**, tracks **8**.
3. **ADR-GAME-AOL-001 / AOL-002** — regions **12**, encounter taxa **≥120**.
4. **ADR-GAME-BL-001 / BL-002** — five modes first-class; catalog **≥12**.

Until those ADRs exist and evidence meets them, `game_release_matrix.yaml` must keep `content_complete: false` and must not describe any single stage/map/racer as launch content.

## Evidence roots (Godot / data)

- AA fighters: `anime-aggressors/game-godot/data/fighters/`, moves: `.../data/moves/`, stages: `.../data/stages/`, CPU: `.../scripts/fighters/cpu_controller.gd`, status: `.../data/gameplay/core_implementation_status.json`
- PP racers/tracks/items: `pedestrian-pursuit/data/`, race wiring: `.../scripts/race/RaceScene.gd`, AI: `.../scripts/ai/`
- Archive regions/biomes: `archive-of-life-artifact-world/public/data/bundles/regions.json`, `.../coverage/biome_registry.json`, companion/journal: `src/ui/companionUI.ts`, `src/ui/notebookUI.ts`
- BeatLink rooms/modes/rights: `beatlink-party/apps/server/src/rooms/RoomManager.ts`, `packages/shared/src/types.ts`, `content/songs/approved-demo-catalog.json`, `docs/MUSIC_COMPLIANCE.md`, `docs/ROADMAP.md`
