from pathlib import Path
import ast
import re

proofs = Path("/Users/gunnchos/Downloads/gunnchos-7gc-research-product-spine/repos/gate-worktrees/device-os-wp-011r/gunnchos_device_os/device_lab/interactive_guest_proofs.py")
pt = proofs.read_text()

# Locate function and replace from "# Place real windows" through focus_moves clearing before ux = compositor_ux_gate
start = pt.find("    # Place real windows: foot on output intuition")
if start < 0:
    # maybe already patched
    start = pt.find("    # Place real windows on left/right halves")
    if start >= 0:
        print("already_patched_placement")
        raise SystemExit(0)
    raise SystemExit("start marker missing")
end = pt.find("    ux = compositor_ux_gate(", start)
if end < 0:
    raise SystemExit("ux marker missing")

new = r'''    # Place real windows on left/right halves of the dual scanout (1280+1280).
    oid_a = compositor_outputs[0]["id"] if compositor_outputs else "card0-Virtual-1"
    oid_b = compositor_outputs[1]["id"] if len(compositor_outputs) > 1 else "card0-Virtual-2"

    _agent_call(session, "input_inject", kind="pointer", dx=120, dy=120, button="left", timeout_sec=10.0)
    time.sleep(0.3)
    win_a = _agent_call(session, "app_launch", app="foot", timeout_sec=15.0)
    time.sleep(1.2)
    for _ in range(18):
        _agent_call(session, "input_inject", kind="pointer", dx=80, dy=0, button=None, timeout_sec=5.0)
    _agent_call(session, "input_inject", kind="pointer", dx=0, dy=40, button="left", timeout_sec=10.0)
    time.sleep(0.3)
    win_b = _agent_call(session, "app_launch", app="mousepad", timeout_sec=15.0)
    time.sleep(1.5)
    result["windows_launched"] = {"foot": win_a, "mousepad": win_b}

    place_cap = _capture_guest_fb(session, retries=5, settle_s=1.0)
    place_bytes = place_cap.get("_decoded_bytes") or b""
    halves = _png_half_sha256(place_bytes)
    result["placement_framebuffer"] = {
        k: v for k, v in place_cap.items() if k not in {"bytes_b64", "_decoded_bytes"}
    }
    result["placement_halves"] = halves
    placement_proven = bool(
        halves.get("ok")
        and halves.get("halves_differ")
        and halves.get("left_nonzero")
        and halves.get("right_nonzero")
        and win_a.get("ok")
        and win_b.get("ok")
    )
    windows = [
        {
            "app_id": "foot",
            "output_id": oid_a if placement_proven else "",
            "pid": win_a.get("pid"),
            "ok": bool(win_a.get("ok")),
            "placement_proven": placement_proven,
            "half": "left",
            "half_sha256": halves.get("left_sha256"),
        },
        {
            "app_id": "mousepad",
            "output_id": oid_b if placement_proven else "",
            "pid": win_b.get("pid"),
            "ok": bool(win_b.get("ok")),
            "placement_proven": placement_proven,
            "half": "right",
            "half_sha256": halves.get("right_sha256"),
        },
    ]

    focus_moves: list[dict[str, Any]] = []
    for oid in (oid_a, oid_b):
        if oid == oid_b:
            for _ in range(16):
                _agent_call(session, "input_inject", kind="pointer", dx=80, dy=0, button=None, timeout_sec=5.0)
            click = _agent_call(
                session, "input_inject", kind="pointer", dx=0, dy=20, button="left", timeout_sec=10.0
            )
        else:
            click = _agent_call(
                session, "input_inject", kind="pointer", dx=100, dy=100, button="left", timeout_sec=10.0
            )
        focus_moves.append(
            {
                "ok": bool(click.get("ok")) and placement_proven,
                "output_id": oid if placement_proven else "",
                "click": click,
            }
        )
        time.sleep(0.3)

    def _drm_status(conn_suffix: str = "Virtual-2") -> dict[str, Any]:
        script = (
            "CARD=$(ls -d /sys/class/drm/card*-"
            + conn_suffix
            + " 2>/dev/null | head -1); "
            "echo CARD=$CARD; "
            'if [ -n "$CARD" ]; then cat $CARD/status; else echo missing; fi'
        )
        r = _agent_call(session, "process_run", argv=["bash", "-lc", script], timeout_sec=15.0)
        lines = [ln.strip() for ln in (r.get("stdout") or "").splitlines() if ln.strip()]
        status = lines[-1] if lines else "unknown"
        card = ""
        for ln in lines:
            if ln.startswith("CARD="):
                card = ln.split("=", 1)[1]
        return {"card": card, "status": status, "raw": {k: r.get(k) for k in ("ok", "returncode", "stdout", "stderr") if k in r}}

    before_st = _drm_status()
    qom_paths = [
        "/machine/peripheral/gpu0",
        "/machine/peripheral-anon/device[0]",
    ]
    tree = _qemu_monitor_lines(session, "info qom-tree", wait_s=0.6)
    result["qom_tree_snip"] = "\n".join(
        [ln for ln in tree.splitlines() if "gpu" in ln.lower() or "virtio-gpu" in ln.lower()][:40]
    )
    for ln in tree.splitlines():
        part = ln.strip().split()[0] if ln.strip() else ""
        if part.startswith("/") and ("gpu" in part.lower() or "virtio-gpu" in ln.lower()):
            if part not in qom_paths:
                qom_paths.insert(0, part)

    disc_attempts: list[dict[str, Any]] = []
    disconnect_reconnect: dict[str, Any] = {
        "disconnect_ok": False,
        "reconnect_ok": False,
        "layout_restored": False,
        "method": "qemu_qom_set_outputs",
    }
    for path in qom_paths:
        off1 = _qemu_monitor_lines(session, f"qom-set {path} outputs[1].xres 0", wait_s=0.3)
        off2 = _qemu_monitor_lines(session, f"qom-set {path} outputs[1].yres 0", wait_s=0.5)
        time.sleep(1.5)
        mid_st = _drm_status()
        mid_comp = _agent_call(session, "compositor_info")
        attempt = {
            "path": path,
            "off_xres_tail": off1[-200:],
            "off_yres_tail": off2[-200:],
            "mid_drm": mid_st,
            "mid_compositor_outputs": mid_comp.get("outputs"),
        }
        disc_attempts.append(attempt)
        mid_disc = str(mid_st.get("status") or "").lower() == "disconnected"
        mid_comp_drop = int(mid_comp.get("outputs") or 99) < 2
        if not (mid_disc or mid_comp_drop):
            continue
        on1 = _qemu_monitor_lines(session, f"qom-set {path} outputs[1].xres 1280", wait_s=0.3)
        on2 = _qemu_monitor_lines(session, f"qom-set {path} outputs[1].yres 800", wait_s=0.5)
        time.sleep(2.0)
        after_st = _drm_status()
        after_comp = _agent_call(session, "compositor_info")
        recon_ok = (
            str(after_st.get("status") or "").lower() == "connected"
            or int(after_comp.get("outputs") or 0) >= 2
        )
        disconnect_reconnect.update(
            {
                "connector": mid_st.get("card") or before_st.get("card"),
                "before": before_st.get("status"),
                "mid": mid_st.get("status") if mid_disc else f"compositor_outputs={mid_comp.get('outputs')}",
                "after": after_st.get("status"),
                "disconnect_ok": True,
                "reconnect_ok": bool(recon_ok),
                "layout_restored": bool(recon_ok and after_comp.get("available")),
                "qom_path": path,
                "mid_compositor_outputs": mid_comp.get("outputs"),
                "after_compositor_outputs": after_comp.get("outputs"),
                "drm_disconnected": mid_disc,
                "compositor_output_drop": mid_comp_drop,
                "on_xres_tail": on1[-120:],
                "on_yres_tail": on2[-120:],
            }
        )
        result["compositor_info_after_reconnect"] = after_comp
        break
    else:
        disc_raw = _agent_call(
            session,
            "process_run",
            argv=[
                "bash",
                "-lc",
                "CARD=$(ls -d /sys/class/drm/card*-Virtual-2 2>/dev/null | head -1); "
                "BEFORE=$(cat $CARD/status 2>/dev/null||echo unknown); "
                "echo off >$CARD/enabled 2>/dev/null||true; sleep 1; "
                "MID=$(cat $CARD/status 2>/dev/null||echo unknown); "
                "echo on >$CARD/enabled 2>/dev/null||true; sleep 1; "
                "AFTER=$(cat $CARD/status 2>/dev/null||echo unknown); "
                "python3 -c \"import json; print(json.dumps({"
                "'connector':'$CARD','before':'$BEFORE','mid':'$MID','after':'$AFTER',"
                "'disconnect_ok': False, 'reconnect_ok': False, 'layout_restored': False,"
                "'method':'sysfs_noop_check'}))\"",
            ],
            timeout_sec=30.0,
        )
        result["disconnect_raw"] = {
            k: disc_raw.get(k) for k in ("ok", "returncode", "stdout", "stderr") if k in disc_raw
        }
        try:
            for line in reversed((disc_raw.get("stdout") or "").strip().splitlines()):
                if line.strip().startswith("{"):
                    disconnect_reconnect = json.loads(line.strip())
                    break
        except Exception as exc:  # noqa: BLE001
            disconnect_reconnect["parse_error"] = str(exc)[:200]
        if str(disconnect_reconnect.get("before")) == str(disconnect_reconnect.get("mid")):
            disconnect_reconnect["noop_rejected"] = True
            disconnect_reconnect["disconnect_ok"] = False
            disconnect_reconnect["note"] = (
                "QEMU qom-set did not change secondary output; sysfs also noop — "
                "DSXL disconnect not earned"
            )

    result["disconnect_attempts"] = disc_attempts
    if "compositor_info_after_reconnect" not in result:
        result["compositor_info_after_reconnect"] = _agent_call(session, "compositor_info")
    comp_after = result["compositor_info_after_reconnect"]
    layout_restore = {
        "ok": bool(
            disconnect_reconnect.get("disconnect_ok")
            and disconnect_reconnect.get("reconnect_ok")
            and comp_after.get("available")
            and int(comp_after.get("outputs") or 0) >= 2
        ),
        "layout_restored": bool(
            disconnect_reconnect.get("disconnect_ok")
            and disconnect_reconnect.get("reconnect_ok")
            and comp_after.get("available")
            and int(comp_after.get("outputs") or 0) >= 2
        ),
        "outputs_after": int(comp_after.get("outputs") or 0),
    }
    if disconnect_reconnect.get("layout_restored") and layout_restore["ok"]:
        disconnect_reconnect["layout_restored"] = True

'''

pt = pt[:start] + new + pt[end:]
ast.parse(pt)
proofs.write_text(pt)
print("DSXL patched OK", proofs)
