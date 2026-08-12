from pathlib import Path
import ast

root = Path("/Users/gunnchos/Downloads/gunnchos-7gc-research-product-spine/repos/gate-worktrees/device-os-wp-011r")
fg = root / "gunnchos_device_os/device_lab/interactive_guest_four_games.py"
text = fg.read_text()

# Replace _hot_patch_guest_agent to prefer file_put
old_hp_start = text.find("def _hot_patch_guest_agent(session: Any, repo_root: Path) -> dict[str, Any]:")
old_hp_end = text.find("\ndef _deploy_bundle_via_9p(", old_hp_start)
if old_hp_start < 0 or old_hp_end < 0:
    raise SystemExit(f"hot_patch bounds missing {old_hp_start} {old_hp_end}")

new_hp = '''def _hot_patch_guest_agent(session: Any, repo_root: Path) -> dict[str, Any]:
    """Push process_run/file_put capable agent without full reprovision.

    Prefer file_put chunks (avoids guest_bash_timeout on large base64 printf loops).
    Restarting the agent drops the virtio-serial session briefly — caller must
    re-ping after this returns.
    """
    import base64

    agent_src = (
        repo_root
        / "os_build"
        / "device_lab_interactive_guest"
        / "debian_cloud"
        / "guest_agent"
        / "gunnchos_guest_agent.py"
    )
    raw = agent_src.read_bytes()
    _agent_call(
        session,
        "process_run",
        argv=["bash", "-lc", "rm -f /tmp/ga_new.py; mkdir -p /opt/gunnchos/bin"],
        timeout_sec=20.0,
    )
    chunk = 24_000
    put_errors: list[dict[str, Any]] = []
    for i in range(0, len(raw), chunk):
        piece = raw[i : i + chunk]
        put = _agent_call(
            session,
            "file_put",
            path="/tmp/ga_new.py",
            bytes_b64=base64.b64encode(piece).decode("ascii"),
            append=(i > 0),
            timeout_sec=30.0,
        )
        if not put.get("ok"):
            put_errors.append({"offset": i, "put": put})
            break
    if put_errors:
        # Fallback to legacy bash base64 path.
        b64 = base64.b64encode(raw).decode("ascii")
        _guest_bash(session, "rm -f /tmp/ga_new.b64 /tmp/ga_new.py; : > /tmp/ga_new.b64", timeout_sec=20)
        for i in range(0, len(b64), 8000):
            part = b64[i : i + 8000]
            _guest_bash(
                session,
                f"printf '%s' '{part}' >> /tmp/ga_new.b64",
                timeout_sec=20,
                name=f"ga-chunk-{i}",
            )
        decode = _guest_bash(
            session,
            "set -e; base64 -d /tmp/ga_new.b64 > /tmp/ga_new.py; wc -c /tmp/ga_new.py",
            timeout_sec=60,
            name="ga-decode",
        )
    else:
        decode = {"ok": True, "via": "file_put", "bytes": len(raw)}

    install = _guest_bash(
        session,
        "set -e; test -s /tmp/ga_new.py; "
        "cp /tmp/ga_new.py /opt/gunnchos/bin/gunnchos_guest_agent.py; "
        "cp /tmp/ga_new.py /usr/local/sbin/gunnchos_guest_agent.py 2>/dev/null || true; "
        "systemctl restart gunnchos-guest-agent.service || "
        "(pkill -f gunnchos_guest_agent.py || true; "
        " nohup python3 /opt/gunnchos/bin/gunnchos_guest_agent.py "
        " >/var/log/gunnchos-guest-agent.log 2>&1 &); sleep 2; echo restarted",
        timeout_sec=60,
        name="ga-install",
    )
    for _ in range(30):
        ping = _agent_call(session, "ping")
        if ping.get("pong"):
            pr = _agent_call(
                session, "process_run", argv=["bash", "-lc", "echo process_run_ok"], timeout_sec=10.0
            )
            return {
                "install": install,
                "decode": decode,
                "put_errors": put_errors,
                "ping": ping,
                "process_run_probe": pr,
            }
        time.sleep(1.0)
    return {"install": install, "decode": decode, "put_errors": put_errors, "error": "agent_did_not_return"}


'''
text = text[:old_hp_start] + new_hp + text[old_hp_end:]

# Fix _ensure_godot4_in_guest to use cache from multiple locations + curl first
old_g_start = text.find("def _ensure_godot4_in_guest(session: Any, repo_root: Path) -> dict[str, Any]:")
old_g_end = text.find("\ndef _deploy_pedestrian_pursuit(", old_g_start)
if old_g_start < 0 or old_g_end < 0:
    raise SystemExit(f"godot bounds missing {old_g_start} {old_g_end}")

new_g = '''def _ensure_godot4_in_guest(session: Any, repo_root: Path) -> dict[str, Any]:
    """Ensure a Godot 4.x aarch64 Linux binary exists in the guest.

    Debian godot3 is Godot 3.x and cannot run Pedestrian Pursuit (Godot 4.x).
    Prefer host curl (SecureTransport) + local cache; never claim PASS on urllib SSL fail alone.
    """
    import shutil
    import subprocess as _sp
    import zipfile

    cache = repo_root / "artifacts" / "wp011r" / "cache"
    cache.mkdir(parents=True, exist_ok=True)
    godot_bin = cache / "Godot_v4.3-stable_linux.arm64"
    zip_path = cache / "Godot_v4.3-stable_linux.arm64.zip"
    url = (
        "https://github.com/godotengine/godot/releases/download/4.3-stable/"
        "Godot_v4.3-stable_linux.arm64.zip"
    )
    # Alternate caches (field-kit / sibling) when device-os cache empty.
    alt_bins = [
        Path("/Users/gunnchos/Downloads/gunnchos-7gc-research-product-spine/repos/gunnchos-7gc-ai-ran-field-kit/.wave5_lab_artifacts/godot_cache/Godot_v4.3-stable_linux.arm64"),
        repo_root.parent / "gunnchos-7gc-ai-ran-field-kit" / ".wave5_lab_artifacts" / "godot_cache" / "Godot_v4.3-stable_linux.arm64",
    ]
    out: dict[str, Any] = {"url": url, "cache_bin": str(godot_bin)}
    probe = _guest_bash(
        session,
        "command -v godot || test -x /opt/gunnchos/bin/godot && echo /opt/gunnchos/bin/godot; "
        "godot --version 2>/dev/null || /opt/gunnchos/bin/godot --version 2>/dev/null || true",
        timeout_sec=20,
        name="godot-probe",
    )
    out["probe"] = probe
    stdout = probe.get("stdout") or ""
    if "4." in stdout and ("godot" in stdout.lower() or "/opt/gunnchos" in stdout):
        out["ok"] = True
        out["already_present"] = True
        return out

    if not godot_bin.is_file():
        for alt in alt_bins:
            if alt.is_file() and alt.stat().st_size > 1_000_000:
                shutil.copy2(alt, godot_bin)
                out["copied_from"] = str(alt)
                break

    if not godot_bin.is_file():
        try:
            if not zip_path.is_file():
                for altz in [p.with_suffix(p.suffix + ".zip") if False else p for p in []]:
                    pass
                alt_zips = [
                    Path("/Users/gunnchos/Downloads/gunnchos-7gc-research-product-spine/repos/gunnchos-7gc-ai-ran-field-kit/.wave5_lab_artifacts/godot_cache/Godot_v4.3-stable_linux.arm64.zip"),
                ]
                for az in alt_zips:
                    if az.is_file():
                        shutil.copy2(az, zip_path)
                        out["zip_copied_from"] = str(az)
                        break
            if not zip_path.is_file():
                curl = _sp.run(
                    ["curl", "-L", "--fail", "--retry", "3", "-o", str(zip_path), url],
                    capture_output=True,
                    text=True,
                    timeout=300,
                    check=False,
                )
                out["curl"] = {"rc": curl.returncode, "stderr": (curl.stderr or "")[-400:]}
                if curl.returncode != 0 or not zip_path.is_file():
                    # Last resort urllib (may fail SSL on some hosts)
                    import urllib.request

                    urllib.request.urlretrieve(url, zip_path)
            with zipfile.ZipFile(zip_path, "r") as zf:
                names = zf.namelist()
                member = names[0]
                zf.extract(member, cache)
                extracted = cache / member
                extracted.chmod(0o755)
                if extracted != godot_bin:
                    extracted.replace(godot_bin)
            out["downloaded"] = True
        except Exception as exc:  # noqa: BLE001
            out["ok"] = False
            out["error"] = f"godot4_download_failed:{exc}"
            return out

    if not godot_bin.is_file():
        out["ok"] = False
        out["error"] = "godot4_cache_missing_after_download"
        return out

    # Prefer file_put of binary (chunked) over base64 printf.
    import base64

    raw = godot_bin.read_bytes()
    _guest_bash(
        session,
        "rm -f /tmp/godot.bin /opt/gunnchos/bin/godot; mkdir -p /opt/gunnchos/bin",
        timeout_sec=20,
    )
    chunk = 24_000
    for i in range(0, len(raw), chunk):
        piece = raw[i : i + chunk]
        put = _agent_call(
            session,
            "file_put",
            path="/tmp/godot.bin",
            bytes_b64=base64.b64encode(piece).decode("ascii"),
            append=(i > 0),
            timeout_sec=45.0,
        )
        if not put.get("ok"):
            out["ok"] = False
            out["error"] = f"godot_file_put_failed_at_{i}"
            out["put"] = put
            return out
    install = _guest_bash(
        session,
        "set -e; mv /tmp/godot.bin /opt/gunnchos/bin/godot; chmod +x /opt/gunnchos/bin/godot; "
        "ln -sf /opt/gunnchos/bin/godot /usr/local/bin/godot; "
        "/opt/gunnchos/bin/godot --version",
        timeout_sec=60,
        name="godot-install",
    )
    out["install"] = install
    out["ok"] = bool(install.get("ok") and "4." in (install.get("stdout") or ""))
    if not out["ok"]:
        out["error"] = out.get("error") or "godot_install_version_probe_failed"
    return out


'''
text = text[:old_g_start] + new_g + text[old_g_end:]
ast.parse(text)
fg.write_text(text)
print("four_games hot_patch+godot patched")

# Improve apt in reearn script
reearn = root / "scripts/run_cycle3b_demoted_reearn.py"
rt = reearn.read_text()
old_apt = '''def _apt_install(session, packages: list[str]) -> dict:
    pkgs = " ".join(packages)
    return _guest_bash(
        session,
        f"export DEBIAN_FRONTEND=noninteractive; "
        f"apt-get update -qq >/var/log/gunnchos-apt-update.log 2>&1 || true; "
        f"apt-get install -y --no-install-recommends {pkgs} "
        f">/var/log/gunnchos-apt-reearn.log 2>&1 || true; "
        f"dpkg -l {pkgs} 2>/dev/null | awk '/^ii/{{print $2,$3}}' | head -40; "
        f"command -v grim; command -v libreoffice; command -v labwc; true",
        timeout_sec=900,
        name="apt-reearn",
    )
'''
new_apt = '''def _apt_install(session, packages: list[str]) -> dict:
    pkgs = " ".join(packages)
    # Disk + network diagnostics first; install libreoffice with retries; surface apt log tail.
    return _guest_bash(
        session,
        "set +e; export DEBIAN_FRONTEND=noninteractive; "
        "echo '===df==='; df -h / /var 2>/dev/null | head; "
        "echo '===ping==='; getent hosts deb.debian.org | head; "
        "apt-get update -y >/var/log/gunnchos-apt-update.log 2>&1; echo update_rc=$?; "
        f"for attempt in 1 2 3; do "
        f"  apt-get install -y --no-install-recommends {pkgs} "
        f"    >/var/log/gunnchos-apt-reearn.log 2>&1 && break; "
        f"  echo apt_attempt_$attempt_failed; sleep 5; "
        f"done; "
        f"dpkg -l {pkgs} 2>/dev/null | awk '/^ii/{{print $2,$3}}' | head -40; "
        "command -v grim; command -v libreoffice; command -v soffice; command -v labwc; "
        "echo '===apt_reearn_tail==='; tail -40 /var/log/gunnchos-apt-reearn.log 2>/dev/null; "
        "true",
        timeout_sec=1200,
        name="apt-reearn",
    )
'''
if old_apt not in rt:
    raise SystemExit("apt_install block not found")
rt = rt.replace(old_apt, new_apt, 1)
# Also bump memory and ensure godot cache exists before four-game
if "memory_mb=4096" in rt and "godot_cache_seed" not in rt:
    rt = rt.replace(
        "summary[\"apt\"] = _apt_install(",
        "    # Seed Godot cache from field-kit if present (avoid SSL urllib fail).\n"
        "    try:\n"
        "        import shutil\n"
        "        cache = ROOT / \"artifacts/wp011r/cache\"\n"
        "        cache.mkdir(parents=True, exist_ok=True)\n"
        "        alt = Path(\"/Users/gunnchos/Downloads/gunnchos-7gc-research-product-spine/repos/gunnchos-7gc-ai-ran-field-kit/.wave5_lab_artifacts/godot_cache/Godot_v4.3-stable_linux.arm64\")\n"
        "        dest = cache / \"Godot_v4.3-stable_linux.arm64\"\n"
        "        if alt.is_file() and not dest.is_file():\n"
        "            shutil.copy2(alt, dest)\n"
        "            summary[\"godot_cache_seed\"] = str(alt)\n"
        "        elif dest.is_file():\n"
        "            summary[\"godot_cache_seed\"] = \"already_present\"\n"
        "    except Exception as exc:  # noqa: BLE001\n"
        "        summary[\"godot_cache_seed\"] = f\"error:{exc}\"\n\n"
        "        summary[\"apt\"] = _apt_install(",
    )
    # Fix accidental indent bug - the replace may have broken indentation
    rt = rt.replace(
        "        summary[\"apt\"] = _apt_install(\n"
        "            session,\n"
        "            [\"libreoffice-writer\", \"libreoffice-gtk3\", \"labwc\", \"grim\", \"wlr-randr\"],\n"
        "        )",
        "        summary[\"apt\"] = _apt_install(\n"
        "            session,\n"
        "            [\"libreoffice-writer\", \"libreoffice-gtk3\", \"labwc\", \"grim\", \"wlr-randr\"],\n"
        "        )",
    )
ast.parse(rt)
reearn.write_text(rt)
print("reearn apt+godot seed patched")
print("AST ok")
