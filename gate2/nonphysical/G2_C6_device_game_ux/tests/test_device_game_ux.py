from gate2.nonphysical.G2_C6_device_game_ux.runtime.profile_loader import load_matrix, resolve

GAMES = ["beatlink-party", "archive-of-life-artifact-world", "pedestrian-pursuit", "anime-aggressors"]
DEVICES = ["student_14_5", "handheld_hybrid", "ds_xl_coder", "edge_io_rings"]

def test_full_matrix():
    m = load_matrix()
    assert m["protected_asset_policy"] == "no_copyrighted_music_or_anime_ip"
    for g in GAMES:
        for d in DEVICES:
            r = resolve(g, d)
            assert r["role"]
            assert r["vision"]
