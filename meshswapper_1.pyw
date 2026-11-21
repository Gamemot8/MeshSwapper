"""MeshSwapper - mesh sets for Bloxstrap (Windows).

Your sets live in their own folder:
    %LOCALAPPDATA%\\MeshSwapper\\Sets\\<SetName>\\leftarm.mesh, torso.mesh, ...

"Apply" copies every .mesh file of a set (the files, not the folder) into:
    %LOCALAPPDATA%\\Bloxstrap\\Modifications\\content\\avatar\\meshes

Bloxstrap applies them whenever you launch Roblox. "Reset" removes them again.
Local only: other players still see the original meshes.

The preview shows the full-detail meshes solid and smoothly shaded in Roblox-dummy grey, with
clear outlines between the parts. It is drawn as an image with numpy (fast, no GPU needed).
The top bar shows which Roblox version is installed and whether it is the latest one.
"""
import base64
import json
import math
import random
import os
import queue
import re
import shutil
import struct
import subprocess
import sys
import threading
import time
import urllib.request
import webbrowser
import zlib
from pathlib import Path

try:
    import numpy as np
except ImportError:  # shown as a message in main(), so the window never just vanishes
    np = None

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, simpledialog, ttk
    from tkinter import font as tkfont
except ImportError:  # only for tests without a GUI
    tk = None

APP = "MeshSwapper"
BLOXSTRAP_URL = "https://bloxstraplabs.com"
DISCORD_URL = "https://discord.gg/E5yuUshPXY"
LOGO_B64 = "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"
LOGO_SMALL_B64 = "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"
VERSION_API = "https://clientsettings.roblox.com/v2/client-version/WindowsPlayer"
LOCAL = Path(os.environ.get("LOCALAPPDATA", str(Path.home())))
DATA = LOCAL / APP
for _old in ("MeshSpind", "MeshLocker"):  # earlier names of this app: keep using their folder so nothing is lost
    if not DATA.is_dir() and (LOCAL / _old).is_dir():
        DATA = LOCAL / _old
SETS = DATA / "Sets"
CONFIG = DATA / "config.json"
ERRLOG = DATA / "error.log"


def log_error():
    """Writes the current exception to error.log and returns its text."""
    import traceback
    text = traceback.format_exc()
    try:
        DATA.mkdir(parents=True, exist_ok=True)
        with open(ERRLOG, "a", encoding="utf-8") as f:
            f.write(text + "\n")
    except OSError:
        pass
    return text

# Suggestions only - the real file names can differ between Roblox versions.
SUGGESTIONS = [
    "leftarm.mesh", "rightarm.mesh", "leftleg.mesh", "rightleg.mesh", "torso.mesh",
    "uppertorso.mesh", "lowertorso.mesh",
    "leftupperarm.mesh", "leftlowerarm.mesh", "lefthand.mesh",
    "rightupperarm.mesh", "rightlowerarm.mesh", "righthand.mesh",
    "leftupperleg.mesh", "leftlowerleg.mesh", "leftfoot.mesh",
    "rightupperleg.mesh", "rightlowerleg.mesh", "rightfoot.mesh",
]


# --------------------------------------------------------------------------
# Core logic (no GUI)
# --------------------------------------------------------------------------
class MeshError(Exception):
    pass


def load_cfg():
    try:
        cfg = json.loads(CONFIG.read_text("utf-8"))
    except Exception:
        cfg = {}
    cfg.setdefault("sets", {})
    cfg.setdefault("bloxstrap_dir", "")
    cfg.setdefault("welcome_shown", False)
    return cfg


def save_cfg(cfg):
    DATA.mkdir(parents=True, exist_ok=True)
    CONFIG.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), "utf-8")


def bloxstrap_dir(cfg):
    custom = cfg.get("bloxstrap_dir")
    return Path(custom) if custom else LOCAL / "Bloxstrap"


def meshes_dir(cfg):
    return bloxstrap_dir(cfg) / "Modifications" / "content" / "avatar" / "meshes"


def ensure_meshes_dir(cfg):
    """Creates Modifications/content/avatar/meshes if missing (only if Bloxstrap exists)."""
    if not bloxstrap_dir(cfg).is_dir():
        raise FileNotFoundError("Bloxstrap folder not found.")
    d = meshes_dir(cfg)
    d.mkdir(parents=True, exist_ok=True)
    return d


def safe_name(raw):
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", str(raw)).strip().strip(".")
    return name


def clean_filename(raw):
    name = Path(str(raw).strip().replace("\\", "/")).name
    if name and not name.lower().endswith(".mesh"):
        name += ".mesh"
    return name


def header_version(path):
    """Returns ('2.00', 2) or None if it is not a Roblox mesh."""
    try:
        with open(path, "rb") as f:
            head = f.read(16)
        m = re.match(rb"version (\d+)\.(\d+)", head)
        if not m:
            return None
        return m.group(0)[8:].decode(), int(m.group(1))
    except OSError:
        return None


def _unpack_header(raw, off, fmt):
    return struct.unpack_from(fmt, raw, off)


def _strided(raw, start, count, stride, col):
    """Reads `count` float3 values that sit `stride` bytes apart (no Python loop, very fast)."""
    return np.ndarray((count, 3), dtype="<f4", buffer=raw, offset=start + col,
                      strides=(stride, 4)).astype(np.float64)


def parse_mesh(path):
    """Reads positions, normals and triangles. Supports formats 1-4.

    Returns (version, V (n,3), N (n,3) or None, F (m,3) int array).
    """
    raw = Path(path).read_bytes()
    if not raw.startswith(b"version "):
        raise MeshError("Not a valid Roblox mesh file (missing 'version x.xx' header).")
    nl = raw.find(b"\n")
    if nl < 0:
        raise MeshError("Broken header.")
    try:
        ver = raw[:nl].decode("ascii", "ignore").strip().split()[1]
        major = int(ver.split(".")[0])
    except (IndexError, ValueError):
        raise MeshError("Broken header.")
    off = nl + 1

    try:
        if major == 1:
            lines = raw.decode("ascii", "ignore").splitlines()
            scale = 0.5 if ver.startswith("1.00") else 1.0
            groups = re.findall(r"\[([^\]]+)\]", " ".join(lines[2:]))
            cnt = len(groups) // 3 * 3
            V = np.array([[float(v) for v in g.split(",")[:3]] for g in groups[0:cnt:3]]) * scale
            N = np.array([[float(v) for v in g.split(",")[:3]] for g in groups[1:cnt:3]])
            F = np.arange(len(V) // 3 * 3, dtype=np.int64).reshape(-1, 3)
            return ver, V, N, F

        if major == 2:
            hsize, vsize, fsize, nv, nf = _unpack_header(raw, off, "<HBBII")
            start = off + hsize
            lod = None
            nbones = 0
        elif major == 3:
            hsize, vsize, fsize, _lodsz, nlod, nv, nf = _unpack_header(raw, off, "<HBBHHII")
            start = off + hsize
            lod = nlod
            nbones = 0
        elif major == 4:
            (hsize, _lt, nv, nf, nlod, nbones, _nt, _ns, _hq, _u) = _unpack_header(raw, off, "<HHIIHHIHBB")
            vsize, fsize = 40, 12
            start = off + hsize
            lod = nlod
        else:
            raise MeshError(f"No preview for mesh format {ver} (applying still works).")

        if nv > 3_000_000 or nf > 6_000_000:
            raise MeshError("Mesh is too large for the preview.")
        if vsize < 12 or fsize < 12:
            raise MeshError("Unusual mesh layout - no preview (applying still works).")
        V = _strided(raw, start, nv, vsize, 0)
        N = _strided(raw, start, nv, vsize, 12) if vsize >= 24 else None
        fstart = start + nv * vsize
        if major == 4 and nbones > 0:
            fstart += nv * 8
        count = nf
        if lod and lod >= 2:
            lods = struct.unpack_from(f"<{lod}I", raw, fstart + nf * fsize)
            fstart += lods[0] * fsize
            count = max(0, min(nf - lods[0], lods[1] - lods[0]))
        F = np.ndarray((count, 3), dtype="<u4", buffer=raw, offset=fstart, strides=(fsize, 4)).astype(np.int64)
        return ver, V, N, F
    except (struct.error, ValueError, TypeError):
        raise MeshError("File is incomplete or damaged.")


def prepare_mesh(path):
    """Loads a mesh in full detail (nothing is simplified). Broken triangles are dropped.

    Returns {'V', 'N' (or None if the file has no usable normals), 'F', 'bbox', ...}.
    """
    ver, V, N, F = parse_mesh(path)
    nv = len(V)
    if not nv or not len(F):
        raise MeshError("Empty mesh.")
    nf = len(F)
    good = (F >= 0).all(1) & (F < nv).all(1)
    F = F[good]
    ok = np.isfinite(V).all(1)
    F = F[ok[F].all(1)]
    F = F[(F[:, 0] != F[:, 1]) & (F[:, 1] != F[:, 2]) & (F[:, 0] != F[:, 2])]
    if not len(F):
        raise MeshError("Mesh has no usable triangles.")
    used = np.unique(F)
    lo, hi = V[used].min(0), V[used].max(0)
    bbox = (lo[0], hi[0], lo[1], hi[1], lo[2], hi[2])
    if N is not None:  # use the file's normals only if they look sane
        with np.errstate(invalid="ignore"):
            ln = np.linalg.norm(N, axis=1)
            sane = np.isfinite(ln) & (ln > 0.3) & (ln < 2.0)
        if sane[used].mean() > 0.99:
            N = np.where(sane[:, None], N / np.where(sane, ln, 1.0)[:, None], 0.0)
        else:
            N = None
    return {"ver": ver, "V": V, "N": N, "F": F, "bbox": bbox, "nv": nv, "nf": nf}


# Where each body part sits relative to another one (Roblox: left = -X, facing -Z).
# kind: above / below / left / right (top-aligned) / below_left / below_right (leg under the torso half)
RULES = {
    "head": ("above", ["torso", "uppertorso"]),
    "uppertorso": ("above", ["lowertorso"]),
    "leftarm": ("left", ["torso", "uppertorso"]),
    "rightarm": ("right", ["torso", "uppertorso"]),
    "leftleg": ("below_left", ["torso", "lowertorso"]),
    "rightleg": ("below_right", ["torso", "lowertorso"]),
    "leftupperarm": ("left", ["uppertorso", "torso"]),
    "rightupperarm": ("right", ["uppertorso", "torso"]),
    "leftlowerarm": ("below", ["leftupperarm"]),
    "rightlowerarm": ("below", ["rightupperarm"]),
    "lefthand": ("below", ["leftlowerarm"]),
    "righthand": ("below", ["rightlowerarm"]),
    "leftupperleg": ("below_left", ["lowertorso", "torso"]),
    "rightupperleg": ("below_right", ["lowertorso", "torso"]),
    "leftlowerleg": ("below", ["leftupperleg"]),
    "rightlowerleg": ("below", ["rightupperleg"]),
    "leftfoot": ("below", ["leftlowerleg"]),
    "rightfoot": ("below", ["rightlowerleg"]),
}
ROOTS = ("torso", "lowertorso", "uppertorso")


def part_key(filename):
    return re.sub(r"[\s_\-]+", "", Path(filename).stem.lower())


def _shift(bb, d):
    return (bb[0] + d[0], bb[1] + d[0], bb[2] + d[1], bb[3] + d[1], bb[4] + d[2], bb[5] + d[2])


def _place_offset(kind, bb, a):
    cx, cz = (bb[0] + bb[1]) / 2, (bb[4] + bb[5]) / 2
    acx, acz = (a[0] + a[1]) / 2, (a[4] + a[5]) / 2
    # Classic dummy, measured in torso heights (torso = 2 studs): the head centre sits 1.5 studs
    # above the torso centre (so it dips a little into the shoulders), the arms sit right next to
    # the torso at the same height, the legs hang directly under it.
    if kind == "neck":
        return (acx - cx, (a[2] + a[3]) / 2 + 0.75 * (a[3] - a[2]) - (bb[2] + bb[3]) / 2, acz - cz)
    if kind in ("left_c", "right_c"):
        dy = (a[2] + a[3]) / 2 - (bb[2] + bb[3]) / 2
        return ((a[0] - bb[1]) if kind == "left_c" else (a[1] - bb[0]), dy, acz - cz)
    if kind == "above":
        return (acx - cx, a[3] - bb[2], acz - cz)
    if kind == "below":
        return (acx - cx, a[2] - bb[3], acz - cz)
    if kind == "left":
        return (a[0] - bb[1], a[3] - bb[3], acz - cz)
    if kind == "right":
        return (a[1] - bb[0], a[3] - bb[3], acz - cz)
    if kind == "below_left":
        return (acx - bb[1], a[2] - bb[3], acz - cz)
    return (acx - bb[0], a[2] - bb[3], acz - cz)  # below_right


# Classic (R6) body: where each part's origin sits relative to the torso's origin, in studs.
# Roblox puts a replaced mesh at the part's origin, so this is how the parts really line up in the game.
R6_OFFSETS = {"torso": (0.0, 0.0, 0.0), "head": (0.0, 1.5, 0.0), "leftarm": (-1.5, 0.0, 0.0),
              "rightarm": (1.5, 0.0, 0.0), "leftleg": (-0.5, -2.0, 0.0), "rightleg": (0.5, -2.0, 0.0)}


# Size of each classic part in studs (width, height, depth).
STD_SIZE = {"torso": (2.0, 2.0, 1.0), "head": (2.0, 1.0, 1.0), "leftarm": (1.0, 2.0, 1.0),
            "rightarm": (1.0, 2.0, 1.0), "leftleg": (1.0, 2.0, 1.0), "rightleg": (1.0, 2.0, 1.0)}


def _fit_part(key, prep):
    """Only helps with meshes that are clearly broken, and never bends a shape:
    - a few stray vertices far away from the body are left out of the preview,
    - a mesh far outside the size of a body part (smaller than 0.25 or bigger than 12 studs, for example
      exported in centimetres) is scaled evenly so that its height matches the part.
    Everything else (also fat, tall or wide custom bodies) is shown exactly as it is in the file.
    Returns (prep, None) when nothing was changed, else (new_prep, info)."""
    std = np.array(STD_SIZE[key])
    V, F, bb = prep["V"], prep["F"], prep["bbox"]
    size = np.array([bb[1] - bb[0], bb[3] - bb[2], bb[5] - bb[4]])
    stray = False
    used = np.unique(F)
    if len(used) > 50:
        lo, hi = np.percentile(V[used], 0.5, axis=0), np.percentile(V[used], 99.5, axis=0)
        robust = hi - lo
        if (size > robust * 3.0 + 1e-9).any():  # stray vertices stretch the box a lot
            m = np.maximum(robust, 1e-6) * 0.5
            inside = ((V >= lo - m) & (V <= hi + m)).all(1)
            F2 = F[inside[F].all(1)]
            if len(F2):
                u2 = np.unique(F2)
                lo2, hi2 = V[u2].min(0), V[u2].max(0)
                F, size, stray = F2, hi2 - lo2, True
                bb = (lo2[0], hi2[0], lo2[1], hi2[1], lo2[2], hi2[2])
    big = float(size.max())
    scaled = big < 0.25 or big > 12
    if not stray and not scaled:
        return prep, None
    p2 = dict(prep)
    p2["F"] = F
    if scaled:
        f = float(std[1] / size[1]) if size[1] > 1e-6 else float(std.max() / max(big, 1e-9))
        p2["V"] = V * f
        bb = tuple(v * f for v in bb)
    p2["bbox"] = bb
    return p2, {"size": tuple(float(v) for v in size), "stray": stray, "scaled": scaled}


def build_scene(parts, origin=True, fix_sizes=True):
    """Puts the parts together like the Roblox dummy (by file name) for one preview.

    parts: list of (filename, prepared_mesh). Returns (scene, assembled_count).
    Parts with unknown names are placed in a row below / in a grid.
    """
    items = []
    for name, prep in parts:
        if not len(prep["F"]):
            continue
        items.append({"key": part_key(name), "name": Path(name).stem, "prep": prep, "bb": prep["bbox"]})
    if not items:
        return None, 0
    n = len(items)
    keyidx = {}
    for i, it in enumerate(items):
        keyidx.setdefault(it["key"], i)
    offs = [None] * n
    placed = {}
    adjusted = []
    origin_used = False
    r6 = [i for i, it in enumerate(items) if keyidx.get(it["key"]) == i and it["key"] in R6_OFFSETS]
    if origin and len(r6) >= 2:  # classic body: every mesh goes to its own origin, like in Roblox
        origin_used = True
        for i in r6:
            if fix_sizes:
                prep2, was = _fit_part(items[i]["key"], items[i]["prep"])
                if was:
                    items[i]["prep"], items[i]["bb"] = prep2, prep2["bbox"]
                    adjusted.append((items[i]["name"], was))
            offs[i] = R6_OFFSETS[items[i]["key"]]
            placed[i] = _shift(items[i]["bb"], offs[i])
    root = next((keyidx[r] for r in ROOTS if r in keyidx), None)
    if not origin_used and root is not None and n > 1:
        bb = items[root]["bb"]
        offs[root] = (-(bb[0] + bb[1]) / 2, -(bb[2] + bb[3]) / 2, -(bb[4] + bb[5]) / 2)
        placed[root] = _shift(bb, offs[root])
        progress = True
        while progress:
            progress = False
            for i, it in enumerate(items):
                if offs[i] is not None or keyidx.get(it["key"]) != i or it["key"] not in RULES:
                    continue
                kind, anchors = RULES[it["key"]]
                a = next((keyidx[x] for x in anchors if x in keyidx and keyidx[x] in placed), None)
                if a is None:
                    continue
                if items[a]["key"] == "torso":  # classic dummy: exact layout
                    kind = {"above": "neck", "left": "left_c", "right": "right_c"}.get(kind, kind)
                offs[i] = _place_offset(kind, it["bb"], placed[a])
                placed[i] = _shift(it["bb"], offs[i])
                progress = True
    assembled = len(placed)

    left = [i for i in range(n) if offs[i] is None]
    if left:
        cell = max(max(b[1] - b[0], b[3] - b[2], b[5] - b[4]) for b in (it["bb"] for it in items)) * 1.2
        if placed:
            gx = [b[0] for b in placed.values()] + [b[1] for b in placed.values()]
            gy = [b[2] for b in placed.values()]
            x0 = (min(gx) + max(gx)) / 2 - (len(left) - 1) / 2 * cell
            for k, i in enumerate(left):
                bb = items[i]["bb"]
                tx, ty = x0 + k * cell, min(gy) - cell * 0.8
                offs[i] = (tx - (bb[0] + bb[1]) / 2, ty - (bb[2] + bb[3]) / 2, -(bb[4] + bb[5]) / 2)
        else:
            cols = math.ceil(math.sqrt(len(left))) if len(left) > 1 else 1
            rows = math.ceil(len(left) / cols)
            for k, i in enumerate(left):
                bb = items[i]["bb"]
                tx = (k % cols - (cols - 1) / 2) * cell
                ty = -(k // cols - (rows - 1) / 2) * cell
                offs[i] = (tx - (bb[0] + bb[1]) / 2, ty - (bb[2] + bb[3]) / 2, -(bb[4] + bb[5]) / 2)

    scene = sample_scene([(it["prep"], offs[i]) for i, it in enumerate(items)])
    scene["origin"], scene["adjusted"] = origin_used, adjusted
    return scene, assembled


# --------------------------------------------------------------------------
# Image renderer: the surface is sampled into points and drawn with a depth buffer
# (all in numpy, so even full-detail meshes stay smooth; no GPU needed)
# --------------------------------------------------------------------------
SAMPLES = 200_000
BG_RGB = (8, 5, 18)  # same as the preview canvas (#080512)
_BD = {}


def backdrop(w, h):
    """Dark purple backdrop with a soft glow behind the model (cached per size)."""
    if (w, h) not in _BD:
        if len(_BD) > 4:
            _BD.clear()
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        d = np.sqrt(((xx - w / 2) / (w * 0.62)) ** 2 + ((yy - h * 0.46) / (h * 0.72)) ** 2)
        k = np.clip(1.0 - d, 0.0, 1.0) ** 1.6
        base = np.array(BG_RGB, np.float32)
        _BD[(w, h)] = (base + (np.array((44, 24, 90), np.float32) - base) * k[..., None]).astype(np.uint8)
    return _BD[(w, h)]
if np is not None:
    DUMMY_GREY = np.array((163, 162, 165), np.float32) * 1.25  # Roblox "Medium stone grey"
    LIGHT = np.array((-0.35, 0.55, 0.76), np.float32)
    LIGHT /= np.linalg.norm(LIGHT)
NEIGH8 = ((0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1))


def png_bytes(arr):
    """Encodes an (h, w, 3) uint8 array as a PNG (tkinter can always show those)."""
    h, w, _c = arr.shape
    raw = np.concatenate([np.zeros((h, 1), np.uint8), arr.reshape(h, w * 3)], axis=1).tobytes()

    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 1)) + chunk(b"IEND", b""))


def sample_scene(placed, total=SAMPLES, norm=None):
    """placed: list of (prepared_mesh, (dx, dy, dz)). Returns a scene dict with ~`total` surface
    points, their normals and the part they belong to, already centred and scaled to -1..1."""
    A, B, C, NA, NB, NC, PID, TR = [], [], [], [], [], [], [], []
    for k, (prep, off) in enumerate(placed):
        V = prep["V"] + np.asarray(off, np.float64)
        F = prep["F"]
        a, b, c = V[F[:, 0]], V[F[:, 1]], V[F[:, 2]]
        cr = np.cross(b - a, c - a)
        ln = np.linalg.norm(cr, axis=1)
        keep = ln > 1e-18
        if prep["N"] is not None:
            Nv = prep["N"]
            na, nb, nc = Nv[F[:, 0]], Nv[F[:, 1]], Nv[F[:, 2]]
        else:
            fn = cr / np.where(keep, ln, 1.0)[:, None]
            na = nb = nc = fn
        A.append(a[keep]); B.append(b[keep]); C.append(c[keep])
        NA.append(na[keep]); NB.append(nb[keep]); NC.append(nc[keep])
        PID.append(np.full(int(keep.sum()), k % 250, np.uint8))
        TR.append(np.full(int(keep.sum()), prep["N"] is not None))  # normals from the file can be trusted
    A, B, C = np.concatenate(A), np.concatenate(B), np.concatenate(C)
    NA, NB, NC = np.concatenate(NA), np.concatenate(NB), np.concatenate(NC)
    PID, TR = np.concatenate(PID), np.concatenate(TR)
    m = len(A)
    if not m:
        raise MeshError("Nothing to draw.")
    area = 0.5 * np.linalg.norm(np.cross(B - A, C - A), axis=1)
    rng = np.random.default_rng(1)
    cnt = (area * (total / max(area.sum(), 1e-30)) + rng.random(m)).astype(np.intp)
    idx = np.repeat(np.arange(m), cnt)
    k = len(idx)
    if not k:
        raise MeshError("Nothing to draw.")
    u = np.sqrt(rng.random(k))
    r2 = rng.random(k)
    w0, w1, w2 = (1 - u)[:, None], (u * (1 - r2))[:, None], (u * r2)[:, None]
    P = w0 * A[idx] + w1 * B[idx] + w2 * C[idx]
    Nn = w0 * NA[idx] + w1 * NB[idx] + w2 * NC[idx]
    nl = np.linalg.norm(Nn, axis=1)
    Nn /= np.where(nl > 1e-9, nl, 1.0)[:, None]
    lo = np.minimum(np.minimum(A.min(0), B.min(0)), C.min(0))
    hi = np.maximum(np.maximum(A.max(0), B.max(0)), C.max(0))
    if norm:  # creator: fixed scale (studs), so the view does not jump while a shape is edited
        P = P / float(norm)
    else:
        P = (P - (lo + hi) / 2) / max((hi - lo).max() / 2, 1e-12)
    perm = rng.permutation(k)  # random order, so taking every n-th point is a fair sample
    return {"pts": P[perm].astype(np.float32), "nrm": Nn[perm].astype(np.float32),
            "part": PID[idx][perm], "trust": TR[idx][perm]}


def render_image(scene, yaw, pitch, zoom, w, h, stride=1, fill=True):
    """Draws the scene into an (h, w, 3) uint8 image: smooth grey shading + outlines."""
    pts, nrm, part, trust = scene["pts"], scene["nrm"], scene["part"], scene["trust"]
    if stride > 1:
        pts, nrm, part, trust = pts[::stride], nrm[::stride], part[::stride], trust[::stride]
    cy, sy = math.cos(yaw), math.sin(yaw)
    cp, sp = math.cos(pitch), math.sin(pitch)
    R = np.array([[cy, 0.0, sy], [sy * sp, cp, -cy * sp], [-sy * cp, sp, cy * cp]], np.float32)
    cam = pts @ R.T
    s = min(w, h) * 0.42 * zoom
    ix = (cam[:, 0] * s + w / 2).astype(np.int32)
    iy = (h / 2 - cam[:, 1] * s).astype(np.int32)
    depth = cam[:, 2]  # bigger = closer to the viewer
    img = backdrop(w, h).copy()
    away = trust & ((nrm @ R[2]) < -0.05)  # surface turned away from us (only where the file's normals are reliable)
    sel = np.nonzero((ix >= 0) & (ix < w - 1) & (iy >= 0) & (iy < h - 1) & ~away)[0]
    if not sel.size:
        return img
    order = sel[np.argsort(depth[sel])]  # far to near: the nearest point written last wins
    pix = iy[order] * w + ix[order]
    d = depth[order]
    zb = np.full(w * h, -np.inf, np.float32)
    buf = np.full(w * h, -1, np.int32)
    for off in (0, 1, w, w + 1):  # every point covers 2x2 pixels, so there are no gaps
        pp = pix + off
        win = d > zb[pp]
        pw = pp[win]
        zb[pw] = d[win]
        buf[pw] = order[win]
    buf = buf.reshape(h, w)
    zb = zb.reshape(h, w)

    if fill:  # remove pixels where a hidden surface peeks through a tiny gap in the front layer
        for _ in range(3):
            have = buf >= 0
            nb_z = [np.roll(np.where(have, zb, -np.inf), sh, (0, 1)) for sh in NEIGH8[:4]]
            nb_b = [np.roll(buf, sh, (0, 1)) for sh in NEIGH8[:4]]
            near = np.stack(nb_z)  # (4, h, w) depths of the 4 direct neighbours
            ahead = (near > (zb + 0.03)[None]).sum(0)  # how many neighbours are clearly in front
            bad = have & (ahead >= 3)
            if not bad.any():
                break
            k = near.argmax(0)  # nearest neighbour
            pick_b = np.take_along_axis(np.stack(nb_b), k[None], 0)[0]
            pick_z = np.take_along_axis(near, k[None], 0)[0]
            buf = np.where(bad, pick_b, buf)
            zb = np.where(bad, pick_z, zb)

    if fill:  # close tiny pinholes inside the surface (a few passes; the outline itself stays sharp)
        for _ in range(3):
            have = buf >= 0
            cnt = np.zeros((h, w), np.uint8)
            for dy, dx in NEIGH8:
                cnt += np.roll(have, (dy, dx), (0, 1))
            hole = (~have) & (cnt >= 5)
            if not hole.any():
                break
            best = np.full((h, w), -np.inf, np.float32)
            bidx = np.full((h, w), -1, np.int32)
            for dy, dx in NEIGH8[:4]:
                sz, sb = np.roll(zb, (dy, dx), (0, 1)), np.roll(buf, (dy, dx), (0, 1))
                better = hole & (sb >= 0) & (sz > best)
                best = np.where(better, sz, best)
                bidx = np.where(better, sb, bidx)
            got = hole & (bidx >= 0)
            buf = np.where(got, bidx, buf)
            zb = np.where(got, best, zb)

    mask = buf >= 0
    ids = buf[mask]
    n = nrm[ids] @ R.T
    n[n[:, 2] < 0] *= -1  # two-sided: always shade the side that faces us
    lum = np.minimum(0.20 + 0.62 * np.maximum(n @ LIGHT, 0) + 0.18 * n[:, 2], 1.0)
    img[mask] = np.clip(DUMMY_GREY[None, :] * (0.16 + 0.84 * lum)[:, None], 0, 255).astype(np.uint8)

    # outlines: object border, borders between parts, sharp creases and depth jumps
    nimg = np.zeros((h, w, 3), np.float32)
    nimg[mask] = n
    pid = np.full((h, w), 255, np.uint8)
    pid[mask] = part[ids]
    zc = np.where(mask, zb, 0.0)
    edge = np.zeros((h, w), bool)
    for s0, s1 in ((np.s_[:, :-1], np.s_[:, 1:]), (np.s_[:-1, :], np.s_[1:, :])):
        m0, m1 = mask[s0], mask[s1]
        both = m0 & m1
        diff = m0 != m1
        diff |= both & (pid[s0] != pid[s1])
        diff |= both & ((nimg[s0] * nimg[s1]).sum(2) < 0.80)
        diff |= both & (np.abs(zc[s0] - zc[s1]) > 0.08)
        edge[s0] |= diff & m0
        edge[s1] |= diff & m1
    img[edge] = (img[edge] * 0.5).astype(np.uint8)
    return img


# --------------------------------------------------------------------------
# Roblox version check
# --------------------------------------------------------------------------
def installed_versions(cfg):
    """Folders like version-xxxxxxxx that contain Roblox (Bloxstrap's first, then the normal one)."""
    found = []
    for base in (bloxstrap_dir(cfg) / "Versions", LOCAL / "Roblox" / "Versions"):
        try:
            for d in base.iterdir():
                if d.is_dir() and d.name.startswith("version-") and (d / "RobloxPlayerBeta.exe").exists():
                    found.append((d.stat().st_mtime, d.name))
        except OSError:
            continue
    found.sort(reverse=True)
    return [name for _m, name in found]


def current_version(cfg):
    """The version Roblox will start with ('' if none is installed)."""
    names = installed_versions(cfg)
    try:
        state = json.loads((bloxstrap_dir(cfg) / "State.json").read_text("utf-8-sig"))
        guid = str(state.get("VersionGuid", ""))
    except Exception:  # noqa: BLE001
        guid = ""
    if guid and guid in names:
        return guid
    return names[0] if names else ""


def fetch_latest_version():
    """Asks Roblox for the newest Windows client. Returns (version_guid, readable_version)."""
    req = urllib.request.Request(VERSION_API, headers={"User-Agent": APP})
    with urllib.request.urlopen(req, timeout=6) as r:
        data = json.loads(r.read().decode("utf-8"))
    return str(data.get("clientVersionUpload", "")), str(data.get("version", ""))


def roblox_status(local, latest):
    """Returns (text, level) with level 'ok', 'warn' or 'muted'."""
    if isinstance(latest, Exception) or not latest or not latest[0]:
        if local:
            return f"Roblox {local} installed · could not check for updates (offline?)", "muted"
        return "Roblox not found · could not check for updates (offline?)", "warn"
    guid, readable = latest
    nice = f"{readable} ({guid})" if readable else guid
    if not local:
        return f"Roblox not found · latest version is {nice}", "warn"
    if local == guid:
        return f"Roblox {local} ✔ up to date" + (f" · {readable}" if readable else ""), "ok"
    return (f"Roblox {local} is outdated ⚠ latest: {nice}. Start Roblox once via Bloxstrap to update, "
            f"then check your meshes again."), "warn"


def list_sets():
    if not SETS.is_dir():
        return []
    return sorted((d.name for d in SETS.iterdir() if d.is_dir()), key=str.lower)


def set_files(setname):
    d = SETS / setname
    if not d.is_dir():
        return []
    return sorted((p for p in d.iterdir() if p.is_file() and p.suffix.lower() == ".mesh"),
                  key=lambda p: p.name.lower())


def applied_files(cfg, setname):
    return cfg["sets"].get(setname, {}).get("applied", [])


def owned_names(cfg):
    return {f.lower() for st in cfg["sets"].values() for f in st.get("applied", [])}


def foreign_files(cfg, setname):
    """Files of this set that already exist in the meshes folder but were not put there by MeshSwapper."""
    mdir = meshes_dir(cfg)
    owned = owned_names(cfg)
    return [p.name for p in set_files(setname) if (mdir / p.name).exists() and p.name.lower() not in owned]


def apply_set(cfg, setname):
    """Copies all .mesh files of the set into Bloxstrap's meshes folder.

    Only one set is applied at a time: files of other applied sets are removed first.
    Returns (number_copied, skipped_names).
    """
    files = set_files(setname)
    if not files:
        raise ValueError("This set has no .mesh files yet.")
    valid = [p for p in files if header_version(p)]
    skipped = [p.name for p in files if p not in valid]
    if not valid:
        raise MeshError("None of the files in this set are valid Roblox meshes.")
    mdir = ensure_meshes_dir(cfg)
    keep = {p.name.lower() for p in valid}
    for sn, st in cfg["sets"].items():
        for fn in st.get("applied", []):
            if sn != setname or fn.lower() not in keep:
                (mdir / fn).unlink(missing_ok=True)
        if sn != setname:
            st["applied"] = []
    for p in valid:
        shutil.copy2(p, mdir / p.name)
    cfg["sets"].setdefault(setname, {})["applied"] = [p.name for p in valid]
    return len(valid), skipped


def reset_set(cfg, setname):
    mdir = meshes_dir(cfg)
    st = cfg["sets"].get(setname)
    if not st:
        return
    for fn in st.get("applied", []):
        try:
            (mdir / fn).unlink(missing_ok=True)
        except OSError as e:
            raise OSError(f"Could not remove {fn}: {e}")
    st["applied"] = []


def reset_all(cfg):
    for sn in list(cfg["sets"]):
        reset_set(cfg, sn)


def reconcile(cfg):
    """Forget applied files that vanished, and sets whose folder was deleted."""
    mdir = meshes_dir(cfg)
    existing = set(list_sets())
    for sn in list(cfg["sets"]):
        if sn not in existing:
            del cfg["sets"][sn]
            continue
        st = cfg["sets"][sn]
        st["applied"] = [f for f in st.get("applied", []) if (mdir / f).is_file()]


# --------------------------------------------------------------------------
# Mesh creator: primitive shapes -> one Roblox mesh (no GUI code in here)
# --------------------------------------------------------------------------
SHAPES = ["Cube", "Sphere", "Cylinder", "Cone", "Capsule", "Wedge", "Pyramid", "Torus"]
ROUND_SHAPES = ("Sphere", "Cylinder", "Cone", "Capsule", "Torus")
GUIDES = {  # reference boxes (studs) that help to build parts in the right size
    "None": None,
    "Arm / leg  1 x 2 x 1": (1.0, 2.0, 1.0),
    "Torso  2 x 2 x 1": (2.0, 2.0, 1.0),
    "Head  2 x 1 x 1": (2.0, 1.0, 1.0),
    "Cube  1 x 1 x 1": (1.0, 1.0, 1.0),
}


def _orient(V, F):
    """Makes the triangles of a closed shape face outwards (flips them if the volume is negative)."""
    vol = np.einsum("ij,ij->i", V[F[:, 0]], np.cross(V[F[:, 1]], V[F[:, 2]])).sum()
    return F[:, ::-1].copy() if vol < 0 else F


def _flat(polys):
    """Flat-shaded convex shape from polygons (every polygon gets its own vertices).
    Each polygon is turned so that it faces away from the middle of the shape."""
    mid = np.array(sorted({tuple(p) for poly in polys for p in poly}), np.float64).mean(0)
    V, F = [], []
    for poly in polys:
        poly = [tuple(p) for p in poly]
        a, b, c = (np.array(poly[i], np.float64) for i in range(3))
        centre = np.mean(np.array(poly, np.float64), axis=0)
        if np.dot(np.cross(b - a, c - a), centre - mid) < 0:
            poly = poly[::-1]
        base = len(V)
        V.extend(poly)
        for k in range(1, len(poly) - 1):
            F.append((base, base + k, base + k + 1))
    return np.array(V, np.float64), np.array(F, np.int64)


def _revolve(profile, seg):
    """Spins a profile [(radius, y), ...] (bottom to top) around the Y axis.
    Equal neighbouring points make a hard edge (they get their own vertex ring)."""
    seg = max(3, int(seg))
    ang = np.linspace(0, 2 * math.pi, seg, endpoint=False)
    ca, sa = np.cos(ang), np.sin(ang)
    V, rings = [], []
    for r, y in profile:
        if r < 1e-9:
            rings.append([len(V)] * seg)
            V.append((0.0, y, 0.0))
        else:
            rings.append(list(range(len(V), len(V) + seg)))
            V.extend(zip(r * ca, [y] * seg, r * sa))
    F = []
    for i in range(len(profile) - 1):
        (r0, y0), (r1, y1) = profile[i], profile[i + 1]
        if abs(r0 - r1) < 1e-9 and abs(y0 - y1) < 1e-9:
            continue
        for j in range(seg):
            a, b = rings[i][j], rings[i][(j + 1) % seg]
            c, d = rings[i + 1][(j + 1) % seg], rings[i + 1][j]
            for t in ((a, b, c), (a, c, d)):
                if len(set(t)) == 3:
                    F.append(t)
    V = np.array(V, np.float64)
    F = np.array(F, np.int64)
    return V, _orient(V, F)


def _arc(n, r0, y0, rad, y_from, y_to, a_from, a_to):
    return [(r0 + rad * math.cos(a), y0 + (y_to - y_from) * math.sin(a))
            for a in np.linspace(a_from, a_to, n)]


def unit_shape(kind, seg=16):
    """The basic shape with a size of 1 (cube: -0.5 .. 0.5). Returns (V, F)."""
    h = 0.5
    if kind == "Cube":
        P = lambda *a: tuple(a)  # noqa: E731
        return _flat([
            [P(h, -h, -h), P(h, h, -h), P(h, h, h), P(h, -h, h)],      # +x
            [P(-h, -h, h), P(-h, h, h), P(-h, h, -h), P(-h, -h, -h)],  # -x
            [P(-h, h, h), P(h, h, h), P(h, h, -h), P(-h, h, -h)],      # +y
            [P(-h, -h, -h), P(h, -h, -h), P(h, -h, h), P(-h, -h, h)],  # -y
            [P(-h, -h, h), P(h, -h, h), P(h, h, h), P(-h, h, h)],      # +z
            [P(-h, h, -h), P(h, h, -h), P(h, -h, -h), P(-h, -h, -h)],  # -z
        ])
    if kind == "Wedge":  # slope rises from the front (-z, bottom) to the back (+z, top)
        A, B, C, D = (-h, -h, -h), (h, -h, -h), (h, -h, h), (-h, -h, h)
        E, G = (-h, h, h), (h, h, h)
        return _flat([[A, B, C, D], [D, C, G, E], [A, B, G, E], [A, D, E], [B, G, C]])
    if kind == "Pyramid":
        t = (0.0, h, 0.0)
        A, B, C, D = (-h, -h, -h), (h, -h, -h), (h, -h, h), (-h, -h, h)
        return _flat([[A, B, C, D], [A, t, B], [B, t, C], [C, t, D], [D, t, A]])
    if kind == "Sphere":
        n = max(4, int(seg) // 2)
        return _revolve([(h * math.sin(math.pi * i / n), h * math.cos(math.pi * i / n) * -1) for i in range(n + 1)], seg)
    if kind == "Cylinder":
        return _revolve([(0, -h), (h, -h), (h, -h), (h, h), (h, h), (0, h)], seg)
    if kind == "Cone":
        return _revolve([(0, -h), (h, -h), (h, -h), (0, h)], seg)
    if kind == "Capsule":  # a pill: flat-ended caps are round once the shape is stretched
        n = max(3, int(seg) // 4)
        low = [(0.5 * math.sin(a), -0.25 - 0.25 * math.cos(a)) for a in np.linspace(0, math.pi / 2, n + 1)]
        up = [(0.5 * math.cos(a), 0.25 + 0.25 * math.sin(a)) for a in np.linspace(0, math.pi / 2, n + 1)]
        return _revolve(low + up, seg)
    if kind == "Torus":
        R, r = 0.32, 0.18
        seg = max(3, int(seg))
        ns = max(4, seg // 2)
        u = np.linspace(0, 2 * math.pi, seg, endpoint=False)
        v = np.linspace(0, 2 * math.pi, ns, endpoint=False)
        V = np.array([((R + r * math.cos(b)) * math.cos(a), r * math.sin(b), (R + r * math.cos(b)) * math.sin(a))
                      for a in u for b in v], np.float64)
        F = []
        for i in range(seg):
            for j in range(ns):
                a, b = i * ns + j, ((i + 1) % seg) * ns + j
                c, d = ((i + 1) % seg) * ns + (j + 1) % ns, i * ns + (j + 1) % ns
                F += [(a, b, c), (a, c, d)]
        F = np.array(F, np.int64)
        return V, _orient(V, F)
    raise MeshError(f"Unknown shape {kind}")


def rotation_matrix(rx, ry, rz):
    """Degrees -> 3x3 matrix (X first, then Y, then Z)."""
    ax, ay, az = (math.radians(v) for v in (rx, ry, rz))
    cx, sx, cy, sy, cz, sz = math.cos(ax), math.sin(ax), math.cos(ay), math.sin(ay), math.cos(az), math.sin(az)
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return Rz @ Ry @ Rx


def parse_obj(path):
    """Wavefront .obj -> (V, F, UV or None). Polygons are cut into triangles; vertices that differ in
    texture coordinate or normal stay separate, so hard edges survive."""
    pos, tex, nn = [], [], 0
    key_idx, V, UV, F = {}, [], [], []
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if line.startswith("v "):
                    q = line.split()
                    pos.append((float(q[1]), float(q[2]), float(q[3])))
                elif line.startswith("vt "):
                    q = line.split()
                    tex.append((float(q[1]), float(q[2]) if len(q) > 2 else 0.0))
                elif line.startswith("vn "):
                    nn += 1
                elif line.startswith("f "):
                    ids = []
                    for tok in line.split()[1:]:
                        a = tok.split("/")
                        vi = int(a[0])
                        vi = vi - 1 if vi > 0 else len(pos) + vi
                        ti = ni = None
                        if len(a) > 1 and a[1]:
                            t = int(a[1])
                            ti = t - 1 if t > 0 else len(tex) + t
                        if len(a) > 2 and a[2]:
                            m = int(a[2])
                            ni = m - 1 if m > 0 else nn + m
                        key = (vi, ti, ni)
                        j = key_idx.get(key)
                        if j is None:
                            j = key_idx[key] = len(V)
                            V.append(pos[vi])
                            UV.append((tex[ti][0], 1.0 - tex[ti][1]) if ti is not None else (math.nan, math.nan))
                        ids.append(j)
                    for k in range(1, len(ids) - 1):
                        F.append((ids[0], ids[k], ids[k + 1]))
    except (ValueError, IndexError):
        raise MeshError("This OBJ file is damaged or uses a layout I cannot read.")
    except OSError as e:
        raise MeshError(str(e))
    if not F:
        raise MeshError("No triangles found in this OBJ file.")
    V, F, UV = np.array(V, np.float64), np.array(F, np.int64), np.array(UV, np.float64)
    return V, F, (None if np.isnan(UV).all() else UV)


# --------------------------------------------------------------------------
# File converters: every supported 3D / Roblox format is turned into plain triangles.
# A loader returns (V, F, UV or None) as numpy arrays (positions, triangle indices, texture coords).
# --------------------------------------------------------------------------
LOAD_NOTES = []  # short remarks about the file that was loaded last (shown in the status line)
ASSET_CACHE = DATA / "AssetCache"  # meshes downloaded from Roblox for .rbxm files


def _note(text):
    if text not in LOAD_NOTES:
        LOAD_NOTES.append(text)


def _read(path):
    try:
        return Path(path).read_bytes()
    except OSError as e:
        raise MeshError(str(e))


def _xml_root(data):
    import xml.etree.ElementTree as ET
    try:
        root = ET.fromstring(data)
    except ET.ParseError as e:
        raise MeshError(f"This file is not valid XML: {e}")
    for el in root.iter():
        if isinstance(el.tag, str) and "}" in el.tag:
            el.tag = el.tag.split("}", 1)[1]  # drop xml namespaces
    return root


def _finish(V, F, UV=None):
    V = np.asarray(V, np.float64).reshape(-1, 3)
    F = np.asarray(F, np.int64).reshape(-1, 3)
    if len(V) and len(F):
        F = F[((F >= 0) & (F < len(V))).all(1)]
        F = F[np.isfinite(V).all(1)[F].all(1)]
    if not len(F):
        raise MeshError("No triangles found in this file.")
    if UV is not None:
        UV = np.asarray(UV, np.float64)
        if len(UV) != len(V) or np.isnan(UV).all():
            UV = None
    return V, F, UV


def _merge(parts):
    """[(V, F, UV or None), ...] -> one (V, F, UV or None)."""
    parts = [p for p in parts if p is not None and len(p[1])]
    if not parts:
        raise MeshError("No triangles found in this file.")
    anyuv = any(p[2] is not None for p in parts)
    Vs, Fs, Us, base = [], [], [], 0
    for V, F, UV in parts:
        Vs.append(V)
        Fs.append(F + base)
        base += len(V)
        if anyuv:
            Us.append(UV if UV is not None else np.full((len(V), 2), np.nan))
    return np.concatenate(Vs), np.concatenate(Fs), (np.concatenate(Us) if anyuv else None)


def _zup(V):
    """Z-up -> Y-up (a turn of -90 degrees around X)."""
    return np.stack([V[:, 0], V[:, 2], -V[:, 1]], 1)


def _apply(V, F, M):
    """Moves a mesh with a 4x4 matrix (column-vector convention). Mirrored matrices flip the triangles."""
    M = np.asarray(M, np.float64)
    V2 = V @ M[:3, :3].T + M[:3, 3]
    return V2, (F[:, ::-1] if np.linalg.det(M[:3, :3]) < 0 else F)


def _fan(ids):
    return [(ids[0], ids[k], ids[k + 1]) for k in range(1, len(ids) - 1)]


def _axis_angle(x, y, z, deg):
    n = math.sqrt(x * x + y * y + z * z) or 1.0
    x, y, z = x / n, y / n, z / n
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    t = 1 - c
    M = np.eye(4)
    M[:3, :3] = [[t * x * x + c, t * x * y - s * z, t * x * z + s * y],
                 [t * x * y + s * z, t * y * y + c, t * y * z - s * x],
                 [t * x * z - s * y, t * y * z + s * x, t * z * z + c]]
    return M


def _quat_matrix(x, y, z, w):
    n = x * x + y * y + z * z + w * w
    s = 2.0 / n if n else 0.0
    return np.array([[1 - s * (y * y + z * z), s * (x * y - z * w), s * (x * z + y * w)],
                     [s * (x * y + z * w), 1 - s * (x * x + z * z), s * (y * z - x * w)],
                     [s * (x * z - y * w), s * (y * z + x * w), 1 - s * (x * x + y * y)]])


# ---- STL -----------------------------------------------------------------
def load_stl(path):
    raw = _read(path)
    n = struct.unpack_from("<I", raw, 80)[0] if len(raw) >= 84 else -1
    if n >= 0 and 84 + 50 * n == len(raw):  # binary STL
        dt = np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")])
        V = np.frombuffer(raw, dt, count=n, offset=84)["v"].reshape(-1, 3).astype(np.float64)
    else:  # text STL
        pts = re.findall(rb"vertex\s+(\S+)\s+(\S+)\s+(\S+)", raw)
        try:
            V = np.array([[float(a), float(b), float(c)] for a, b, c in pts], np.float64).reshape(-1, 3)
        except ValueError:
            raise MeshError("This STL file is damaged.")
        V = V[: len(V) // 3 * 3]
    return _finish(V, np.arange(len(V)).reshape(-1, 3))


# ---- OFF -----------------------------------------------------------------
def load_off(path):
    lines = [ln.split("#")[0].strip() for ln in _read(path).decode("ascii", "ignore").splitlines()]
    lines = [ln for ln in lines if ln]
    if not lines or "OFF" not in lines[0].upper():
        raise MeshError("This is not a valid OFF file.")
    head = lines[0].split()
    try:
        if len(head) >= 3:
            nv, nf = int(head[1]), int(head[2])
            body = lines[1:]
        else:
            nv, nf = (int(x) for x in lines[1].split()[:2])
            body = lines[2:]
        V = np.array([[float(x) for x in ln.split()[:3]] for ln in body[:nv]], np.float64)
        F = []
        for ln in body[nv:nv + nf]:
            q = ln.split()
            k = int(q[0])
            F += _fan([int(x) for x in q[1:1 + k]])
    except (ValueError, IndexError):
        raise MeshError("This OFF file is damaged.")
    return _finish(V, np.array(F, np.int64))


# ---- PLY -----------------------------------------------------------------
_PLY_T = {"char": "b", "int8": "b", "uchar": "B", "uint8": "B", "short": "h", "int16": "h", "ushort": "H",
          "uint16": "H", "int": "i", "int32": "i", "uint": "I", "uint32": "I", "float": "f", "float32": "f",
          "double": "d", "float64": "d"}


def load_ply(path):
    raw = _read(path)
    m = re.search(rb"end_header\r?\n", raw)
    if not raw.startswith(b"ply") or not m:
        raise MeshError("This is not a valid PLY file.")
    fmt, elements = "ascii", []
    try:
        for line in raw[:m.start()].decode("ascii", "ignore").splitlines():
            t = line.split()
            if not t:
                continue
            if t[0] == "format":
                fmt = t[1]
            elif t[0] == "element":
                elements.append([t[1], int(t[2]), []])
            elif t[0] == "property" and elements:
                if t[1] == "list":
                    elements[-1][2].append((t[4], True, _PLY_T[t[2]], _PLY_T[t[3]]))
                else:
                    elements[-1][2].append((t[2], False, _PLY_T[t[1]], None))
        body = raw[m.end():]
        cols, faces = None, []

        def face(name, vals):
            if name in ("vertex_indices", "vertex_index"):
                faces.extend(_fan(list(vals)))

        if fmt == "ascii":
            tok, pos = body.decode("ascii", "ignore").split(), 0
            for name, count, props in elements:
                if name == "vertex" and not any(p[1] for p in props):
                    w = len(props)
                    arr = np.array(tok[pos:pos + count * w], np.float64).reshape(count, w)
                    pos += count * w
                    cols = {p[0]: arr[:, i] for i, p in enumerate(props)}
                    continue
                for _ in range(count):
                    for pname, is_list, _ct, _it in props:
                        if is_list:
                            k = int(tok[pos])
                            face(pname if name == "face" else "", [int(x) for x in tok[pos + 1:pos + 1 + k]])
                            pos += 1 + k
                        else:
                            pos += 1
        elif fmt in ("binary_little_endian", "binary_big_endian"):
            e = "<" if fmt == "binary_little_endian" else ">"
            pos = 0
            for name, count, props in elements:
                if not any(p[1] for p in props):
                    dt = np.dtype([(p[0], e + p[2]) for p in props])
                    arr = np.frombuffer(body, dt, count=count, offset=pos)
                    pos += dt.itemsize * count
                    if name == "vertex":
                        cols = {n: arr[n].astype(np.float64) for n in dt.names}
                    continue
                for _ in range(count):
                    for pname, is_list, ct, it in props:
                        if is_list:
                            k = struct.unpack_from(e + ct, body, pos)[0]
                            pos += struct.calcsize(e + ct)
                            vals = struct.unpack_from(f"{e}{k}{it}", body, pos)
                            pos += struct.calcsize(e + it) * k
                            if name == "face":
                                face(pname, vals)
                        else:
                            pos += struct.calcsize(e + ct)
        else:
            raise MeshError(f"Unknown PLY format '{fmt}'.")
    except (ValueError, KeyError, IndexError, struct.error, TypeError):
        raise MeshError("This PLY file is damaged or uses a layout I cannot read.")
    if cols is None or not all(k in cols for k in ("x", "y", "z")):
        raise MeshError("This PLY file has no vertex positions.")
    V = np.stack([cols["x"], cols["y"], cols["z"]], 1)
    UV = None
    for a, b in (("u", "v"), ("s", "t"), ("texture_u", "texture_v"), ("texture_s", "texture_t")):
        if a in cols and b in cols:
            UV = np.stack([cols[a], 1.0 - cols[b]], 1)
            break
    if not faces:
        raise MeshError("This PLY file has no faces (it may be a point cloud).")
    return _finish(V, np.array(faces, np.int64), UV)


# ---- glTF / GLB ----------------------------------------------------------
_GLTF_CT = {5120: ("b", 1, 127.0), 5121: ("B", 1, 255.0), 5122: ("h", 2, 32767.0), 5123: ("H", 2, 65535.0),
            5125: ("I", 4, 4294967295.0), 5126: ("f", 4, 1.0)}
_GLTF_N = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT2": 4, "MAT3": 9, "MAT4": 16}


def load_gltf(path):
    raw = _read(path)
    glb = None
    try:
        if raw[:4] == b"glTF":
            doc, pos = None, 12
            while pos + 8 <= len(raw):
                clen, ctype = struct.unpack_from("<II", raw, pos)
                chunk = raw[pos + 8:pos + 8 + clen]
                pos += 8 + clen
                if ctype == 0x4E4F534A:
                    doc = json.loads(chunk.decode("utf-8"))
                elif ctype == 0x004E4942 and glb is None:
                    glb = chunk
            if doc is None:
                raise ValueError
        else:
            doc = json.loads(raw.decode("utf-8"))
    except (ValueError, struct.error):
        raise MeshError("This is not a valid glTF / GLB file.")
    req = set(doc.get("extensionsRequired", []))
    if req & {"KHR_draco_mesh_compression", "EXT_meshopt_compression"}:
        raise MeshError("This glTF uses Draco/meshopt compression. Export it again without compression.")
    from urllib.parse import unquote
    buffers = []
    for b in doc.get("buffers", []):
        uri = b.get("uri")
        if uri is None:
            buffers.append(glb or b"")
        elif uri.startswith("data:"):
            buffers.append(base64.b64decode(uri.split(",", 1)[1]))
        else:
            buffers.append(_read(Path(path).parent / unquote(uri)))

    def accessor(i):
        a = doc["accessors"][i]
        code, size, norm = _GLTF_CT[a["componentType"]]
        nc, count = _GLTF_N[a["type"]], a["count"]
        if "bufferView" not in a:
            return np.zeros((count, nc))
        bv = doc["bufferViews"][a["bufferView"]]
        stride = bv.get("byteStride") or size * nc
        arr = np.ndarray((count, nc), dtype="<" + code, buffer=buffers[bv["buffer"]],
                         offset=bv.get("byteOffset", 0) + a.get("byteOffset", 0), strides=(stride, size))
        arr = arr.astype(np.float64)
        if a.get("normalized"):
            arr = np.maximum(arr / norm, -1.0)
        return arr

    def mesh_parts(mi):
        out = []
        for prim in doc["meshes"][mi].get("primitives", []):
            mode = prim.get("mode", 4)
            if mode not in (4, 5, 6) or "POSITION" not in prim.get("attributes", {}):
                continue
            P = accessor(prim["attributes"]["POSITION"])
            UV = accessor(prim["attributes"]["TEXCOORD_0"]) if "TEXCOORD_0" in prim["attributes"] else None
            idx = accessor(prim["indices"]).astype(np.int64).ravel() if "indices" in prim else np.arange(len(P))
            if mode == 4:
                F = idx[: len(idx) // 3 * 3].reshape(-1, 3)
            elif mode == 5:
                F = np.array([(idx[i], idx[i + 1], idx[i + 2]) if i % 2 == 0 else (idx[i + 1], idx[i], idx[i + 2])
                              for i in range(len(idx) - 2)], np.int64)
            else:
                F = np.array([(idx[0], idx[i], idx[i + 1]) for i in range(1, len(idx) - 1)], np.int64)
            out.append(_finish(P, F, UV))
        return out

    nodes = doc.get("nodes", [])
    result = []

    def local(n):
        if "matrix" in n:
            return np.array(n["matrix"], np.float64).reshape(4, 4).T
        M = np.eye(4)
        S = np.diag(n.get("scale", [1, 1, 1]))
        M[:3, :3] = _quat_matrix(*n.get("rotation", [0, 0, 0, 1])) @ S
        M[:3, 3] = n.get("translation", [0, 0, 0])
        return M

    def walk(i, parent, depth=0):
        if depth > 64:
            return
        n = nodes[i]
        M = parent @ local(n)
        if "mesh" in n:
            for V, F, UV in mesh_parts(n["mesh"]):
                V, F = _apply(V, F, M)
                result.append((V, F, UV))
        for c in n.get("children", []):
            walk(c, M, depth + 1)

    try:
        if nodes:
            scenes = doc.get("scenes", [])
            if scenes:
                roots = scenes[doc.get("scene", 0)].get("nodes", [])
            else:
                kids = {c for n in nodes for c in n.get("children", [])}
                roots = [i for i in range(len(nodes)) if i not in kids]
            for r in roots:
                walk(r, np.eye(4))
        if not result:
            for mi in range(len(doc.get("meshes", []))):
                result.extend(mesh_parts(mi))
    except (KeyError, IndexError, ValueError, TypeError, struct.error):
        raise MeshError("This glTF file is damaged or uses a layout I cannot read.")
    return _merge(result)


# ---- Collada (.dae) ------------------------------------------------------
def _dae_geometry(mesh):
    def floats(el):
        return np.array((el.text or "").split(), np.float64)

    sources = {}
    for s in mesh.findall("source"):
        arr = s.find("float_array")
        if arr is None:
            continue
        acc = s.find("technique_common/accessor")
        stride = int(acc.get("stride", 1)) if acc is not None else 1
        data = floats(arr)
        sources[s.get("id")] = data[: len(data) // stride * stride].reshape(-1, stride)
    vert_src = {}
    for v in mesh.findall("vertices"):
        for inp in v.findall("input"):
            if inp.get("semantic") == "POSITION":
                vert_src[v.get("id")] = inp.get("source", "").lstrip("#")
    V, UV, F, key_idx = [], [], [], {}
    for prim in mesh:
        if prim.tag not in ("triangles", "polylist", "polygons"):
            continue
        inputs = prim.findall("input")
        stride = max(int(i.get("offset", 0)) for i in inputs) + 1
        pos = nrm = tex = None
        for i in inputs:
            sem, off, src = i.get("semantic"), int(i.get("offset", 0)), i.get("source", "").lstrip("#")
            if sem == "VERTEX" and pos is None:
                pos = (off, vert_src.get(src, src))
            elif sem == "NORMAL" and nrm is None:
                nrm = (off, src)
            elif sem == "TEXCOORD" and tex is None:
                tex = (off, src)
        if pos is None or pos[1] not in sources:
            continue
        P = sources[pos[1]]
        T = sources.get(tex[1]) if tex else None
        polys = []
        if prim.tag == "triangles":
            p = np.array((prim.findtext("p") or "").split(), np.int64)
            n = len(p) // (stride * 3)
            polys = [p[k * stride * 3:(k + 1) * stride * 3] for k in range(n)]
        elif prim.tag == "polylist":
            p = np.array((prim.findtext("p") or "").split(), np.int64)
            at = 0
            for c in (int(x) for x in (prim.findtext("vcount") or "").split()):
                polys.append(p[at:at + c * stride])
                at += c * stride
        else:
            polys = [np.array((q.text or "").split(), np.int64) for q in prim.findall("p")]
        for poly in polys:
            ids = []
            for k in range(len(poly) // stride):
                c = poly[k * stride:(k + 1) * stride]
                vi = int(c[pos[0]])
                ni = int(c[nrm[0]]) if nrm else None
                ti = int(c[tex[0]]) if tex and T is not None else None
                key = (pos[1], vi, ni, ti)
                j = key_idx.get(key)
                if j is None:
                    j = key_idx[key] = len(V)
                    V.append(P[vi][:3])
                    UV.append((T[ti][0], 1.0 - T[ti][1]) if ti is not None else (math.nan, math.nan))
                ids.append(j)
            F.extend(_fan(ids))
    if not F:
        return None
    return np.array(V, np.float64), np.array(F, np.int64), np.array(UV, np.float64)


def load_dae(path):
    root = _xml_root(_read(path))
    try:
        geoms = {}
        for g in root.iter("geometry"):
            mesh = g.find("mesh")
            if mesh is not None:
                r = _dae_geometry(mesh)
                if r is not None:
                    geoms[g.get("id")] = r
        ctrl = {c.get("id"): (c.find("skin").get("source") or "").lstrip("#")
                for c in root.iter("controller") if c.find("skin") is not None}
        nodes = {n.get("id"): n for n in root.iter("node") if n.get("id")}
        result = []

        def matrix(node):
            M = np.eye(4)
            for ch in node:
                t = [float(x) for x in (ch.text or "").split()]
                if ch.tag == "matrix" and len(t) == 16:
                    M = M @ np.array(t).reshape(4, 4)
                elif ch.tag == "translate" and len(t) == 3:
                    T = np.eye(4)
                    T[:3, 3] = t
                    M = M @ T
                elif ch.tag == "rotate" and len(t) == 4:
                    M = M @ _axis_angle(*t)
                elif ch.tag == "scale" and len(t) == 3:
                    M = M @ np.diag(t + [1.0])
            return M

        def add(gid, M):
            if gid in geoms:
                V, F, UV = geoms[gid]
                V, F = _apply(V, F, M)
                result.append((V, F, UV))

        def walk(node, parent, depth=0):
            if depth > 64:
                return
            M = parent @ matrix(node)
            for ig in node.findall("instance_geometry"):
                add((ig.get("url") or "").lstrip("#"), M)
            for ic in node.findall("instance_controller"):
                add(ctrl.get((ic.get("url") or "").lstrip("#"), ""), M)
            for inode in node.findall("instance_node"):
                tgt = nodes.get((inode.get("url") or "").lstrip("#"))
                if tgt is not None:
                    walk(tgt, M, depth + 1)
            for ch in node.findall("node"):
                walk(ch, M, depth + 1)

        scene = root.find(".//visual_scene")
        if scene is not None:
            for n in scene.findall("node"):
                walk(n, np.eye(4))
        if not result:
            result = [g for g in geoms.values()]
    except (ValueError, IndexError, KeyError, TypeError):
        raise MeshError("This Collada file is damaged or uses a layout I cannot read.")
    V, F, UV = _merge(result)
    if (root.findtext("asset/up_axis") or "Y_UP").strip().upper() == "Z_UP":
        V = _zup(V)
    return V, F, UV


# ---- FBX -----------------------------------------------------------------
def _fbx_read_binary(raw):
    ver = struct.unpack_from("<I", raw, 23)[0]
    wide = ver >= 7500
    head, sfmt = (25, "<QQQB") if wide else (13, "<IIIB")
    arr_t = {"f": "<f4", "d": "<f8", "l": "<i8", "i": "<i4", "b": "u1"}
    sca_t = {"Y": "<h", "C": "<B", "I": "<i", "F": "<f", "D": "<d", "L": "<q"}

    def read_prop(p):
        t = chr(raw[p])
        p += 1
        if t in sca_t:
            return struct.unpack_from(sca_t[t], raw, p)[0], p + struct.calcsize(sca_t[t])
        if t in arr_t:
            n, enc, clen = struct.unpack_from("<III", raw, p)
            p += 12
            data = raw[p:p + clen]
            if enc == 1:
                data = zlib.decompress(data)
            return np.frombuffer(data, arr_t[t], count=n), p + clen
        if t in "SR":
            n = struct.unpack_from("<I", raw, p)[0]
            data = raw[p + 4:p + 4 + n]
            return (data.decode("utf-8", "ignore") if t == "S" else data), p + 4 + n
        raise ValueError("bad property type")

    def read_node(p):
        end, nprops, _plen, nlen = struct.unpack_from(sfmt, raw, p)
        if end == 0:
            return None, p + head
        p += head
        name = raw[p:p + nlen].decode("latin1")
        p += nlen
        props = []
        for _ in range(nprops):
            v, p = read_prop(p)
            props.append(v)
        kids = []
        while p < end:
            ch, p = read_node(p)
            if ch is None:
                break
            kids.append(ch)
        return (name, props, kids), end

    top, p = [], 27
    while p + head <= len(raw):
        node, p = read_node(p)
        if node is None:
            break
        top.append(node)
    return top


def _fbx_read_ascii(text):
    text = re.sub(r";[^\n]*", "", text)
    toks = re.findall(r'"[^"]*"|[A-Za-z_][\w.]*:|\{|\}|\*\d+|[^\s,{}]+', text)
    pos = 0

    def num(t):
        if t.startswith('"'):
            return t[1:-1]
        try:
            return float(t)
        except ValueError:
            return t

    def block():
        nonlocal pos
        out = []
        while pos < len(toks) and toks[pos] != "}":
            name = toks[pos]
            if not name.endswith(":"):
                pos += 1
                continue
            pos += 1
            props, kids = [], []
            while pos < len(toks) and toks[pos] not in ("{", "}") and not toks[pos].endswith(":"):
                if not toks[pos].startswith("*"):
                    props.append(num(toks[pos]))
                pos += 1
            if pos < len(toks) and toks[pos] == "{":
                pos += 1
                kids = block()
                pos += 1  # the closing brace
            node = (name[:-1], props, kids)
            for k in kids:  # "a:" holds the values of big arrays
                if k[0] == "a":
                    node = (name[:-1], [np.array(k[1], np.float64)], [])
            out.append(node)
        return out

    return block()


def _fbx_child(node, name):
    for c in node[2]:
        if c[0] == name:
            return c
    return None


def _fbx_props(node):
    d = {}
    p70 = _fbx_child(node, "Properties70")
    for p in (p70[2] if p70 else []):
        if p[0] == "P" and len(p[1]) >= 5:
            d[p[1][0]] = p[1][4:]
    return d


def _fbx_geometry(g):
    vp, pi = _fbx_child(g, "Vertices"), _fbx_child(g, "PolygonVertexIndex")
    if vp is None or pi is None:
        return None
    verts = np.asarray(vp[1][0], np.float64).reshape(-1, 3)
    pvi = np.asarray(pi[1][0], np.int64)
    cv = np.where(pvi < 0, ~pvi, pvi)

    def layer(lname, dname, iname, width):
        el = _fbx_child(g, lname)
        d = _fbx_child(el, dname) if el else None
        if d is None:
            return None
        mapping = (_fbx_child(el, "MappingInformationType") or (0, [""]))[1][0]
        idx = _fbx_child(el, iname)
        arr = np.asarray(d[1][0], np.float64)
        return mapping, (np.asarray(idx[1][0], np.int64) if idx is not None else None), arr[: len(arr) // width * width].reshape(-1, width)

    def pick(m, c, vi, poly):
        mapping, idx, arr = m
        if mapping == "ByPolygonVertex":
            j = int(idx[c]) if idx is not None else c
        elif mapping in ("ByVertice", "ByVertex"):
            j = int(idx[vi]) if idx is not None else vi
        elif mapping == "ByPolygon":
            j = int(idx[poly]) if idx is not None else poly
        else:
            j = 0
        return j if 0 <= j < len(arr) else None

    nrm, uvl = layer("LayerElementNormal", "Normals", "NormalsIndex", 3), layer("LayerElementUV", "UV", "UVIndex", 2)
    V, UV, F, key_idx = [], [], [], {}
    start, poly = 0, 0
    for e in np.nonzero(pvi < 0)[0]:
        ids = []
        for c in range(start, e + 1):
            vi = int(cv[c])
            nj = pick(nrm, c, vi, poly) if nrm else None
            uj = pick(uvl, c, vi, poly) if uvl else None
            key = (vi, tuple(np.round(nrm[2][nj], 3)) if nj is not None else None, uj)
            j = key_idx.get(key)
            if j is None:
                j = key_idx[key] = len(V)
                V.append(verts[vi])
                UV.append((uvl[2][uj][0], 1.0 - uvl[2][uj][1]) if uj is not None else (math.nan, math.nan))
            ids.append(j)
        F.extend(_fan(ids))
        start, poly = e + 1, poly + 1
    if not F:
        return None
    return np.array(V, np.float64), np.array(F, np.int64), np.array(UV, np.float64)


def load_fbx(path):
    raw = _read(path)
    try:
        top = _fbx_read_binary(raw) if raw.startswith(b"Kaydara FBX Binary") else _fbx_read_ascii(raw.decode("utf-8", "ignore"))
        objects = next((n for n in top if n[0] == "Objects"), None)
        if objects is None:
            raise ValueError
        geoms = {n[1][0]: n for n in objects[2] if n[0] == "Geometry" and len(n[1]) >= 3 and n[1][2] == "Mesh"}
        models = {n[1][0]: n for n in objects[2] if n[0] == "Model"}
        parent, geo_models = {}, {}
        conn = next((n for n in top if n[0] == "Connections"), None)
        for c in (conn[2] if conn else []):
            p = c[1]
            if c[0] == "C" and len(p) >= 3 and p[0] == "OO":
                if p[1] in models:
                    parent[p[1]] = p[2]
                elif p[1] in geoms:
                    geo_models.setdefault(p[1], []).append(p[2])
        memo = {}

        def world(mid, depth=0):
            if mid in memo:
                return memo[mid]
            pr = _fbx_props(models[mid])
            M = np.eye(4)
            s = np.asarray([float(x) for x in pr.get("Lcl Scaling", (1, 1, 1))[:3]], np.float64)
            rot = rotation_matrix(*[float(x) for x in pr.get("Lcl Rotation", (0, 0, 0))[:3]])
            pre = rotation_matrix(*[float(x) for x in pr.get("PreRotation", (0, 0, 0))[:3]])
            M[:3, :3] = pre @ rot @ np.diag(s)
            M[:3, 3] = [float(x) for x in pr.get("Lcl Translation", (0, 0, 0))[:3]]
            par = parent.get(mid)
            if par in models and depth < 64:
                M = world(par, depth + 1) @ M
            memo[mid] = M
            return M

        result = []
        for gid, g in geoms.items():
            r = _fbx_geometry(g)
            if r is None:
                continue
            V, F, UV = r
            targets = [m for m in geo_models.get(gid, []) if m in models] or [None]
            for mid in targets:
                V2, F2 = _apply(V, F, world(mid)) if mid is not None else (V, F)
                result.append((V2, F2, UV))
        V, F, UV = _merge(result)
        gs = next((n for n in top if n[0] == "GlobalSettings"), None)
        up = _fbx_props(gs).get("UpAxis", (1,))[0] if gs else 1
        if int(up) == 2:
            V = _zup(V)
        return V, F, UV
    except (struct.error, ValueError, IndexError, KeyError, TypeError, zlib.error):
        raise MeshError("This FBX file is damaged or uses a layout I cannot read.")


# ---- 3MF -----------------------------------------------------------------
def load_3mf(path):
    import zipfile
    try:
        with zipfile.ZipFile(path) as z:
            name = next((n for n in z.namelist() if n.lower().endswith(".model")), None)
            if name is None:
                raise MeshError("This 3MF file has no model inside.")
            root = _xml_root(z.read(name))
    except (zipfile.BadZipFile, OSError) as e:
        raise MeshError(f"This is not a valid 3MF file: {e}")
    try:
        objs = {}
        for o in root.iter("object"):
            mesh = o.find("mesh")
            if mesh is not None:
                V = np.array([[float(v.get(a)) for a in "xyz"] for v in mesh.iter("vertex")], np.float64)
                F = np.array([[int(t.get(a)) for a in ("v1", "v2", "v3")] for t in mesh.iter("triangle")], np.int64)
                objs[o.get("id")] = ("mesh", V, F)
            else:
                objs[o.get("id")] = ("comp", [(c.get("objectid"), c.get("transform")) for c in o.iter("component")])
        result = []

        def mat(t):
            M = np.eye(4)
            if t:
                v = [float(x) for x in t.split()]
                if len(v) == 12:  # row-vector convention: p' = p * A + t
                    M[:3, :3] = np.array(v[:9]).reshape(3, 3).T
                    M[:3, 3] = v[9:]
            return M

        def emit(oid, M, depth=0):
            o = objs.get(oid)
            if o is None or depth > 32:
                return
            if o[0] == "mesh":
                V, F = _apply(o[1], o[2], M)
                result.append((V, F, None))
            else:
                for cid, t in o[1]:
                    emit(cid, M @ mat(t), depth + 1)

        items = list(root.iter("item"))
        for it in items:
            emit(it.get("objectid"), mat(it.get("transform")))
        if not items:
            for oid in objs:
                emit(oid, np.eye(4))
    except (ValueError, TypeError, KeyError):
        raise MeshError("This 3MF file is damaged.")
    V, F, UV = _merge(result)
    return _zup(V), F, UV  # 3MF is Z-up


# ---- Roblox models: .rbxm .rbxmx .rbxl .rbxlx ----------------------------
_RBX_ROT = {
    0x02: (1, 0, 0, 0, 1, 0, 0, 0, 1), 0x03: (1, 0, 0, 0, 0, -1, 0, 1, 0), 0x05: (1, 0, 0, 0, -1, 0, 0, 0, -1),
    0x06: (1, 0, 0, 0, 0, 1, 0, -1, 0), 0x07: (0, 1, 0, 1, 0, 0, 0, 0, -1), 0x09: (0, 0, 1, 1, 0, 0, 0, 1, 0),
    0x0A: (0, -1, 0, 1, 0, 0, 0, 0, 1), 0x0C: (0, 0, -1, 1, 0, 0, 0, -1, 0), 0x0D: (0, 1, 0, 0, 0, 1, 1, 0, 0),
    0x0E: (0, 0, -1, 0, 1, 0, 1, 0, 0), 0x10: (0, -1, 0, 0, 0, -1, 1, 0, 0), 0x11: (0, 0, 1, 0, -1, 0, 1, 0, 0),
    0x14: (-1, 0, 0, 0, 1, 0, 0, 0, -1), 0x15: (-1, 0, 0, 0, 0, 1, 0, 1, 0), 0x17: (-1, 0, 0, 0, -1, 0, 0, 0, 1),
    0x18: (-1, 0, 0, 0, 0, -1, 0, -1, 0), 0x19: (0, 1, 0, -1, 0, 0, 0, 0, 1), 0x1B: (0, 0, -1, -1, 0, 0, 0, 1, 0),
    0x1C: (0, -1, 0, -1, 0, 0, 0, 0, -1), 0x1E: (0, 0, 1, -1, 0, 0, 0, -1, 0), 0x1F: (0, 1, 0, 0, 0, -1, -1, 0, 0),
    0x20: (0, 0, 1, 0, 1, 0, -1, 0, 0), 0x22: (0, -1, 0, 0, 0, 1, -1, 0, 0), 0x23: (0, 0, -1, 0, -1, 0, -1, 0, 0),
}
_RBX_PARTS = {"Part", "MeshPart", "WedgePart", "CornerWedgePart", "TrussPart", "SpawnLocation", "Seat",
              "VehicleSeat", "FlagStand", "SkateboardPlatform"}
_RBX_CSG = {"UnionOperation", "NegateOperation", "IntersectOperation", "PartOperation"}
_RBX_WANT = {"name", "size", "cframe", "meshid", "meshcontent", "shape", "meshtype", "scale", "offset"}


def _lz4_block(src, out_size):
    dst = bytearray()
    i, n = 0, len(src)
    while i < n:
        token = src[i]
        i += 1
        lit = token >> 4
        if lit == 15:
            while True:
                b = src[i]
                i += 1
                lit += b
                if b != 255:
                    break
        dst += src[i:i + lit]
        i += lit
        if i >= n:
            break
        off = src[i] | (src[i + 1] << 8)
        i += 2
        ml = token & 15
        if ml == 15:
            while True:
                b = src[i]
                i += 1
                ml += b
                if b != 255:
                    break
        ml += 4
        start = len(dst) - off
        if off >= ml:
            dst += dst[start:start + ml]
        else:
            for _ in range(ml):
                dst.append(dst[len(dst) - off])
    return bytes(dst)


def _il(data, pos, n, width):
    """Byte-interleaved big-endian array (how .rbxm stores numbers)."""
    b = np.frombuffer(data, np.uint8, n * width, pos).reshape(width, n).astype(np.uint64)
    out = np.zeros(n, np.uint64)
    for k in range(width):
        out = (out << np.uint64(8)) | b[k]
    return out


def _il_i32(data, pos, n):
    u = _il(data, pos, n, 4).astype(np.int64)
    return (u >> 1) ^ -(u & 1)


def _il_f32(data, pos, n):
    u = _il(data, pos, n, 4).astype(np.uint32)
    return ((u >> np.uint32(1)) | (u << np.uint32(31))).view(np.float32).astype(np.float64)


def _rbx_binary(raw):
    pos = 32
    classes, by_ref = {}, {}
    while pos + 16 <= len(raw):
        tag = raw[pos:pos + 4]
        clen, ulen, _r = struct.unpack_from("<III", raw, pos + 4)
        pos += 16
        if clen == 0:
            data = raw[pos:pos + ulen]
            pos += ulen
        else:
            blob = raw[pos:pos + clen]
            pos += clen
            if blob[:4] == b"\x28\xb5\x2f\xfd":
                raise MeshError("This .rbxm uses a newer compression I cannot read. In Studio use "
                                "'Save to File' as .rbxmx (the XML version) and convert that.")
            data = _lz4_block(blob, ulen)
        if tag == b"END\x00":
            break
        if tag == b"INST":
            cid, nlen = struct.unpack_from("<II", data, 0)
            cname = data[8:8 + nlen].decode("utf-8", "ignore")
            p = 8 + nlen + 1
            n = struct.unpack_from("<I", data, p)[0]
            refs = np.cumsum(_il_i32(data, p + 4, n))
            lst = []
            for r in refs:
                d = {"class": cname, "props": {}, "parent": None, "id": int(r)}
                by_ref[int(r)] = d
                lst.append(d)
            classes[cid] = lst
        elif tag == b"PROP":
            cid, nlen = struct.unpack_from("<II", data, 0)
            pname = data[8:8 + nlen].decode("utf-8", "ignore").lower()
            ptype = data[8 + nlen]
            p = 9 + nlen
            insts = classes.get(cid)
            if not insts or pname not in _RBX_WANT:
                continue
            n = len(insts)
            vals = None
            if ptype == 0x01:
                vals, q = [], p
                for _ in range(n):
                    ln = struct.unpack_from("<I", data, q)[0]
                    vals.append(data[q + 4:q + 4 + ln].decode("utf-8", "ignore"))
                    q += 4 + ln
            elif ptype == 0x0E:
                x, y, z = _il_f32(data, p, n), _il_f32(data, p + 4 * n, n), _il_f32(data, p + 8 * n, n)
                vals = [(x[k], y[k], z[k]) for k in range(n)]
            elif ptype == 0x10:
                rots, q = [], p
                for _ in range(n):
                    rid = data[q]
                    q += 1
                    if rid == 0:
                        rots.append(np.array(struct.unpack_from("<9f", data, q)).reshape(3, 3))
                        q += 36
                    else:
                        rots.append(np.array(_RBX_ROT.get(rid, _RBX_ROT[0x02]), np.float64).reshape(3, 3))
                x, y, z = _il_f32(data, q, n), _il_f32(data, q + 4 * n, n), _il_f32(data, q + 8 * n, n)
                vals = [(rots[k], np.array([x[k], y[k], z[k]])) for k in range(n)]
            elif ptype == 0x12:
                vals = [int(v) for v in _il(data, p, n, 4)]
            elif pname in ("meshid", "meshcontent"):  # newer storage types: pick the asset links out of the bytes
                found = re.findall(rb"(?:rbxassetid://|[?&]id=)\d+", data)
                if len(found) == n:
                    vals = [f.decode() for f in found]
            if vals is not None:
                for d, v in zip(insts, vals):
                    d["props"][pname] = v
        elif tag == b"PRNT":
            cnt = struct.unpack_from("<I", data, 1)[0]
            kids = np.cumsum(_il_i32(data, 5, cnt))
            pars = np.cumsum(_il_i32(data, 5 + 4 * cnt, cnt))
            for c, pr in zip(kids, pars):
                if int(c) in by_ref:
                    by_ref[int(c)]["parent"] = by_ref.get(int(pr))
    return list(by_ref.values())


def _rbx_xml(raw):
    root = _xml_root(raw)
    out = []

    def walk(item, parent):
        d = {"class": item.get("class") or "", "parent": parent, "props": {}}
        pr = item.find("Properties")
        for p in (pr if pr is not None else []):
            n, t = (p.get("name") or "").lower(), p.tag
            try:
                if t == "Vector3":
                    d["props"][n] = tuple(float(p.findtext(a) or 0) for a in "XYZ")
                elif t in ("CoordinateFrame", "CFrame"):
                    r = [float(p.findtext(f"R{i}{j}") or (1 if i == j else 0)) for i in range(3) for j in range(3)]
                    d["props"][n] = (np.array(r).reshape(3, 3), np.array([float(p.findtext(a) or 0) for a in "XYZ"]))
                elif t == "token":
                    d["props"][n] = int(p.text)
                elif t in ("Content", "ContentId"):
                    d["props"][n] = p.findtext("url") or p.findtext("uri") or (p.text or "").strip()
                elif t in ("string", "ProtectedString"):
                    d["props"][n] = p.text or ""
            except (ValueError, TypeError):
                pass
        out.append(d)
        for ch in item.findall("Item"):
            walk(ch, d)

    for it in root.findall("Item"):
        walk(it, None)
    return out


def _roblox_asset_mesh(url, budget):
    """Mesh of an uploaded Roblox asset (rbxassetid://123). Returns (V, F) or None."""
    m = re.search(r"rbxassetid://(\d+)|[?&]id=(\d+)", url or "")
    if not m:
        return None
    aid = m.group(1) or m.group(2)
    f = ASSET_CACHE / f"{aid}.mesh"
    if not f.is_file():
        if budget[0] <= 0:
            return None
        budget[0] -= 1
        data = None
        try:
            req = urllib.request.Request(f"https://assetdelivery.roblox.com/v1/asset/?id={aid}",
                                         headers={"User-Agent": "Mozilla/5.0 " + APP})
            with urllib.request.urlopen(req, timeout=8) as r:
                data = r.read()
        except Exception:  # noqa: BLE001  (offline, private asset, ...)
            data = None
        if not data or not data.startswith(b"version "):
            return None
        try:
            ASSET_CACHE.mkdir(parents=True, exist_ok=True)
            f.write_bytes(data)
        except OSError:
            return None
    try:
        prep = prepare_mesh(f)
    except MeshError:
        return None
    V, F = center_mesh(prep["V"], prep["F"])
    return V, F


_SHAPE_BY_ENUM = {0: "Sphere", 1: "Cube", 2: "Cylinder", 3: "Wedge", 4: "Corner"}
_MESHTYPE = {0: "Cylinder", 1: "Cube", 2: "Wedge", 3: "Sphere", 4: "Cylinder", 6: "Cube", 8: "Pyramid", 11: "Corner"}


def _rbx_primitive(kind):
    if kind == "Corner":  # square base, tip above one corner
        A, B, C, D, E = (-.5, -.5, -.5), (.5, -.5, -.5), (.5, -.5, .5), (-.5, -.5, .5), (-.5, .5, -.5)
        return _flat([[A, B, C, D], [A, E, B], [A, D, E], [B, C, E], [C, D, E]])
    V, F = unit_shape(kind)
    if kind == "Cylinder":  # Roblox cylinders lie along the X axis
        V = np.stack([V[:, 1], -V[:, 0], V[:, 2]], 1)
    return V, F


def load_rbx(path):
    raw = _read(path)
    try:
        insts = _rbx_binary(raw) if raw.startswith(b"<roblox!") else _rbx_xml(raw)
    except (struct.error, ValueError, IndexError, KeyError, TypeError):
        raise MeshError("This Roblox file is damaged or uses a layout I cannot read.")
    by_parent = {}
    for i in insts:
        if i["class"] == "SpecialMesh" and i["parent"] is not None:
            by_parent.setdefault(id(i["parent"]), []).append(i)
    budget, parts, lost, unions = [30], [], [], 0
    for i in insts:
        cls, p = i["class"], i["props"]
        if cls in _RBX_CSG:
            unions += 1
            continue
        if cls not in _RBX_PARTS:
            continue
        R, pos = p.get("cframe", (np.eye(3), np.zeros(3)))
        size = np.array(p.get("size", (4.0, 1.0, 2.0)), np.float64)
        name = p.get("name") or cls
        mesh = None
        special = (by_parent.get(id(i)) or [None])[0]
        sp = special["props"] if special else {}
        url = p.get("meshid") or p.get("meshcontent") or sp.get("meshid") or sp.get("meshcontent")
        if url:
            got = _roblox_asset_mesh(url, budget)
            if got is None:
                lost.append(name)
                continue
            V, F = got
            if cls == "MeshPart":  # the mesh is stretched to the part size
                ext = np.maximum(V.max(0) - V.min(0), 1e-9)
                V = V * (size / ext)
            else:  # SpecialMesh: native size times its Scale
                V = V * np.array(sp.get("scale", (1, 1, 1)), np.float64) + np.array(sp.get("offset", (0, 0, 0)), np.float64)
            mesh = (V, F)
        else:
            if special and "meshtype" in sp:
                kind = _MESHTYPE.get(sp["meshtype"], "Cube")
                scale = np.array(sp.get("scale", (1, 1, 1)), np.float64)
            else:
                kind = {"WedgePart": "Wedge", "CornerWedgePart": "Corner"}.get(cls, _SHAPE_BY_ENUM.get(p.get("shape", 1), "Cube"))
                scale = np.ones(3)
            V, F = _rbx_primitive(kind)
            mesh = (V * size * scale, F)
        V, F = mesh
        parts.append((V @ np.asarray(R, np.float64).T + np.asarray(pos, np.float64), F, None))
    if len(parts) > 2000:  # whole places can hold hundreds of thousands of parts
        _note(f"only the first 2000 of {len(parts)} parts were converted")
        parts = parts[:2000]
    if lost:
        shown = ", ".join(lost[:3]) + (f" and {len(lost) - 3} more" if len(lost) > 3 else "")
        _note(f"{len(lost)} mesh part(s) were skipped ({shown}): their meshes could not be downloaded from "
              f"Roblox (offline or not public) - save those .mesh files yourself and convert them directly")
    if unions:
        _note(f"{unions} union(s) skipped (Roblox does not store unions as a normal mesh)")
    if not parts:
        raise MeshError("Nothing I can convert was found in this Roblox file (no parts, or the meshes could not be "
                        "downloaded). Parts that use an uploaded mesh only store a link, so an internet connection "
                        "is needed.")
    return _merge(parts)


def load_mesh_file(path):
    prep = prepare_mesh(path)
    return prep["V"], prep["F"], None


MODEL_FORMATS = {
    ".obj": ("Wavefront OBJ", parse_obj), ".fbx": ("Autodesk FBX", load_fbx), ".stl": ("STL", load_stl),
    ".ply": ("PLY", load_ply), ".off": ("OFF", load_off), ".dae": ("Collada", load_dae),
    ".gltf": ("glTF / GLB", load_gltf), ".glb": ("glTF / GLB", load_gltf), ".3mf": ("3MF", load_3mf),
    ".mesh": ("Roblox mesh", load_mesh_file), ".rbxm": ("Roblox model", load_rbx), ".rbxmx": ("Roblox model", load_rbx),
    ".rbxl": ("Roblox place", load_rbx), ".rbxlx": ("Roblox place", load_rbx),
}


def model_filetypes():
    """File chooser entries: everything supported first, then one entry per format."""
    types = [("All 3D and Roblox files", " ".join("*" + e for e in MODEL_FORMATS))]
    by_label = {}
    for ext, (label, _fn) in MODEL_FORMATS.items():
        by_label.setdefault(label, []).append("*" + ext)
    types += [(label, " ".join(exts)) for label, exts in by_label.items()]
    return types + [("All files", "*.*")]


def load_any_mesh(path):
    """Any supported 3D or Roblox file -> (V, F, UV or None), centred on the middle of its bounding box."""
    del LOAD_NOTES[:]
    ext = Path(path).suffix.lower()
    fmt = MODEL_FORMATS.get(ext)
    if fmt is None:
        raise MeshError(f"'{ext or 'This file'}' is not a format I can convert. Supported: "
                        + ", ".join(e for e in MODEL_FORMATS) + ". (For .blend / .3ds / .max export an .fbx or .obj first.)")
    V, F, UV = fmt[1](path)
    V, F = center_mesh(V, F)
    return V, _orient(V, F), UV



def new_object(kind, n=1):
    return {"name": f"{kind} {n}", "kind": kind, "pos": [0.0, 0.0, 0.0], "rot": [0.0, 0.0, 0.0],
            "scl": [1.0, 1.0, 1.0], "seg": 16, "taper": 0.0, "mirror": False}


def object_geometry(o):
    """World-space triangles (V, F) of one object, including its mirrored copy if asked."""
    if o.get("mesh") is not None:
        V, F = o["mesh"]
        V = V.astype(np.float64).copy()
    else:
        V, F = unit_shape(o["kind"], o.get("seg", 16))
        V = V.copy()
    t = float(o.get("taper", 0.0))
    if abs(t) > 1e-6:
        y = V[:, 1]
        lo, hi = y.min(), y.max()
        f = 1.0 - t * ((y - lo) / max(hi - lo, 1e-9))
        f = np.maximum(f, 0.001)
        V[:, 0] *= f
        V[:, 2] *= f
    V = V * np.asarray(o["scl"], np.float64)
    if o.get("flipx"):  # left/right swap
        V = V * np.array([-1.0, 1.0, 1.0])
        F = F[:, ::-1]
    V = V @ rotation_matrix(*o["rot"]).T + np.asarray(o["pos"], np.float64)
    if o.get("mirror"):
        V2 = V * np.array([-1.0, 1.0, 1.0])
        F2 = F[:, ::-1] + len(V)
        V, F = np.concatenate([V, V2]), np.concatenate([F, F2])
    return V, F


def compute_normals(V, F):
    a, b, c = V[F[:, 0]], V[F[:, 1]], V[F[:, 2]]
    fn = np.cross(b - a, c - a)  # area weighted
    N = np.zeros_like(V)
    for k in range(3):
        np.add.at(N, F[:, k], fn)
    ln = np.linalg.norm(N, axis=1)
    bad = ln < 1e-12
    N = N / np.where(bad, 1.0, ln)[:, None]
    N[bad] = (0.0, 1.0, 0.0)
    return N


def object_uv(o, nv):
    """Texture coordinates of an object's vertices (NaN = no own coordinates, a simple projection is used)."""
    n0 = nv // 2 if o.get("mirror") else nv
    uv = o.get("uv")
    base = np.asarray(uv, np.float64) if uv is not None and len(uv) == n0 else np.full((n0, 2), np.nan)
    return np.concatenate([base, base]) if o.get("mirror") else base


def build_model(objs):
    """Merges all objects. Returns (V, N, F, pieces, UV); pieces = [(V, N, F)] per object (for the preview)."""
    pieces, Vs, Fs, Us, base = [], [], [], [], 0
    for o in objs:
        V, F = object_geometry(o)
        if not len(F):
            continue
        pieces.append((V, compute_normals(V, F), F))
        Vs.append(V)
        Fs.append(F + base)
        Us.append(object_uv(o, len(V)))
        base += len(V)
    if not pieces:
        raise MeshError("Add a shape first.")
    V, F = np.concatenate(Vs), np.concatenate(Fs)
    return V, compute_normals(V, F), F, pieces, np.concatenate(Us)


def planar_uv(V, N):
    """Very simple texture coordinates: each vertex is projected along its main normal axis."""
    lo, hi = V.min(0), V.max(0)
    size = np.maximum(hi - lo, 1e-9)
    ax = np.abs(N).argmax(1)
    pairs = np.array([[2, 1], [0, 2], [0, 1]])  # +-x -> (z, y), +-y -> (x, z), +-z -> (x, y)
    ia, ib = pairs[ax, 0], pairs[ax, 1]
    idx = np.arange(len(V))
    u = (V[idx, ia] - lo[ia]) / size[ia]
    v = (V[idx, ib] - lo[ib]) / size[ib]
    return np.stack([u, 1.0 - v], 1)


def mesh_bytes(V, N, F, center=True, two_sided=True, uv=None):
    """Roblox mesh file, format version 2.00."""
    V = np.asarray(V, np.float64)
    if center:
        V = V - (V.min(0) + V.max(0)) / 2
    own = planar_uv(V, N)
    if uv is not None:
        own = np.where(np.isnan(uv), own, uv)
    uv = own
    dt = np.dtype([("p", "<f4", 3), ("n", "<f4", 3), ("uv", "<f4", 2), ("t", "i1", 4), ("c", "u1", 4)])
    arr = np.zeros(len(V), dt)
    arr["p"], arr["n"], arr["uv"] = V, N, uv
    arr["t"] = (127, 0, 0, 127)
    arr["c"] = (255, 255, 255, 255)
    F = np.asarray(F, np.int64)
    if two_sided:  # also the reversed triangles: visible whichever way Roblox culls, normals stay outward
        F = np.concatenate([F, F[:, ::-1]])
    head = b"version 2.00\n" + struct.pack("<HBBII", 12, 40, 12, len(V), len(F))
    return head + arr.tobytes() + F.astype("<u4").tobytes()


def project_to_json(objs):
    out = []
    for o in objs:
        d = {k: v for k, v in o.items() if k not in ("mesh", "uv")}
        out.append(d)
    return json.dumps({"app": APP, "version": 1, "objects": out}, indent=1)


def project_from_json(text):
    data = json.loads(text)
    objs = []
    for d in data.get("objects", []):
        o = new_object(d.get("kind", "Cube"))
        for k in ("name", "kind", "seg", "taper", "mirror", "flipx", "path"):
            if k in d:
                o[k] = d[k]
        for k in ("pos", "rot", "scl"):
            if k in d and len(d[k]) == 3:
                o[k] = [float(x) for x in d[k]]
        if o["kind"] == "Imported":
            p = o.get("path")
            if not p or not Path(p).is_file():
                continue
            V, F, UV = load_any_mesh(p)
            o["mesh"], o["uv"] = (V, F), UV
        elif o["kind"] not in SHAPES:
            continue
        objs.append(o)
    return objs


def center_mesh(V, F):
    V = np.asarray(V, np.float64)
    used = np.unique(F)
    lo, hi = V[used].min(0), V[used].max(0)
    return (V - (lo + hi) / 2, np.asarray(F, np.int64))



# --------------------------------------------------------------------------
# Roblox control: start the client through Bloxstrap / restart it and rejoin the same game.
# Only the official client is closed and started again. Nothing is injected, and Roblox's own log
# is only read (the same thing Bloxstrap does for its Discord status).
# --------------------------------------------------------------------------
PLAYER_EXE = "RobloxPlayerBeta.exe"
NO_WINDOW = 0x08000000 if os.name == "nt" else 0       # CREATE_NO_WINDOW
DETACHED = (0x00000008 | 0x00000200) if os.name == "nt" else 0  # DETACHED_PROCESS | NEW_PROCESS_GROUP
JOIN_RE = re.compile(r"Joining game '([0-9a-fA-F\-]{36})' place (\d+) at")


def _run(cmd, timeout=15):
    """Runs a console tool without a window and returns its output as text (never None)."""
    p = subprocess.run(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                       timeout=timeout, creationflags=NO_WINDOW)
    return (p.stdout or b"").decode("utf-8", "ignore")


def process_running(exe):
    try:
        return exe.lower() in (_run(["tasklist", "/FI", f"IMAGENAME eq {exe}", "/FO", "CSV", "/NH"]) or "").lower()
    except (OSError, subprocess.SubprocessError):
        return False


def roblox_running():
    return process_running(PLAYER_EXE)


def current_game(max_age=600):
    """(placeId, jobId) of the game the running client joined last, from its newest player log; or None."""
    try:
        logs = [p for p in (LOCAL / "Roblox" / "logs").glob("*.log") if "player" in p.name.lower()]
        logs.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        if not logs or time.time() - logs[0].stat().st_mtime > max_age:
            return None
        with open(logs[0], "rb") as f:
            f.seek(0, 2)
            f.seek(max(0, f.tell() - 3_000_000))
            text = f.read().decode("utf-8", "ignore")
    except OSError:
        return None
    found = JOIN_RE.findall(text)
    if not found:
        return None
    job, place = found[-1]
    return place, job


def game_uri(game):
    return f"roblox://experience?placeId={game[0]}&gameInstanceId={game[1]}"


def close_roblox(timeout=15):
    """Asks Roblox to close; forces it after 3 seconds. True when it is gone."""
    def kill(force):
        _run(["taskkill", "/IM", PLAYER_EXE] + (["/F"] if force else []))
    try:
        kill(False)
        t0 = time.time()
        while time.time() - t0 < timeout:
            if not roblox_running():
                return True
            if time.time() - t0 > 3:
                kill(True)
            time.sleep(0.4)
        return not roblox_running()
    except (OSError, subprocess.SubprocessError):
        return False


def wait_bloxstrap_idle(timeout=6):
    """After Roblox closes, Bloxstrap needs a moment to finish. Starting the next launch too early can be ignored."""
    t0 = time.time()
    while time.time() - t0 < timeout and process_running("Bloxstrap.exe"):
        time.sleep(0.4)


def launch_roblox(cfg, uri=None):
    """Starts Roblox through Bloxstrap (like its 'Launch Roblox' button), optionally straight into a game."""
    exe = bloxstrap_dir(cfg) / "Bloxstrap.exe"
    if exe.is_file():
        subprocess.Popen([str(exe), uri] if uri else [str(exe), "-player"], cwd=str(exe.parent),
                         close_fds=True, creationflags=DETACHED)
    elif uri and hasattr(os, "startfile"):
        os.startfile(uri)  # noqa: S606 - the roblox:// link opens whatever launcher is registered
    else:
        raise FileNotFoundError("Bloxstrap.exe was not found in " + str(exe.parent))


# --------------------------------------------------------------------------
# GUI
# --------------------------------------------------------------------------
BG, PANEL, FG, MUTED = "#0c0818", "#150f2a", "#ede9ff", "#9a90c4"
ACCENT, GREEN, AMBER = "#7c3aed", "#4ade80", "#e0a63a"   # ACCENT = buttons/selection, GREEN = "ok" status text
PINK, GLOW, BTN, HOVER = "#d946ef", "#c4b5fd", "#231a45", "#2a2056"


def mix(c1, c2, t):
    """Blend two #rrggbb colours (t = 0 gives c1, t = 1 gives c2)."""
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(max(0, min(255, round(x + (y - x) * t))) for x, y in zip(a, b))


if tk:
    def fade_in(win, ms=240):
        """Window fades in from transparent."""
        try:
            win.attributes("-alpha", 0.0)
        except tk.TclError:
            return
        steps = max(ms // 16, 1)

        def step(i=1):
            try:
                win.attributes("-alpha", min(i / steps, 1.0))
            except tk.TclError:
                return
            if i < steps:
                win.after(16, lambda: step(i + 1))
        win.after(10, step)

    def fade_color(w, c1, c2, ms=500, key="fg"):
        """Smoothly changes a colour option of a widget."""
        old = getattr(w, "_fade_job", None)
        if old:
            try:
                w.after_cancel(old)
            except tk.TclError:
                pass
        steps = max(ms // 25, 1)

        def step(i=0):
            t = i / steps
            try:
                w.config(**{key: mix(c1, c2, t * t * (3 - 2 * t))})
            except tk.TclError:
                return
            if i < steps:
                w._fade_job = w.after(25, lambda: step(i + 1))
        step()

    def _rr(x1, y1, x2, y2, r):
        return [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2, x2 - r, y2,
                x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]

    class Btn(tk.Canvas):
        """Rounded button with a smooth hover fade and a press effect.
        style='Accent.TButton' makes it green; toggle=True makes it an on/off switch."""

        def __init__(self, master, text="", command=None, style="", toggle=False, on=False, **_kw):
            self._font = tkfont.Font(family="Segoe UI", size=9)
            w = self._font.measure(text) + 32
            h = self._font.metrics("linespace") + 16
            super().__init__(master, width=w, height=h, bg=master.cget("bg"),
                             highlightthickness=0, bd=0, cursor="hand2")
            self.text, self.command, self.toggle = text, command, toggle
            self.accent = style.startswith("Accent")
            self.on = bool(on)
            self.enabled = True
            self.t = self.target = 0.0
            self.job = None
            self.pressed = False
            self.shape = None
            self.bind("<Configure>", lambda _e: self._draw())
            self.bind("<Enter>", lambda _e: self._go(1.0 if self.enabled else 0.0))
            self.bind("<Leave>", self._leave)
            self.bind("<ButtonPress-1>", self._press)
            self.bind("<ButtonRelease-1>", self._release)
            self.bind("<Destroy>", self._gone)

        def enable(self, flag=True):
            self.enabled = bool(flag)
            self.config(cursor="hand2" if self.enabled else "arrow")
            self._draw()

        def _fill(self):
            if not self.enabled:
                return mix(BTN, BG, 0.45)
            base = ACCENT if (self.accent or self.on) else BTN
            c = mix(base, "#ffffff", 0.14 * self.t)
            return mix(c, "#000000", 0.22) if self.pressed else c

        def _draw(self):
            self.delete("all")
            w, h = max(self.winfo_width(), 4), max(self.winfo_height(), 4)
            self.shape = self.create_polygon(_rr(1, 1, w - 1, h - 1, 9), smooth=True,
                                             fill=self._fill(), outline="")
            self.create_text(w / 2, h / 2 + (1 if self.pressed else 0), text=self.text,
                             fill=MUTED if not self.enabled else ("white" if (self.accent or self.on) else FG), font=self._font)

        def _recolor(self):
            try:
                self.itemconfig(self.shape, fill=self._fill())
            except tk.TclError:
                pass

        def _go(self, target):
            self.target = target
            if self.job is None:
                self._step()

        def _step(self):
            self.job = None
            d = self.target - self.t
            if abs(d) < 0.02:
                self.t = self.target
            else:
                self.t += d * 0.35
                try:
                    self.job = self.after(16, self._step)
                except tk.TclError:
                    return
            self._recolor()

        def _leave(self, _e):
            self.pressed = False
            self._go(0.0)
            self._draw()

        def _press(self, _e):
            if not self.enabled:
                return
            self.pressed = True
            self._draw()

        def _release(self, e):
            if not self.enabled:
                return
            was = self.pressed
            self.pressed = False
            self._draw()
            if was and 0 <= e.x <= self.winfo_width() and 0 <= e.y <= self.winfo_height():
                if self.toggle:
                    self.on = not self.on
                    self._draw()
                if self.command:
                    self.command(self.on) if self.toggle else self.command()

        def _gone(self, _e):
            if self.job:
                try:
                    self.after_cancel(self.job)
                except tk.TclError:
                    pass

    class Shimmer(tk.Canvas):
        """Thin animated gradient strip at the top of the window."""
        N = 90
        PAL = [mix("#5b3df5", PINK, i / 31) for i in range(32)]

        def __init__(self, master, height=3):
            super().__init__(master, height=height, bg=BG, highlightthickness=0, bd=0)
            self.ph = 0.0
            self.segs = []
            self.bind("<Configure>", self._layout)
            self._tick()

        def _layout(self, e):
            self.delete("all")
            self.segs = []
            for i in range(self.N):
                self.segs.append(self.create_rectangle(e.width * i / self.N, 0, e.width * (i + 1) / self.N + 1,
                                                       e.height, fill=ACCENT, width=0))

        def _tick(self):
            self.ph += 0.05
            try:
                for i, sid in enumerate(self.segs):
                    k = 0.5 + 0.5 * math.sin(6.283 * 1.4 * i / self.N - self.ph)
                    self.itemconfig(sid, fill=self.PAL[int(k * 31)])
                self.after(40, self._tick)
            except tk.TclError:
                pass

    class Stars(tk.Canvas):
        """Twinkling, slowly drifting star field with an occasional shooting star."""

        def __init__(self, master, height=52):
            super().__init__(master, height=height, bg=BG, highlightthickness=0, bd=0)
            rnd = random.Random(5)
            self.stars = [[rnd.random(), rnd.random(), rnd.uniform(0.004, 0.015), rnd.uniform(0, 6.3),
                           rnd.uniform(1.2, 2.6)] for _ in range(46)]
            self.ids = []
            self.shoot = None
            self.sid = None
            self.ph = 0.0
            self.bind("<Configure>", self._layout)
            self._tick()

        def _layout(self, _e):
            self.delete("all")
            self.ids = [self.create_oval(0, 0, 1, 1, fill=BG, width=0) for _ in self.stars]
            self.sid = self.create_line(0, 0, 0, 0, fill=BG, width=2, capstyle="round")

        def _tick(self):
            try:
                w, h = max(self.winfo_width(), 2), max(self.winfo_height(), 2)
                self.ph += 0.06
                for st, sid in zip(self.stars, self.ids):
                    st[0] = (st[0] - st[2] * 0.5) % 1.0  # drift to the left
                    k = 0.5 + 0.5 * math.sin(self.ph * 1.6 + st[3])
                    x, y, r = st[0] * w, st[1] * h, st[4] * (0.7 + 0.3 * k)
                    self.coords(sid, x - r, y - r, x + r, y + r)
                    self.itemconfig(sid, fill=mix(BG, "#ffffff" if st[4] > 2.1 else GLOW, 0.2 + 0.8 * k))
                if self.sid is not None and self.shoot is None and random.random() < 0.012:
                    self.shoot = [w * random.uniform(0.5, 1.0), random.uniform(0, h * 0.4), 0]
                if self.shoot:
                    x, y, i = self.shoot
                    i += 1
                    self.shoot[2] = i
                    hx, hy = x - i * 9, y + i * 3.2
                    self.coords(self.sid, hx, hy, hx + 26, hy - 9)
                    self.itemconfig(self.sid, fill=mix(BG, "#ffffff", max(0.0, 1 - i / 26)))
                    if i >= 26:
                        self.shoot = None
                        self.itemconfig(self.sid, fill=BG)
                self.after(50, self._tick)
            except tk.TclError:
                pass

    class Link(tk.Label):
        """Clickable text that glows on hover."""

        def __init__(self, master, text, url):
            self._f = tkfont.Font(family="Segoe UI", size=9)
            super().__init__(master, text=text, bg=master.cget("bg"), fg=GLOW, cursor="hand2", font=self._f)
            self.bind("<Enter>", lambda _e: (self._f.configure(underline=True),
                                             fade_color(self, GLOW, "#ffffff", 160)))
            self.bind("<Leave>", lambda _e: (self._f.configure(underline=False),
                                             fade_color(self, "#ffffff", GLOW, 200)))
            self.bind("<Button-1>", lambda _e: webbrowser.open(url))

    def hover_list(lb):
        """Highlights the row under the mouse in a Listbox."""
        state = {"i": -1}

        def clear():
            i = state["i"]
            state["i"] = -1
            if 0 <= i < lb.size():
                try:
                    lb.itemconfig(i, background=PANEL)
                except tk.TclError:
                    pass

        def motion(e):
            i = lb.nearest(e.y)
            bb = lb.bbox(i) if 0 <= i < lb.size() else None
            if not bb or not (bb[1] <= e.y <= bb[1] + bb[3]):
                return clear()
            if i != state["i"]:
                clear()
                state["i"] = i
                lb.itemconfig(i, background=HOVER)
        lb.bind("<Motion>", motion, add="+")
        lb.bind("<Leave>", lambda _e: clear(), add="+")

    def ease_out(k):
        k = max(0.0, min(1.0, k))
        return 1 - (1 - k) ** 3

    def slide_in(win, w, h, dy=28, ms=380):
        """Shows a hidden window: it glides up into the middle of the screen while it fades in."""
        try:
            sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
            x, y = max((sw - w) // 2, 0), max((sh - h) // 2 - 20, 0)
            win.attributes("-alpha", 0.0)
            win.geometry(f"{w}x{h}+{x}+{y + dy}")
            win.deiconify()
        except tk.TclError:
            try:
                win.deiconify()
            except tk.TclError:
                pass
            return
        t0 = time.monotonic()

        def step():
            k = min((time.monotonic() - t0) / (ms / 1000.0), 1.0)
            e = ease_out(k)
            try:
                win.attributes("-alpha", e)
                win.geometry(f"+{x}+{round(y + dy * (1 - e))}")
            except tk.TclError:
                return
            if k < 1.0:
                win.after(14, step)
        step()

    class Splash(tk.Toplevel):
        """Start-up screen: glowing logo, orbiting ring and a progress bar that follows the real loading steps."""
        W, H = 460, 290

        def __init__(self, master):
            super().__init__(master)
            self.overrideredirect(True)
            self.configure(bg=BG)
            sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
            self.geometry(f"{self.W}x{self.H}+{max((sw - self.W) // 2, 0)}+{max((sh - self.H) // 2 - 30, 0)}")
            self.cv = tk.Canvas(self, width=self.W, height=self.H, bg=BG, highlightthickness=0, bd=0)
            self.cv.pack()
            try:
                self.logo = tk.PhotoImage(data=LOGO_B64)
            except tk.TclError:
                self.logo = None
            rnd = random.Random(7)
            self.dust = [(rnd.uniform(8, self.W - 8), rnd.uniform(0, self.H), rnd.uniform(6, 22),
                          rnd.uniform(0, 6.3), rnd.choice((1, 1, 2))) for _ in range(26)]
            self.t0 = self.last = time.monotonic()
            self.target = self.shown = 0.0
            self.text = "Starting…"
            self.finishing = self.dead = self.drew_error = False
            self.hold = self.out = self.cb = None
            try:
                self.attributes("-alpha", 0.0)
            except tk.TclError:
                pass
            self.update_idletasks()
            self._tick()

        def set(self, frac, text=None):
            self.target = max(self.target, min(frac, 1.0))
            if text:
                self.text = text

        def finish(self, cb):
            """Fill the bar, fade out, then call cb()."""
            self.cb, self.finishing, self.target, self.text = cb, True, 1.0, "Ready"

        def kill(self):
            if not self.dead:
                self.dead = True
                try:
                    self.destroy()
                except tk.TclError:
                    pass

        def _end(self):
            cb, self.cb = self.cb, None
            self.kill()
            if cb:
                cb()

        def _tick(self):
            if self.dead:
                return
            now = time.monotonic()
            dt, self.last = min(now - self.last, 0.1), now
            t = now - self.t0
            self.shown += (self.target - self.shown) * min(1.0, dt * 5.0)
            alpha = ease_out(t / 0.3)
            if self.finishing and self.shown > 0.985:
                if self.hold is None:
                    self.hold = now
                elif self.out is None and now - self.hold > 0.28:
                    self.out = now
            if self.out is not None:
                k = (now - self.out) / 0.25
                if k >= 1:
                    return self._end()
                alpha *= 1 - k
            try:
                self.attributes("-alpha", max(alpha, 0.0))
                self.draw(t)
            except tk.TclError:
                return self.kill()
            except Exception:  # noqa: BLE001 - a drawing bug must never block start-up
                if not self.drew_error:
                    self.drew_error = True
                    log_error()
            self.after(16, self._tick)

        def _pill(self, x0, x1, y, h, col):
            cv, r = self.cv, h / 2
            cv.create_oval(x0, y - r, x0 + h, y + r, fill=col, outline="")
            cv.create_oval(x1 - h, y - r, x1, y + r, fill=col, outline="")
            cv.create_rectangle(x0 + r, y - r, x1 - r, y + r, fill=col, width=0)

        def draw(self, t):
            cv, W, H = self.cv, self.W, self.H
            cv.delete("all")
            cx, cy = W / 2, 100
            pulse = 1 + 0.06 * math.sin(t * 2.4)
            for i in range(12, 0, -1):  # soft glow behind the logo
                r = (12 + i * 7) * pulse
                cv.create_oval(cx - r, cy - r, cx + r, cy + r, fill=mix(BG, ACCENT, 0.035 * (13 - i)), outline="")
            for x, y, sp, ph, s in self.dust:  # drifting, twinkling dust
                yy = (y - t * sp) % H
                k = 0.2 + 0.35 * (0.5 + 0.5 * math.sin(t * 2.0 + ph))
                cv.create_oval(x - s, yy - s, x + s, yy + s, fill=mix(BG, GLOW, k), outline="")
            R = 50
            cv.create_oval(cx - R, cy - R, cx + R, cy + R, outline=mix(BG, ACCENT, 0.4), width=1)
            cv.create_arc(cx - R, cy - R, cx + R, cy + R, start=(-t * 230) % 360, extent=80, style="arc",
                          outline=PINK, width=3)
            cv.create_arc(cx - R, cy - R, cx + R, cy + R, start=(-t * 150 + 180) % 360, extent=40, style="arc",
                          outline=GLOW, width=2)
            for k in range(4):  # a little comet
                a = t * 3.2 - k * 0.22
                px, py, rr = cx + R * math.cos(a), cy + R * math.sin(a), 4 - k * 0.8
                cv.create_oval(px - rr, py - rr, px + rr, py + rr, fill=mix(BG, "#ffffff", 1 - k * 0.27), outline="")
            if self.logo is not None:
                cv.create_image(cx, cy + 3 * math.sin(t * 2.0), image=self.logo)
            k = ease_out((t - 0.15) / 0.6)
            cv.create_text(cx, 188 + (1 - k) * 12, text=APP, fill=mix(BG, FG, k), font=("Segoe UI", 22, "bold"))
            k = ease_out((t - 0.5) / 0.6)
            cv.create_text(cx, 214, text="swap your Roblox meshes", fill=mix(BG, MUTED, k), font=("Segoe UI", 10))
            x0, x1, y, h = 60, W - 60, 246, 6
            self._pill(x0, x1, y, h, mix(BG, ACCENT, 0.22))
            fw = (x1 - x0) * max(0.0, min(self.shown, 1.0))
            if fw > h:
                self._pill(x0, x0 + fw, y, h, mix(ACCENT, PINK, 1.0))
                n = max(int(fw / 4), 2)
                shine = (t * 170) % (fw + 60) - 30
                r = h / 2
                for i in range(n):
                    xa, xb = x0 + r + (fw - h) * i / n, x0 + r + (fw - h) * (i + 1) / n + 1
                    col = mix(ACCENT, PINK, i / n)
                    col = mix(col, "#ffffff", 0.4 * max(0.0, 1 - abs((xa - x0) - shine) / 26))
                    cv.create_rectangle(xa, y - r, xb, y + r, fill=col, width=0)
                cv.create_oval(x0, y - r, x0 + h, y + r, fill=ACCENT, outline="")
            cv.create_text(x0, 268, text=self.text, anchor="w", fill=MUTED, font=("Segoe UI", 9))
            cv.create_text(x1, 268, text=f"{int(self.shown * 100)}%", anchor="e", fill=GLOW, font=("Segoe UI", 9))
            # the border is drawn last so the glow can never paint over it
            cv.create_rectangle(0, 0, W - 1, H - 1, outline=mix(ACCENT, PINK, 0.5 + 0.5 * math.sin(t * 1.6)), width=1)

    class Preview(tk.Canvas):
        def __init__(self, master):
            super().__init__(master, bg="#080512", highlightthickness=0, width=440, height=300)
            self.scene = None
            self.photo = None
            self.yaw, self.pitch, self.zoom = math.pi + 0.45, -0.15, 1.0
            self.drag = None
            self.dragging = False
            self.pending = False
            self.cfg_job = None
            self.msg = "Select a set to see the preview"
            self.spin = False
            self.spin_id = 0
            self.spin_last = 0.0
            self.intro_zoom, self.intro_yaw, self.intro_k, self.intro_id = 1.0, 0.0, 1.0, 0
            self.busy, self.busy_id = False, 0
            self.after(60, self._pulse)
            self.bind("<ButtonPress-1>", self._down)
            self.bind("<B1-Motion>", self._move)
            self.bind("<ButtonRelease-1>", self._up)
            self.bind("<MouseWheel>", self._wheel)
            self.bind("<Configure>", self._configure)

        def _pulse(self):
            """Gentle breathing of the hint text while there is nothing to show."""
            try:
                if self.scene is None:
                    k = 0.5 + 0.5 * math.sin(time.monotonic() * 2.2)
                    self.itemconfig("msg", fill=mix("#3a2f66", MUTED, k))
                self.after(60, self._pulse)
            except tk.TclError:
                pass

        def set_spin(self, on):
            self.spin = bool(on)
            self.spin_id += 1
            if self.spin:
                self.spin_last = time.monotonic()
                self._spin_step(self.spin_id)
            elif self.scene is not None:
                self._draw()

        def _spin_step(self, sid):
            if not self.spin or sid != self.spin_id:
                return
            now = time.monotonic()
            dt = min(now - self.spin_last, 0.1)
            self.spin_last = now
            if self.scene is not None and not self.dragging and self.drag is None:
                self.yaw += 0.7 * dt  # time based, so the speed is the same on slow and fast PCs
                self._draw()
            self.after(15, lambda: self._spin_step(sid))

        def clear(self, msg):
            self.intro_id += 1
            self.intro_zoom, self.intro_yaw, self.intro_k = 1.0, 0.0, 1.0
            self.scene, self.msg = None, msg
            self.busy = msg.rstrip().endswith("…")  # "Loading preview…" / "Converting …" get a spinner
            self.busy_id += 1
            self._draw()
            if self.busy:
                self._busy_step(self.busy_id, time.monotonic())

        def _busy_step(self, bid, t0):
            if not self.busy or bid != self.busy_id or self.scene is not None:
                return
            try:
                self.delete("busy")
                w, h = max(self.winfo_width(), 2), max(self.winfo_height(), 2)
                cx, cy, r, t = w / 2, h / 2 - 26, 22, time.monotonic() - t0
                self.create_oval(cx - r, cy - r, cx + r, cy + r, outline="#2a2056", width=3, tags="busy")
                self.create_arc(cx - r, cy - r, cx + r, cy + r, start=(-t * 260) % 360, extent=95, style="arc",
                                outline=PINK, width=3, tags="busy")
                self.create_arc(cx - r, cy - r, cx + r, cy + r, start=(-t * 160 + 180) % 360, extent=45, style="arc",
                                outline=GLOW, width=3, tags="busy")
                self.after(30, lambda: self._busy_step(bid, t0))
            except tk.TclError:
                pass

        def set_scene(self, scene):
            if not scene:
                return self.clear("Nothing to preview")
            self.busy = False
            self.busy_id += 1
            self.scene, self.msg = scene, ""
            self.intro_id += 1
            self._intro_step(self.intro_id, time.monotonic())

        def _intro_step(self, iid, t0):
            """The model zooms in, turns a little and fades up out of the dark (quick, low-cost frames)."""
            if iid != self.intro_id or self.scene is None:
                return
            k = min((time.monotonic() - t0) / 0.6, 1.0)
            e = ease_out(k)
            self.intro_zoom, self.intro_yaw, self.intro_k = 0.72 + 0.28 * e, -1.2 * (1 - e), e
            self._draw()  # the very last frame (k = 1) is drawn in full quality
            if k < 1.0:
                self.after(10, lambda: self._intro_step(iid, t0))

        def _draw(self):
            self.pending = False
            self.delete("all")
            w, h = max(self.winfo_width(), 2), max(self.winfo_height(), 2)
            if self.scene is None:
                self.create_text(w / 2, h / 2 + (30 if self.busy else 0), text=self.msg, fill=MUTED, width=w - 40,
                                 justify="center", tags="msg", font=("Segoe UI", 11))
                return
            rest = 1 if w * h <= 300_000 else 2  # big windows are drawn at half size and enlarged
            quick = self.dragging or self.intro_k < 1.0
            sc = rest + 1 if quick else rest  # while dragging / zooming in: coarser + fewer points = instant
            try:
                arr = render_image(self.scene, self.yaw + self.intro_yaw, self.pitch, self.zoom * self.intro_zoom,
                                   max(w // sc, 2), max(h // sc, 2), stride=2 if quick else 1, fill=not quick)
                if self.intro_k < 1.0:  # fade up out of the backdrop
                    arr = (arr * self.intro_k + backdrop(arr.shape[1], arr.shape[0]) * (1 - self.intro_k)).astype(np.uint8)
                img = tk.PhotoImage(data=base64.b64encode(png_bytes(arr)))
                if sc > 1:
                    img = img.zoom(sc, sc)
            except Exception as e:  # noqa: BLE001
                log_error()
                self.create_text(w / 2, h / 2, fill=AMBER, width=w - 40, justify="center",
                                 text=f"Preview error: {e}\n(details in {ERRLOG})")
                return
            self.photo = img  # keep a reference, otherwise tkinter throws the picture away
            self.create_image(0, 0, image=img, anchor="nw")

        def _schedule(self):
            if not self.pending and self.scene is not None:
                self.pending = True
                self.after(10, self._draw)

        def _down(self, e):
            self.intro_id += 1  # grabbing the model ends the intro animation at once
            self.intro_zoom, self.intro_yaw, self.intro_k = 1.0, 0.0, 1.0
            self.drag = (e.x, e.y)

        def _move(self, e):
            if not self.drag or self.scene is None:
                return
            self.dragging = True
            self.yaw += (e.x - self.drag[0]) * 0.01
            self.pitch = max(-1.4, min(1.4, self.pitch + (e.y - self.drag[1]) * 0.01))
            self.drag = (e.x, e.y)
            self._schedule()

        def _up(self, _e):
            self.drag = None
            if self.dragging:
                self.dragging = False
                self._draw()  # full quality again

        def _wheel(self, e):
            self.zoom = max(0.4, min(3.0, self.zoom * (1.1 if e.delta > 0 else 0.9)))
            self._schedule()

        def _configure(self, _e):
            if self.cfg_job:
                self.after_cancel(self.cfg_job)
            self.cfg_job = self.after(80, self._draw)

    class Welcome(tk.Toplevel):
        def __init__(self, master):
            super().__init__(master)
            self.title("Welcome to MeshSwapper")
            self.configure(bg=BG)
            self.resizable(False, False)
            self.transient(master)
            tk.Label(self, text="Welcome to MeshSwapper", bg=BG, fg=FG,
                     font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=20, pady=(18, 6))
            msg = ("You need to have Bloxstrap installed for MeshSwapper to work.\n\n"
                   "MeshSwapper copies the meshes of your sets into Bloxstrap's Modifications folder. "
                   "Bloxstrap then applies them every time you launch Roblox.\n\n"
                   "You can close this message whether or not you have Bloxstrap yet. "
                   "It is only shown once.")
            tk.Label(self, text=msg, bg=BG, fg=FG, justify="left", wraplength=420).pack(padx=20, anchor="w")
            cr = tk.Frame(self, bg=BG)
            cr.pack(fill="x", padx=20, pady=(14, 0))
            tk.Label(cr, text="Created with the help of Claude by Anthropic  ·", bg=BG, fg=MUTED).pack(side="left")
            Link(cr, "Discord", DISCORD_URL).pack(side="left", padx=(6, 0))
            row = tk.Frame(self, bg=BG)
            row.pack(fill="x", padx=20, pady=18)
            Btn(row, text="Open bloxstraplabs.com", command=lambda: webbrowser.open(BLOXSTRAP_URL)).pack(side="left")
            Btn(row, text="Got it", style="Accent.TButton", command=self.destroy).pack(side="right")
            self.update_idletasks()
            x = master.winfo_rootx() + (master.winfo_width() - self.winfo_width()) // 2
            y = master.winfo_rooty() + (master.winfo_height() - self.winfo_height()) // 3
            self.geometry(f"+{max(x, 0)}+{max(y, 0)}")
            fade_in(self)
            self.grab_set()

    class NameDialog(tk.Toplevel):
        def __init__(self, master, current, title="Rename file",
                     text="New file name. It must match the Roblox mesh file exactly\n"
                          "(e.g. leftarm.mesh). Pick a suggestion or type it."):
            super().__init__(master)
            self.title(title)
            self.configure(bg=BG)
            self.resizable(False, False)
            self.transient(master)
            self.result = None
            tk.Label(self, text=text, bg=BG, fg=FG, justify="left").pack(anchor="w", padx=16, pady=(14, 6))
            self.var = tk.StringVar(value=current)
            self.cb = ttk.Combobox(self, textvariable=self.var, values=SUGGESTIONS, width=40)
            self.cb.pack(padx=16)
            tk.Label(self, text="Suggestions only - names can differ between Roblox versions.",
                     bg=BG, fg=MUTED).pack(anchor="w", padx=16, pady=(4, 0))
            row = tk.Frame(self, bg=BG)
            row.pack(fill="x", padx=16, pady=14)
            Btn(row, text="Cancel", command=self.destroy).pack(side="right", padx=(6, 0))
            Btn(row, text="OK", style="Accent.TButton", command=self.ok).pack(side="right")
            self.cb.focus_set()
            self.bind("<Return>", lambda _e: self.ok())
            fade_in(self)
            self.grab_set()

        def ok(self):
            t = clean_filename(self.var.get())
            if t:
                self.result = t
                self.destroy()

    NORM = 4.0  # studs from the centre to the edge of the creator view at zoom 1

    class EditorView(Preview):
        """Preview with a floor grid, axes, a size guide and draggable handles on top."""

        def __init__(self, master, editor):
            super().__init__(master)
            self.ed = editor
            self.moving = None
            self.press = None
            self.start_pos = None
            self.msg = "Add a shape on the left to start"
            self.zoom = 1.7  # shapes are only a few studs big
            for key, d in (("<Left>", (-1, 0, 0)), ("<Right>", (1, 0, 0)), ("<Up>", (0, 1, 0)),
                           ("<Down>", (0, -1, 0)), ("<Shift-Up>", (0, 0, -1)), ("<Shift-Down>", (0, 0, 1))):
                self.bind(key, lambda _e, d=d: self.ed.nudge(d))
            self.bind("<Delete>", lambda _e: self.ed.delete_selected())

        # ---- projection (same camera as render_image)
        def _cam(self):
            w, h = max(self.winfo_width(), 2), max(self.winfo_height(), 2)
            cy, sy = math.cos(self.yaw), math.sin(self.yaw)
            cp, sp = math.cos(self.pitch), math.sin(self.pitch)
            R = np.array([[cy, 0.0, sy], [sy * sp, cp, -cy * sp], [-sy * cp, sp, cy * cp]])
            return R, min(w, h) * 0.42 * self.zoom, w, h

        @staticmethod
        def _pt(cam, p):
            R, s, w, h = cam
            c = R @ (np.asarray(p, float) / NORM)
            return float(c[0] * s + w / 2), float(h / 2 - c[1] * s)

        def _box(self, cam, lo, hi, col, width, dash):
            c = [(x, y, z) for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]
            kw = {"dash": dash} if dash else {}
            for a, b in ((0, 1), (2, 3), (4, 5), (6, 7), (0, 2), (1, 3), (4, 6), (5, 7), (0, 4), (1, 5), (2, 6), (3, 7)):
                pa, pb = self._pt(cam, c[a]), self._pt(cam, c[b])
                self.create_line(pa[0], pa[1], pb[0], pb[1], fill=col, width=width, tags="ov", **kw)

        def _draw(self):
            super()._draw()
            try:
                self._overlay()
            except Exception:  # noqa: BLE001 - the overlay must never break the view
                log_error()

        def _overlay(self):
            cam = self._cam()
            P = lambda p: self._pt(cam, p)  # noqa: E731
            for i in range(-4, 5):
                col = "#3b2f78" if i == 0 else "#241c4a"
                a, b = P((i, 0, -4)), P((i, 0, 4))
                self.create_line(a[0], a[1], b[0], b[1], fill=col, tags="ov")
                a, b = P((-4, 0, i)), P((4, 0, i))
                self.create_line(a[0], a[1], b[0], b[1], fill=col, tags="ov")
            o = P((0, 0, 0))
            for vec, col, name in (((2.5, 0, 0), "#f87171", "X"), ((0, 2.5, 0), "#4ade80", "Y"), ((0, 0, 2.5), "#60a5fa", "Z")):
                e = P(vec)
                self.create_line(o[0], o[1], e[0], e[1], fill=col, width=2, tags="ov")
                self.create_text(e[0] + 8, e[1] - 8, text=name, fill=col, tags="ov", font=("Segoe UI", 8, "bold"))
            fr = P((0, 0, -2.6))
            self.create_line(o[0], o[1], fr[0], fr[1], fill="#f0abfc", width=2, dash=(5, 4), arrow="last", tags="ov")
            self.create_text(fr[0] + 6, fr[1] - 10, text="FRONT", fill="#f0abfc", tags="ov", font=("Segoe UI", 8, "bold"))
            g = self.ed.guide_size()
            if g:
                self._box(cam, (-g[0] / 2, -g[1] / 2, -g[2] / 2), (g[0] / 2, g[1] / 2, g[2] / 2), "#a78bfa", 1, (4, 4))
            bb = self.ed.selected_bbox()
            if bb:
                self._box(cam, bb[0], bb[1], GLOW, 2, None)
            for i, c in self.ed.handles():
                x, y = P(c)
                sel = i == self.ed.sel
                r = 8 if sel else 5
                self.create_oval(x - r, y - r, x + r, y + r, fill=ACCENT if sel else BG,
                                 outline="#ffffff" if sel else GLOW, width=2, tags="ov")

        # ---- mouse: drag a dot = move that shape, drag empty space = rotate
        def _hit(self, x, y):
            cam = self._cam()
            best, bd = None, 18.0
            for i, c in self.ed.handles():
                px, py = self._pt(cam, c)
                d = math.hypot(px - x, py - y)
                if i == self.ed.sel:
                    d -= 6  # the selected one wins when dots overlap
                if d < bd:
                    best, bd = i, d
            return best

        def _down(self, e):
            self.focus_set()
            hit = self._hit(e.x, e.y)
            if hit is None:
                self.moving = None
                return super()._down(e)
            self.ed.select(hit)
            self.ed.push_undo()
            self.moving = hit
            self.press = (e.x, e.y)
            self.start_pos = list(self.ed.objs[hit]["pos"])

        def _move(self, e):
            if self.moving is None:
                return super()._move(e)
            R, s, _w, _h = self._cam()
            d = NORM * (R.T @ np.array([(e.x - self.press[0]) / s, -(e.y - self.press[1]) / s, 0.0]))
            pos = [self.start_pos[k] + float(d[k]) for k in range(3)]
            if self.ed.snap.get():
                pos = [round(v / 0.25) * 0.25 for v in pos]
            self.dragging = True
            self.ed.set_pos(pos)

        def _up(self, e):
            if self.moving is None:
                return super()._up(e)
            self.moving = None
            self.dragging = False
            self.ed.refresh()

    class MeshEditor(tk.Toplevel):
        """Build your own mesh from simple shapes and save it straight into a set."""
        PROPS = [("Position X", "pos", 0, -8, 8, 0.05), ("Position Y", "pos", 1, -8, 8, 0.05),
                 ("Position Z", "pos", 2, -8, 8, 0.05),
                 ("Rotate X", "rot", 0, -180, 180, 1), ("Rotate Y", "rot", 1, -180, 180, 1),
                 ("Rotate Z", "rot", 2, -180, 180, 1),
                 ("Size X", "scl", 0, 0.05, 8, 0.05), ("Size Y", "scl", 1, 0.05, 8, 0.05),
                 ("Size Z", "scl", 2, 0.05, 8, 0.05),
                 ("Taper", "taper", None, -0.95, 0.95, 0.01), ("Detail", "seg", None, 3, 48, 1)]

        def __init__(self, app):
            super().__init__(app)
            self.app = app
            self.title("MeshSwapper · Mesh creator")
            self.configure(bg=BG)
            self.geometry("1180x740")
            self.minsize(1000, 640)
            self.objs, self.undo, self.redo, self.bb = [], [], [], {}
            self.sel = None
            self.dirty = False
            self.counter = 0
            self._loading = False
            self._job = None
            self.snap = tk.BooleanVar(value=True)
            self.center = tk.BooleanVar(value=True)
            self.two = tk.BooleanVar(value=True)
            self.guide = tk.StringVar(value="Arm / leg  1 x 2 x 1")
            self.v_name = tk.StringVar()
            self.v_mirror = tk.BooleanVar(value=False)
            self.v_status = tk.StringVar(value="Add a shape to start.")
            self._build()
            self.protocol("WM_DELETE_WINDOW", self._close)
            self.bind("<Control-z>", lambda _e: self.do_undo())
            self.bind("<Control-y>", lambda _e: self.do_redo())
            self.bind("<Control-d>", lambda _e: self.duplicate_selected())
            self.v_name.trace_add("write", self._on_name)
            fade_in(self, 260)
            self.refresh()

        # ---- layout
        def _build(self):
            Shimmer(self).pack(fill="x")
            bar = tk.Frame(self, bg=PANEL)
            bar.pack(fill="x", padx=10, pady=(10, 0))
            tk.Label(bar, text="Mesh creator", bg=PANEL, fg=FG, font=("Segoe UI", 13, "bold")).pack(side="left", padx=(12, 14), pady=8)
            for text, cmd in (("New", self.new_project), ("Open…", self.open_project), ("Save project…", self.save_project),
                              ("↶ Undo", self.do_undo), ("↷ Redo", self.do_redo)):
                Btn(bar, text=text, command=cmd).pack(side="left", padx=3, pady=8)
            Btn(bar, text="Save to set…", style="Accent.TButton", command=self.save_to_set).pack(side="right", padx=(3, 10), pady=8)
            Btn(bar, text="Export .mesh…", command=self.export_mesh).pack(side="right", padx=3, pady=8)

            body = tk.Frame(self, bg=BG)
            body.pack(fill="both", expand=True, padx=10, pady=10)

            left = tk.Frame(body, bg=BG)
            left.pack(side="left", fill="y")
            tk.Label(left, text="Add shape", bg=BG, fg=FG, font=("Segoe UI", 11, "bold")).pack(anchor="w")
            grid = tk.Frame(left, bg=BG)
            grid.pack(fill="x", pady=4)
            for i, kind in enumerate(SHAPES):
                Btn(grid, text=kind, command=lambda k=kind: self.add_shape(k)).grid(row=i // 2, column=i % 2, sticky="ew", padx=2, pady=2)
            grid.columnconfigure(0, weight=1)
            grid.columnconfigure(1, weight=1)
            Btn(left, text="Import 3D file…", command=self.import_mesh).pack(fill="x", pady=(2, 10))
            tk.Label(left, text="Shapes in this mesh", bg=BG, fg=FG, font=("Segoe UI", 11, "bold")).pack(anchor="w")
            self.lb = tk.Listbox(left, width=24, bg=PANEL, fg=FG, selectbackground=ACCENT, selectforeground="#ffffff",
                                 relief="flat", activestyle="none", exportselection=False, bd=0,
                                 highlightthickness=0, font=("Segoe UI", 10))
            self.lb.pack(fill="both", expand=True, pady=6)
            hover_list(self.lb)
            self.lb.bind("<<ListboxSelect>>", lambda _e: self._on_list())
            row = tk.Frame(left, bg=BG)
            row.pack(fill="x")
            Btn(row, text="Duplicate", command=self.duplicate_selected).pack(side="left", expand=True, fill="x", padx=(0, 2))
            Btn(row, text="Delete", command=self.delete_selected).pack(side="left", expand=True, fill="x", padx=(2, 0))

            right = tk.Frame(body, bg=BG)
            right.pack(side="right", fill="y")
            tk.Label(right, text="Selected shape", bg=BG, fg=FG, font=("Segoe UI", 11, "bold")).pack(anchor="w")
            nrow = tk.Frame(right, bg=BG)
            nrow.pack(fill="x", pady=(4, 6))
            tk.Label(nrow, text="Name", bg=BG, fg=MUTED, width=10, anchor="w").pack(side="left")
            tk.Entry(nrow, textvariable=self.v_name, bg=BTN, fg=FG, insertbackground=FG, relief="flat",
                     highlightthickness=0, bd=4).pack(side="left", fill="x", expand=True)
            self.scales = {}
            for label, key, idx, lo, hi, res in self.PROPS:
                r = tk.Frame(right, bg=BG)
                r.pack(fill="x", pady=1)
                tk.Label(r, text=label, bg=BG, fg=MUTED, width=10, anchor="w").pack(side="left")
                sc = tk.Scale(r, from_=lo, to=hi, resolution=res, orient="horizontal", length=200, showvalue=True,
                              bg=BG, fg=FG, troughcolor=BTN, highlightthickness=0, bd=0, sliderrelief="flat",
                              activebackground=ACCENT, command=lambda v, k=key, i=idx: self._on_scale(k, i, v))
                sc.pack(side="left", fill="x", expand=True)
                sc.bind("<ButtonPress-1>", lambda _e: self.push_undo(), add="+")
                self.scales[(key, idx)] = sc
            tk.Checkbutton(right, text="Mirror copy on the other side (X)", variable=self.v_mirror, command=self._on_mirror,
                           bg=BG, fg=FG, selectcolor=BTN, activebackground=BG, activeforeground=FG,
                           highlightthickness=0, bd=0).pack(anchor="w", pady=(8, 0))
            tk.Label(right, text="Taper narrows the top (or widens it with minus).\nDetail = how round the round shapes are.",
                     bg=BG, fg=MUTED, justify="left").pack(anchor="w", pady=(6, 0))
            tk.Label(right, text="Fix position / direction", bg=BG, fg=FG, font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(10, 2))
            tools = tk.Frame(right, bg=BG)
            tools.pack(fill="x")
            for i, (text, cmd) in enumerate((
                    ("Face other way", lambda: self.turn(1, 180)), ("Stand up (Z→Y)", lambda: self.turn(0, -90)),
                    ("Turn X 90°", lambda: self.turn(0, 90)), ("Turn Y 90°", lambda: self.turn(1, 90)),
                    ("Turn Z 90°", lambda: self.turn(2, 90)), ("Flip left/right", self.flip_lr),
                    ("Fit to guide", self.fit_guide), ("Centre", self.centre_selected))):
                Btn(tools, text=text, command=cmd).grid(row=i // 2, column=i % 2, sticky="ew", padx=2, pady=2)
            tools.columnconfigure(0, weight=1)
            tools.columnconfigure(1, weight=1)

            self.view = EditorView(body, self)
            self.view.pack(side="left", fill="both", expand=True, padx=10)

            bottom = tk.Frame(self, bg=BG)
            bottom.pack(fill="x", padx=10, pady=(0, 4))
            for text, var in (("Snap to 0.25", self.snap), ("Centre mesh on export", self.center),
                              ("Visible from both sides", self.two)):
                tk.Checkbutton(bottom, text=text, variable=var, bg=BG, fg=FG, selectcolor=BTN, activebackground=BG,
                               activeforeground=FG, highlightthickness=0, bd=0).pack(side="left", padx=(0, 12))
            tk.Label(bottom, text="Size guide", bg=BG, fg=MUTED).pack(side="left")
            cb = ttk.Combobox(bottom, textvariable=self.guide, values=list(GUIDES), state="readonly", width=22)
            cb.pack(side="left", padx=6)
            cb.bind("<<ComboboxSelected>>", lambda _e: self.view._schedule())
            tk.Label(bottom, textvariable=self.v_status, bg=BG, fg=FG).pack(side="right")
            tk.Label(self, text="Drag a dot to move a shape · drag empty space to rotate · scroll to zoom · arrow keys nudge · "
                                "Ctrl+Z undo · units are studs (a Roblox arm is 1 × 2 × 1)",
                     bg=BG, fg=MUTED).pack(fill="x", padx=12, pady=(0, 8), anchor="w")

        # ---- data helpers used by the view
        def guide_size(self):
            return GUIDES.get(self.guide.get())

        def selected_bbox(self):
            return self.bb.get(self.sel) if self.sel is not None else None

        def handles(self):
            return [(i, (lo + hi) / 2) for i, (lo, hi) in self.bb.items()]

        # ---- undo / redo
        def _snap(self):
            return ([dict(o, pos=list(o["pos"]), rot=list(o["rot"]), scl=list(o["scl"])) for o in self.objs], self.sel)

        def push_undo(self):
            self.undo.append(self._snap())
            del self.undo[:-60]
            self.redo.clear()
            self.dirty = True

        def _restore(self, state):
            self.objs = [dict(o, pos=list(o["pos"]), rot=list(o["rot"]), scl=list(o["scl"])) for o in state[0]]
            self.sel = state[1] if state[1] is not None and state[1] < len(self.objs) else (0 if self.objs else None)
            self._fill_list()
            self._load()
            self.refresh()

        def do_undo(self):
            if self.undo:
                self.redo.append(self._snap())
                self._restore(self.undo.pop())

        def do_redo(self):
            if self.redo:
                self.undo.append(self._snap())
                self._restore(self.redo.pop())

        # ---- selection and the property panel
        def _fill_list(self):
            self.lb.delete(0, "end")
            for o in self.objs:
                self.lb.insert("end", ("⇋ " if o.get("mirror") else "   ") + o["name"])
            if self.sel is not None:
                self.lb.selection_set(self.sel)

        def _on_list(self):
            s = self.lb.curselection()
            if s:
                self.select(s[0], from_list=True)

        def select(self, i, from_list=False):
            self.sel = i
            if not from_list:
                self.lb.selection_clear(0, "end")
                if i is not None:
                    self.lb.selection_set(i)
            self._load()
            self.view._schedule()

        def _load(self):
            self._loading = True
            try:
                o = self.objs[self.sel] if self.sel is not None else None
                self.v_name.set(o["name"] if o else "")
                self.v_mirror.set(bool(o and o.get("mirror")))
                for (key, idx), sc in self.scales.items():
                    if o:
                        sc.set(o[key] if idx is None else o[key][idx])
            finally:
                self._loading = False

        def _on_scale(self, key, idx, value):
            if self._loading or self.sel is None:
                return
            o = self.objs[self.sel]
            val = float(value)
            if idx is None:
                o[key] = int(val) if key == "seg" else val
            else:
                o[key][idx] = val
            self.dirty = True
            self.schedule()

        def _on_name(self, *_a):
            if self._loading or self.sel is None:
                return
            self.objs[self.sel]["name"] = self.v_name.get() or "Shape"
            self._fill_list()
            self.dirty = True

        def _on_mirror(self):
            if self.sel is None:
                return
            self.push_undo()
            self.objs[self.sel]["mirror"] = bool(self.v_mirror.get())
            self._fill_list()
            self.refresh()

        def set_pos(self, pos):
            if self.sel is None:
                return
            self.objs[self.sel]["pos"] = list(pos)
            self._loading = True
            try:
                for k in range(3):
                    self.scales[("pos", k)].set(pos[k])
            finally:
                self._loading = False
            self.dirty = True
            self.schedule()

        def nudge(self, d):
            if self.sel is None:
                return
            self.push_undo()
            o = self.objs[self.sel]
            self.set_pos([o["pos"][k] + d[k] * 0.25 for k in range(3)])

        # ---- orientation helpers (mostly for imported models)
        def _edit(self, fn):
            if self.sel is None:
                return
            self.push_undo()
            fn(self.objs[self.sel])
            self._load()
            self.refresh()

        def turn(self, idx, deg):
            def go(o):
                o["rot"][idx] = ((o["rot"][idx] + deg + 180) % 360) - 180
            self._edit(go)

        def flip_lr(self):
            self._edit(lambda o: o.__setitem__("flipx", not o.get("flipx")))

        def centre_selected(self):
            def go(o):
                V, _f = object_geometry(o)
                c = (V.min(0) + V.max(0)) / 2
                o["pos"] = [o["pos"][k] - float(c[k]) for k in range(3)]
            self._edit(go)

        def fit_guide(self):
            g = self.guide_size()
            if not g:
                messagebox.showinfo(APP, "Pick a size guide at the bottom first (for example 'Arm / leg').", parent=self)
                return

            def go(o):
                V, _f = object_geometry(o)
                size = V.max(0) - V.min(0)
                f = min(g[k] / size[k] for k in range(3) if size[k] > 1e-9)
                o["scl"] = [v * f for v in o["scl"]]
                o["pos"] = [v * f for v in o["pos"]]
            self._edit(go)
            self.centre_selected()

        # ---- shapes
        def _add(self, o):
            self.push_undo()
            self.objs.append(o)
            self.sel = len(self.objs) - 1
            self._fill_list()
            self._load()
            self.refresh()

        def add_shape(self, kind):
            self.counter += 1
            self._add(new_object(kind, self.counter))

        def import_mesh(self, path=None):
            f = path or filedialog.askopenfilename(
                parent=self, title="Select a 3D or Roblox file to convert (.obj .fbx .rbxm .mesh .glb .dae .stl .ply ...)",
                filetypes=model_filetypes())
            if not f:
                return
            self.v_status.set(f"Converting {Path(f).name} …")
            self.update_idletasks()
            try:
                V, F, UV = load_any_mesh(f)
            except Exception as e:  # noqa: BLE001
                if not isinstance(e, MeshError):
                    log_error()
                messagebox.showerror(APP, f"Could not read that file:\n{e}", parent=self)
                return
            o = new_object("Imported")
            o["name"], o["mesh"], o["uv"], o["path"] = Path(f).stem, (V, F), UV, str(f)
            big = float((V.max(0) - V.min(0)).max())
            note = f"Imported {Path(f).name}"
            if big > 8 or big < 0.5:  # a model in metres / centimetres: bring it to a size that fits Roblox
                k = 2.0 / big
                o["scl"] = [k, k, k]
                note += f" (the file's units did not fit Roblox, it was scaled by {k:.4g})"
            self._add(o)
            self.v_status.set(note + " · use 'Fix position / direction' on the right if it faces the wrong way"
                              + "".join(" · " + t for t in LOAD_NOTES))

        def duplicate_selected(self):
            if self.sel is None:
                return
            o = self.objs[self.sel]
            c = dict(o, pos=list(o["pos"]), rot=list(o["rot"]), scl=list(o["scl"]))
            c["name"] = o["name"] + " copy"
            c["pos"][0] += 0.5
            self._add(c)

        def delete_selected(self):
            if self.sel is None:
                return
            self.push_undo()
            del self.objs[self.sel]
            self.sel = min(self.sel, len(self.objs) - 1) if self.objs else None
            self._fill_list()
            self._load()
            self.refresh()

        # ---- preview
        def schedule(self):
            if self._job is None:
                self._job = self.after(25, self.refresh)

        def refresh(self):
            self._job = None
            self.bb = {}
            pieces = []
            tris = 0
            for i, o in enumerate(self.objs):
                try:
                    V, F = object_geometry(o)
                except Exception:  # noqa: BLE001
                    log_error()
                    continue
                if not len(F):
                    continue
                N = None if o.get("mesh") is not None else compute_normals(V, F)  # imports: shade two-sided
                self.bb[i] = (V.min(0), V.max(0))
                tris += len(F)
                pieces.append(({"V": V, "N": N, "F": F}, (0.0, 0.0, 0.0)))
            if not pieces:
                self.view.clear("Add a shape on the left to start")
                self.v_status.set("Add a shape to start.")
                return
            try:
                self.view.set_scene(sample_scene(pieces, total=90_000, norm=NORM))
            except MeshError as e:
                self.view.clear(str(e))
            self.v_status.set(f"{len(self.objs)} shape(s) · {tris} triangles")

        # ---- files
        def _projects_dir(self):
            d = DATA / "Projects"
            d.mkdir(parents=True, exist_ok=True)
            return d

        def _ask_discard(self):
            return not (self.dirty and self.objs) or messagebox.askyesno(
                APP, "Throw away the shapes you have now?", parent=self)

        def new_project(self):
            if self._ask_discard():
                self.push_undo()
                self.objs, self.sel, self.counter = [], None, 0
                self.dirty = False
                self._fill_list()
                self._load()
                self.refresh()

        def save_project(self):
            if not self.objs:
                messagebox.showinfo(APP, "Add a shape first.", parent=self)
                return
            f = filedialog.asksaveasfilename(parent=self, title="Save project", defaultextension=".swapper",
                                             initialdir=str(self._projects_dir()), initialfile="my_mesh.swapper",
                                             filetypes=[("MeshSwapper project", "*.swapper")])
            if f:
                try:
                    Path(f).write_text(project_to_json(self.objs), encoding="utf-8")
                    self.v_status.set(f"Project saved: {Path(f).name}")
                except OSError as e:
                    messagebox.showerror(APP, str(e), parent=self)

        def open_project(self):
            if not self._ask_discard():
                return
            f = filedialog.askopenfilename(parent=self, title="Open project", initialdir=str(self._projects_dir()),
                                           filetypes=[("MeshSwapper project", "*.swapper"), ("All files", "*.*")])
            if not f:
                return
            try:
                objs = project_from_json(Path(f).read_text(encoding="utf-8"))
            except Exception as e:  # noqa: BLE001
                messagebox.showerror(APP, f"Could not open that project:\n{e}", parent=self)
                return
            self.push_undo()
            self.objs, self.sel = objs, (0 if objs else None)
            self.counter = len(objs)
            self.dirty = False
            self._fill_list()
            self._load()
            self.refresh()

        def _bytes(self):
            if not self.objs:
                messagebox.showinfo(APP, "Add a shape first.", parent=self)
                return None
            V, N, F, _p, UV = build_model(self.objs)
            return mesh_bytes(V, N, F, center=self.center.get(), two_sided=self.two.get(), uv=UV)

        def export_mesh(self):
            data = self._bytes()
            if data is None:
                return
            f = filedialog.asksaveasfilename(parent=self, title="Export mesh", defaultextension=".mesh",
                                             initialfile="mymesh.mesh", filetypes=[("Roblox mesh", "*.mesh")])
            if f:
                try:
                    Path(f).write_bytes(data)
                    self.v_status.set(f"Exported {Path(f).name}")
                except OSError as e:
                    messagebox.showerror(APP, str(e), parent=self)

        def save_to_set(self):
            data = self._bytes()
            if data is None:
                return
            app = self.app
            n = app.current_set()
            if not n:
                raw = simpledialog.askstring(APP, "Name of the new set (e.g. Enderman):", parent=self)
                if raw is None:
                    return
                n = safe_name(raw)
                if not n:
                    messagebox.showwarning(APP, "Please enter a valid name.", parent=self)
                    return
            first = clean_filename(self.objs[0]["name"].lower().replace(" ", "")) if self.objs else "torso.mesh"
            dlg = NameDialog(self, "torso.mesh" if len(self.objs) > 1 else first, title="Save into set",
                             text=f"File name in the set '{n}'. It must match the Roblox part exactly\n"
                                  "(e.g. leftarm.mesh, torso.mesh). Pick a suggestion or type it.")
            self.wait_window(dlg)
            if not dlg.result:
                return
            target = SETS / n / dlg.result
            if target.exists() and not messagebox.askyesno(APP, f"{dlg.result} already exists in {n}. Replace it?", parent=self):
                return
            try:
                (SETS / n).mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
            except OSError as e:
                messagebox.showerror(APP, str(e), parent=self)
                return
            self.dirty = False
            app.refresh_sets(keep=n)
            app.say(f"Created {dlg.result} in {n}")
            self.v_status.set(f"Saved {dlg.result} into {n}")

        def _close(self):
            if self.dirty and self.objs and not messagebox.askyesno(
                    APP, "Close the creator? Shapes you did not save will be lost.", parent=self):
                return
            if self._job:
                try:
                    self.after_cancel(self._job)
                except tk.TclError:
                    pass
            self.destroy()

    class App(tk.Tk):
        def __init__(self):
            super().__init__()
            self.withdraw()  # stays hidden behind the splash screen until everything is ready
            self._t_boot = time.monotonic()
            self._ver_done = self._revealed = False
            self._splash = None
            try:
                self._splash = Splash(self)
            except Exception:  # noqa: BLE001 - no splash is better than no app
                log_error()
            self.title("MeshSwapper")
            try:
                self._icon = tk.PhotoImage(data=LOGO_B64)
                self.iconphoto(True, self._icon)  # also used by all dialogs
            except tk.TclError:
                pass
            self.configure(bg=BG)
            self.geometry("980x640")
            self.minsize(880, 580)
            SETS.mkdir(parents=True, exist_ok=True)
            self.cfg = load_cfg()
            self.set_names = []
            self.file_paths = []
            self.found = False
            self.cache = {}
            self.q = queue.Queue()  # results from background threads
            self._rbx_checking = self._rbx_busy = self.rbx_running = False
            self._rbx_grace = 0.0
            self.assemble_origin = True
            self.fix_sizes = True
            self.req = 0
            self.local_version = ""
            self._boot(0.12, "Preparing…")
            self._style()
            self._build()
            self._boot(0.45, "Building the interface…")
            self.refresh_bloxstrap()
            self._boot(0.62, "Looking for Bloxstrap…")
            self.refresh_sets()
            self._boot(0.78, "Opening your sets…")
            self.refresh_roblox()
            self._boot(0.88, "Checking your Roblox version…")
            self.protocol("WM_DELETE_WINDOW", self._close)
            self.after(80, self._poll)
            self.after(600, self._check_rbx)
            self.after(40, self._boot_wait)
            self.after(7000, self._reveal)  # safety net: the window always shows up in the end

        # ---- start-up screen
        def _boot(self, frac, text):
            sp = self._splash
            if sp is not None:
                try:
                    sp.set(frac, text)
                    self.update()  # lets the splash animation keep running while we load
                except tk.TclError:
                    pass

        def _boot_wait(self):
            """Waits (briefly) for the Roblox version check, then fades the splash out and shows the window."""
            if self._revealed:
                return
            waited = time.monotonic() - self._t_boot
            if self._splash is None:
                return self._reveal()
            self._splash.set(min(0.96, 0.88 + 0.06 * waited), "Roblox version checked ✔" if self._ver_done else None)
            if waited >= 1.5 and (self._ver_done or waited >= 3.2):
                try:
                    return self._splash.finish(self._reveal)
                except Exception:  # noqa: BLE001
                    log_error()
                    return self._reveal()
            self.after(40, self._boot_wait)

        def _reveal(self):
            if self._revealed:
                return
            self._revealed = True
            sp, self._splash = self._splash, None
            if sp is not None:
                sp.kill()
            slide_in(self, 980, 640)
            self.after(520, self.maybe_welcome)

        # ---- layout
        def _style(self):
            st = ttk.Style(self)
            st.theme_use("clam")
            st.configure("TCombobox", fieldbackground=BTN, background=BTN, foreground=FG, arrowcolor=FG,
                         bordercolor=BTN, lightcolor=BTN, darkcolor=BTN, padding=4)
            st.map("TCombobox", fieldbackground=[("readonly", BTN)], foreground=[("readonly", FG)])
            self.option_add("*TCombobox*Listbox.background", PANEL)
            self.option_add("*TCombobox*Listbox.foreground", FG)
            self.option_add("*TCombobox*Listbox.selectBackground", ACCENT)

        def _build(self):
            Shimmer(self).pack(fill="x")
            head = tk.Frame(self, bg=BG)
            head.pack(fill="x", padx=14, pady=(10, 0))
            try:
                self._logo_small = tk.PhotoImage(data=LOGO_SMALL_B64)
                tk.Label(head, image=self._logo_small, bg=BG).pack(side="left", padx=(0, 10))
            except tk.TclError:
                pass
            tk.Label(head, text="MeshSwapper", bg=BG, fg=FG, font=("Segoe UI", 19, "bold")).pack(side="left")
            sub = tk.Label(head, text="", bg=BG, fg=MUTED, font=("Segoe UI", 10))
            sub.pack(side="left", padx=(12, 0), pady=(9, 0))
            Stars(head).pack(side="left", fill="x", expand=True, padx=(14, 0))
            tagline = "swap your Roblox meshes"

            def type_in(n=1):  # tagline types itself in
                try:
                    sub.config(text=tagline[:n])
                except tk.TclError:
                    return
                if n < len(tagline):
                    sub.after(35, lambda: type_in(n + 1))
            self.after(350, type_in)

            top = tk.Frame(self, bg=PANEL)
            top.pack(fill="x", padx=10, pady=10)
            self.v_bs = tk.StringVar()
            self.l_bs = tk.Label(top, textvariable=self.v_bs, bg=PANEL, fg=MUTED, anchor="w")
            self.l_bs.grid(row=0, column=0, sticky="w", padx=10, pady=(8, 0))
            tk.Label(top, text=f"Your sets folder: {SETS}", bg=PANEL, fg=MUTED, anchor="w").grid(
                row=1, column=0, sticky="w", padx=10, pady=(0, 2))
            self.v_rb = tk.StringVar()
            self.l_rb = tk.Label(top, textvariable=self.v_rb, bg=PANEL, fg=MUTED, anchor="w",
                                 justify="left", wraplength=560)
            self.l_rb.grid(row=2, column=0, sticky="w", padx=10, pady=(0, 8))
            top.columnconfigure(0, weight=1)
            btns = tk.Frame(top, bg=PANEL)
            btns.grid(row=0, column=1, rowspan=3, sticky="e", padx=10)
            Btn(btns, text="Check Roblox version", command=self.refresh_roblox).pack(side="left", padx=3)
            Btn(btns, text="Get Bloxstrap", command=lambda: webbrowser.open(BLOXSTRAP_URL)).pack(side="left", padx=3)
            Btn(btns, text="Open meshes folder", command=self.open_meshes).pack(side="left", padx=3)
            Btn(btns, text="Choose Bloxstrap folder…", command=self.pick_bloxstrap).pack(side="left", padx=3)

            play = tk.Frame(self, bg=PANEL)
            play.pack(fill="x", padx=10, pady=(0, 10))
            tk.Label(play, text="Roblox", bg=PANEL, fg=FG, font=("Segoe UI", 11, "bold")).grid(
                row=0, column=0, sticky="w", padx=10, pady=(8, 0))
            self.v_play = tk.StringVar(value="Checking…")
            tk.Label(play, textvariable=self.v_play, bg=PANEL, fg=GLOW, anchor="w", justify="left").grid(
                row=1, column=0, sticky="w", padx=10)
            tk.Label(play, text="Only closes and starts the official client again through Bloxstrap - nothing is injected "
                                "and the game itself is not touched.", bg=PANEL, fg=MUTED, anchor="w",
                     justify="left", wraplength=560).grid(row=2, column=0, sticky="w", padx=10, pady=(0, 8))
            play.columnconfigure(0, weight=1)
            pb = tk.Frame(play, bg=PANEL)
            pb.grid(row=0, column=1, rowspan=3, sticky="e", padx=10, pady=8)
            self.b_launch = Btn(pb, text="▶  Launch Roblox", style="Accent.TButton", command=self.launch_roblox_clicked)
            self.b_launch.pack(side="left", padx=4)
            self.b_refresh = Btn(pb, text="⟳  Refresh Roblox", command=self.refresh_game_clicked)
            self.b_refresh.pack(side="left", padx=4)
            self.b_refresh.enable(False)

            main = tk.Frame(self, bg=BG)
            main.pack(fill="both", expand=True, padx=10)

            left = tk.Frame(main, bg=BG)
            left.pack(side="left", fill="y")
            tk.Label(left, text="My sets", bg=BG, fg=FG, font=("Segoe UI", 11, "bold")).pack(anchor="w")
            self.lb = tk.Listbox(left, width=26, bg=PANEL, fg=FG, selectbackground=ACCENT, selectforeground="#ffffff", relief="flat",
                                 activestyle="none", exportselection=False, bd=0, highlightthickness=0,
                                 font=("Segoe UI", 10))
            hover_list(self.lb)
            self.lb.pack(fill="y", expand=True, pady=6)
            self.lb.bind("<<ListboxSelect>>", lambda _e: self.on_select_set())
            Btn(left, text="✦ Create mesh…", style="Accent.TButton", command=self.open_editor).pack(fill="x", pady=(0, 4))
            Btn(left, text="Convert Files → mesh…", command=lambda: self.open_editor(convert=True)).pack(fill="x", pady=(0, 8))
            Btn(left, text="New set…", command=self.new_set).pack(fill="x", pady=2)
            Btn(left, text="Import folder…", command=self.import_folder).pack(fill="x", pady=2)
            Btn(left, text="Delete set", command=self.delete_set).pack(fill="x", pady=2)
            Btn(left, text="Open sets folder", command=self.open_sets).pack(fill="x", pady=2)
            tk.Label(left, text="● applied   ○ not applied", bg=BG, fg=MUTED).pack(anchor="w", pady=(6, 0))

            right = tk.Frame(main, bg=BG)
            right.pack(side="left", fill="both", expand=True, padx=(12, 0))
            self.prev = Preview(right)
            self.prev.pack(fill="both", expand=True)
            self.v_info = tk.StringVar()
            tk.Label(right, textvariable=self.v_info, bg=BG, fg=MUTED, anchor="w").pack(fill="x", pady=(4, 4))

            frow = tk.Frame(right, bg=BG)
            frow.pack(fill="x")
            self.flb = tk.Listbox(frow, height=6, bg=PANEL, fg=FG, selectbackground=ACCENT, selectforeground="#ffffff", relief="flat",
                                  activestyle="none", exportselection=False, selectmode="extended",
                                  bd=0, highlightthickness=0, font=("Segoe UI", 10))
            hover_list(self.flb)
            self.flb.pack(side="left", fill="x", expand=True)
            self.flb.bind("<<ListboxSelect>>", lambda _e: self.update_preview())
            fbtn = tk.Frame(frow, bg=BG)
            fbtn.pack(side="left", padx=(8, 0))
            Btn(fbtn, text="Add meshes…", command=self.add_meshes).pack(fill="x", pady=1)
            Btn(fbtn, text="Rename…", command=self.rename_file).pack(fill="x", pady=1)
            Btn(fbtn, text="Remove file", command=self.remove_files).pack(fill="x", pady=1)
            Btn(fbtn, text="Show whole set", command=self.show_whole).pack(fill="x", pady=1)
            tk.Label(right, text="Select files to preview only those. Nothing selected = whole set, assembled like the Roblox dummy.",
                     bg=BG, fg=MUTED, anchor="w").pack(fill="x", pady=(2, 0))

            arow = tk.Frame(right, bg=BG)
            arow.pack(fill="x", pady=8)
            Btn(arow, text="Apply set", style="Accent.TButton", command=self.apply).pack(side="left")
            Btn(arow, text="Reset set", command=self.reset).pack(side="left", padx=6)
            Btn(arow, text="Reset all", command=self.reset_everything).pack(side="left")
            Btn(arow, text="↻ Auto-rotate", toggle=True, command=self.prev.set_spin).pack(side="right")
            Btn(arow, text="Place by origin", toggle=True, on=True, command=self.set_assemble).pack(side="right", padx=6)
            Btn(arow, text="Fix odd sizes", toggle=True, on=True, command=self.set_fix_sizes).pack(side="right")

            bottom = tk.Frame(self, bg=BG)
            bottom.pack(fill="x", padx=10, pady=(0, 8))
            tk.Label(bottom, text="Applying a set replaces the previously applied one. "
                                  "Launch Roblox through Bloxstrap to see it.",
                     bg=BG, fg=MUTED).pack(side="left")
            self.v_msg = tk.StringVar()
            self.l_msg = tk.Label(bottom, textvariable=self.v_msg, bg=BG, fg=FG)
            self.l_msg.pack(side="right")

            credit = tk.Frame(self, bg=BG)
            credit.pack(fill="x", padx=10, pady=(0, 8))
            tk.Label(credit, text="App created with the help of Claude by Anthropic   ·", bg=BG, fg=MUTED).pack(side="left")
            Link(credit, "Join my Discord", DISCORD_URL).pack(side="left", padx=(6, 0))

        def open_editor(self, convert=False):
            ed = getattr(self, "_editor", None)
            try:
                if ed is not None and ed.winfo_exists():
                    ed.lift()
                    ed.focus_force()
                else:
                    ed = self._editor = MeshEditor(self)
            except tk.TclError:
                ed = self._editor = MeshEditor(self)
            if convert:  # open the file chooser right away: pick the model, then fix its direction and save
                self.after(350, ed.import_mesh)

        # ---- helpers
        def say(self, text):
            self.v_msg.set(text)
            fade_color(self.l_msg, GLOW, FG, 700)  # new messages flash in lilac, then settle

        def _close(self):
            save_cfg(self.cfg)
            self.destroy()

        def current_set(self):
            sel = self.lb.curselection()
            return self.set_names[sel[0]] if sel else None

        def maybe_welcome(self):
            if not self.cfg.get("welcome_shown"):
                self.cfg["welcome_shown"] = True
                save_cfg(self.cfg)
                self.wait_window(Welcome(self))

        def open_path(self, p):
            if os.name == "nt":
                os.startfile(str(p))  # noqa: S606

        # ---- Bloxstrap
        def refresh_bloxstrap(self):
            bdir = bloxstrap_dir(self.cfg)
            self.found = bdir.is_dir()
            if self.found:
                try:
                    ensure_meshes_dir(self.cfg)
                    self.v_bs.set(f"Bloxstrap found ✔   {bdir}")
                    self.l_bs.config(fg=GREEN)
                except OSError as e:
                    self.v_bs.set(f"Bloxstrap found, but the meshes folder could not be created: {e}")
                    self.l_bs.config(fg=AMBER)
                reconcile(self.cfg)
                save_cfg(self.cfg)
            else:
                self.v_bs.set("Bloxstrap not found ⚠   Install it from bloxstraplabs.com first.")
                self.l_bs.config(fg=AMBER)

        def pick_bloxstrap(self):
            d = filedialog.askdirectory(title="Select your Bloxstrap folder",
                                        initialdir=str(LOCAL if LOCAL.exists() else Path.home()))
            if d:
                self.cfg["bloxstrap_dir"] = d
                save_cfg(self.cfg)
                self.refresh_bloxstrap()
                self.refresh_sets(keep=self.current_set())

        def open_meshes(self):
            if not self.found:
                messagebox.showinfo(APP, "Bloxstrap was not found yet.")
                return
            try:
                ensure_meshes_dir(self.cfg)
                self.open_path(meshes_dir(self.cfg))
            except OSError as e:
                messagebox.showerror(APP, str(e))

        def open_sets(self):
            SETS.mkdir(parents=True, exist_ok=True)
            self.open_path(SETS)

        # ---- Roblox version + background results
        def refresh_roblox(self):
            self.local_version = current_version(self.cfg)
            self.l_rb.config(fg=MUTED)
            self.v_rb.set((f"Roblox {self.local_version} · " if self.local_version else "Roblox not found · ")
                          + "checking for updates…")

            def work():
                try:
                    info = fetch_latest_version()
                except Exception as e:  # noqa: BLE001
                    info = e
                self.q.put(("ver", info))

            threading.Thread(target=work, daemon=True).start()

        def _poll(self):
            try:
                while True:
                    try:
                        kind, *rest = self.q.get_nowait()
                    except queue.Empty:
                        break
                    try:
                        if kind == "ver":
                            text, level = roblox_status(self.local_version, rest[0])
                            self.v_rb.set(text)
                            self.l_rb.config(fg={"ok": GREEN, "warn": AMBER}.get(level, MUTED))
                            self._ver_done = True
                        elif kind == "rbx_run":
                            self._rbx_checking = False
                            self._rbx_update(rest[0], rest[1])
                        elif kind == "rbx_msg":
                            self.v_play.set(rest[0])
                        elif kind == "rbx_done":
                            self._rbx_busy = False
                            self._rbx_grace = time.time() + (12 if rest[0] else 0)
                            self.v_play.set(rest[1])
                            self.say(rest[1])
                        elif kind == "mesh":
                            req, res = rest
                            self.cache.update(res)
                            if req == self.req:
                                self.show_preview()
                    except Exception as e:  # noqa: BLE001  - one bad result must never stop the loop
                        log_error()
                        if kind == "mesh":
                            self.prev.clear(f"Preview error: {e}\n(details in {ERRLOG})")
            finally:
                self.after(80, self._poll)

        # ---- Roblox: launch / restart into the same game
        def _check_rbx(self):
            if not self._rbx_checking:  # one lookup at a time, in the background
                self._rbx_checking = True

                def work():
                    try:
                        run = roblox_running()
                        game = current_game() if run else None
                    except Exception:  # noqa: BLE001
                        run, game = False, None
                    self.q.put(("rbx_run", run, game))
                threading.Thread(target=work, daemon=True).start()
            self.after(4000, self._check_rbx)

        def _rbx_update(self, run, game):
            self.rbx_running = run
            if self._rbx_busy:
                return
            if not run and time.time() < self._rbx_grace:
                self.v_play.set("Roblox is starting…")
                self.b_launch.enable(False)
                self.b_refresh.enable(False)
                return
            if run:
                self.v_play.set("Roblox is running" + (f" · in a game (place {game[0]})" if game else " · no game joined yet"))
            else:
                self.v_play.set("Roblox is not running")
            self.b_launch.enable(not run)
            self.b_refresh.enable(run)

        def launch_roblox_clicked(self):
            if self._rbx_busy or self.rbx_running:
                return
            try:
                launch_roblox(self.cfg)
            except FileNotFoundError as e:
                messagebox.showwarning(APP, f"{e}\nInstall Bloxstrap, or use 'Choose Bloxstrap folder…'.", parent=self)
                return
            except OSError as e:
                messagebox.showerror(APP, f"Could not start Roblox:\n{e}", parent=self)
                return
            self._rbx_grace = time.time() + 15
            self.v_play.set("Launching Roblox through Bloxstrap…")
            self.b_launch.enable(False)
            self.say("Launching Roblox through Bloxstrap…")

        def refresh_game_clicked(self):
            if self._rbx_busy:
                return
            if not roblox_running():
                messagebox.showinfo(APP, "Roblox is not running. Use 'Launch Roblox' first.", parent=self)
                return
            game = current_game()
            ask = ("Roblox will close and start again, and you rejoin the same game (same server if it still exists)."
                   if game else "Roblox will close and start again. No game was found, so it opens normally.")
            if not messagebox.askyesno(APP, ask + "\n\nProgress in the game that is not saved will be lost. Continue?", parent=self):
                return
            self._rbx_busy = True
            self.b_launch.enable(False)
            self.b_refresh.enable(False)
            self.v_play.set("Restarting Roblox…")
            threading.Thread(target=self._rbx_worker, args=(game,), daemon=True).start()

        def _rbx_worker(self, game):
            try:
                self.q.put(("rbx_msg", "Closing Roblox…"))
                if not close_roblox():
                    self.q.put(("rbx_done", False, "Roblox did not close. Close it by hand and press Launch Roblox."))
                    return
                self.q.put(("rbx_msg", "Waiting for Bloxstrap to finish…"))
                time.sleep(1.0)
                wait_bloxstrap_idle()
                time.sleep(0.5)
                self.q.put(("rbx_msg", "Starting Roblox through Bloxstrap…"))
                launch_roblox(self.cfg, game_uri(game) if game else None)
                self.q.put(("rbx_done", True, "Roblox restarted - rejoining your game…" if game
                            else "Roblox restarted (no game was found, opened normally)."))
            except Exception as e:  # noqa: BLE001
                log_error()
                self.q.put(("rbx_done", False, f"Could not restart Roblox: {e}"))

        # ---- sets
        def refresh_sets(self, keep=None):
            if self.found:
                reconcile(self.cfg)
            self.set_names = list_sets()
            self.lb.delete(0, "end")
            for n in self.set_names:
                mark = "● " if applied_files(self.cfg, n) else "○ "
                self.lb.insert("end", f"{mark}{n}  ({len(set_files(n))})")
            if keep in self.set_names:
                self.lb.selection_set(self.set_names.index(keep))
            self.on_select_set()

        def new_set(self):
            raw = simpledialog.askstring(APP, "Name of the new set (e.g. Enderman):", parent=self)
            if raw is None:
                return
            name = safe_name(raw)
            if not name:
                messagebox.showwarning(APP, "Please enter a valid name.")
                return
            if (SETS / name).exists():
                messagebox.showwarning(APP, f"A set called {name} already exists.")
                return
            (SETS / name).mkdir(parents=True)
            self.refresh_sets(keep=name)
            self.say(f"Set {name} created. Use 'Add meshes…' to fill it.")

        def import_folder(self):
            d = filedialog.askdirectory(title="Select a folder with .mesh files")
            if not d:
                return
            src = Path(d)
            name = safe_name(src.name)
            meshes = [p for p in src.rglob("*") if p.is_file() and p.suffix.lower() == ".mesh"]
            if not name or not meshes:
                messagebox.showwarning(APP, "No .mesh files found in that folder.")
                return
            dest = SETS / name
            if dest.exists() and not messagebox.askyesno(
                    APP, f"A set called {name} already exists.\nAdd the files to it (same names get overwritten)?"):
                return
            dest.mkdir(parents=True, exist_ok=True)
            copied, bad = 0, 0
            for p in meshes:
                if header_version(p) is None:
                    bad += 1
                    continue
                shutil.copy2(p, dest / p.name)
                copied += 1
            self.refresh_sets(keep=name)
            self.say(f"Imported {copied} file(s) into {name}." + (f" Skipped {bad} invalid." if bad else ""))

        def delete_set(self):
            n = self.current_set()
            if not n:
                return
            if not messagebox.askyesno(APP, f"Delete the set {n} and all its files?\n"
                                            "(If it is applied, it will be reset first.)"):
                return
            try:
                if applied_files(self.cfg, n):
                    reset_set(self.cfg, n)
                shutil.rmtree(SETS / n)
            except OSError as e:
                messagebox.showerror(APP, str(e))
                return
            self.cfg["sets"].pop(n, None)
            save_cfg(self.cfg)
            self.refresh_sets()

        def on_select_set(self):
            n = self.current_set()
            self.flb.delete(0, "end")
            self.file_paths = set_files(n) if n else []
            for p in self.file_paths:
                self.flb.insert("end", p.name)
            self.update_preview()

        # ---- files in a set
        def selected_files(self):
            return [self.file_paths[i] for i in self.flb.curselection()]

        def add_meshes(self):
            n = self.current_set()
            if not n:
                messagebox.showinfo(APP, "Create or select a set first.")
                return
            files = filedialog.askopenfilenames(title="Select mesh files",
                                                filetypes=[("Roblox mesh", "*.mesh"), ("All files", "*.*")])
            bad = 0
            for f in files:
                p = Path(f)
                if header_version(p) is None:
                    bad += 1
                    continue
                shutil.copy2(p, SETS / n / p.name)
            if bad:
                messagebox.showwarning(APP, f"{bad} file(s) were not valid Roblox meshes and were skipped.")
            self.refresh_sets(keep=n)

        def rename_file(self):
            n, sel = self.current_set(), self.selected_files()
            if not n or len(sel) != 1:
                messagebox.showinfo(APP, "Select exactly one file to rename.")
                return
            p = sel[0]
            dlg = NameDialog(self, p.name)
            self.wait_window(dlg)
            if not dlg.result or dlg.result == p.name:
                return
            new = p.with_name(dlg.result)
            if new.exists() and new.name.lower() != p.name.lower():
                messagebox.showwarning(APP, f"{new.name} already exists in this set.")
                return
            try:
                p.rename(new)
            except OSError as e:
                messagebox.showerror(APP, str(e))
                return
            if applied_files(self.cfg, n):
                self.say("Renamed - press 'Apply set' again to update Bloxstrap.")
            self.refresh_sets(keep=n)

        def remove_files(self):
            n, sel = self.current_set(), self.selected_files()
            if not n or not sel:
                messagebox.showinfo(APP, "Select the file(s) to remove first.")
                return
            if not messagebox.askyesno(APP, f"Remove {len(sel)} file(s) from the set {n}?"):
                return
            for p in sel:
                p.unlink(missing_ok=True)
            if applied_files(self.cfg, n):
                self.say("Removed - press 'Apply set' again to update Bloxstrap.")
            self.refresh_sets(keep=n)

        def show_whole(self):
            self.flb.selection_clear(0, "end")
            self.update_preview()

        @staticmethod
        def _key(p):
            try:
                return (str(p), p.stat().st_mtime)
            except OSError:
                return (str(p), 0)

        def update_preview(self):
            n = self.current_set()
            self.req += 1
            if not n:
                self.prev.clear("Select a set to see the preview")
                self.v_info.set("")
                return
            if not self.file_paths:
                self.prev.clear("This set is empty. Use 'Add meshes…' or drop .mesh files into its folder.")
                self.v_info.set(f"{n} · 0 files")
                return
            chosen = self.selected_files() or self.file_paths
            need = [p for p in chosen if self._key(p) not in self.cache]
            if not need:
                self.show_preview()
                return
            self.prev.clear("Loading preview…")
            req = self.req

            def work():  # parsing happens in the background so the window never freezes
                res = {}
                try:
                    for p in need:
                        try:
                            res[self._key(p)] = prepare_mesh(p)
                        except Exception as e:  # noqa: BLE001
                            if not isinstance(e, MeshError):
                                log_error()
                            res[self._key(p)] = e
                finally:
                    self.q.put(("mesh", req, res))  # always answer, so "Loading…" can never hang

            threading.Thread(target=work, daemon=True).start()

        def set_fix_sizes(self, on):
            self.fix_sizes = bool(on)
            self.show_preview()

        def set_assemble(self, on):
            self.assemble_origin = bool(on)
            self.show_preview()

        def show_preview(self):
            n = self.current_set()
            if not n or not self.file_paths:
                return
            chosen = self.selected_files() or self.file_paths
            parts, failed = [], []
            for p in chosen:
                got = self.cache.get(self._key(p))
                if isinstance(got, Exception):
                    failed.append(f"{p.name}: {got}")
                elif got is not None:
                    parts.append((p.name, got))
            if not parts:
                self.prev.clear(failed[0] if failed else "Nothing to preview")
                self.v_info.set("")
                return
            try:
                scene, assembled = build_scene(parts, origin=self.assemble_origin, fix_sizes=self.fix_sizes)
            except MeshError as e:
                self.prev.clear(str(e))
                self.v_info.set("")
                return
            self.prev.set_scene(scene)
            tip = "drag to rotate, scroll to zoom"
            if len(parts) == 1:
                name, prep = parts[0]
                self.v_info.set(f"{name} · Format {prep['ver']} · {prep['nv']} points · {prep['nf']} triangles · {tip}")
            else:
                if assembled > 1:
                    text = f"{n} · {assembled} parts assembled like the Roblox dummy"
                    extra = len(parts) - assembled
                    if extra:
                        text += f" · {extra} other part(s) shown below"
                else:
                    text = f"{n} · {len(parts)} parts side by side (file names not recognised)"
                if scene.get("origin"):
                    text += " · every part at its Roblox origin"
                for nm, inf in scene.get("adjusted", []):
                    if inf["stray"]:
                        text += f" · {nm} has stray points far outside the body (ignored here)"
                    if inf["scaled"]:
                        sz = inf["size"]
                        text += f" · {nm} was {sz[0]:.3g} x {sz[1]:.3g} x {sz[2]:.3g} studs (unusual), scaled evenly to a normal size"
                text += f" · {tip}"
                if failed:
                    text += f" · {len(failed)} without preview"
                self.v_info.set(text)

        # ---- apply / reset
        def apply(self):
            n = self.current_set()
            if not n:
                return
            if not self.found:
                messagebox.showwarning(APP, "Bloxstrap was not found.\nInstall it from bloxstraplabs.com first, "
                                            "or choose its folder at the top.")
                return
            try:
                ensure_meshes_dir(self.cfg)
                foreign = foreign_files(self.cfg, n)
                if foreign:
                    shown = ", ".join(foreign[:8]) + (" …" if len(foreign) > 8 else "")
                    if not messagebox.askyesno(APP, f"These files already exist in your Bloxstrap meshes folder and "
                                                    f"were not created by MeshSwapper:\n\n{shown}\n\nOverwrite them?"):
                        return
                count, skipped = apply_set(self.cfg, n)
                save_cfg(self.cfg)
                msg = f"{n} applied ({count} files). Launch Roblox through Bloxstrap."
                self.say(msg)
                if skipped:
                    messagebox.showwarning(APP, "Skipped (not valid Roblox meshes):\n" + "\n".join(skipped))
            except Exception as e:  # noqa: BLE001
                messagebox.showerror(APP, str(e))
            self.refresh_sets(keep=n)

        def reset(self):
            n = self.current_set()
            if not n:
                return
            try:
                reset_set(self.cfg, n)
                save_cfg(self.cfg)
                self.say(f"{n} reset.")
            except Exception as e:  # noqa: BLE001
                messagebox.showerror(APP, str(e))
            self.refresh_sets(keep=n)

        def reset_everything(self):
            if not messagebox.askyesno(APP, "Remove all meshes MeshSwapper applied and go back to the originals?"):
                return
            try:
                reset_all(self.cfg)
                save_cfg(self.cfg)
                self.say("Everything reset.")
            except Exception as e:  # noqa: BLE001
                messagebox.showerror(APP, str(e))
            self.refresh_sets(keep=self.current_set())


def main():
    if tk is None:
        print("tkinter is missing - please install Python with Tk support.")
        sys.exit(1)
    if np is None:
        root = tk.Tk()
        root.withdraw()
        if getattr(sys, "frozen", False):
            messagebox.showerror(APP, "This build is missing numpy. Please rebuild it with build_exe.bat.")
            sys.exit(1)
        if messagebox.askyesno(APP, "MeshSwapper needs the package 'numpy' for the preview.\n\n"
                                    "Install it now? (needs internet, takes about a minute)"):
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "numpy"], check=True,
                               creationflags=0x08000000 if os.name == "nt" else 0)
            except Exception as e:  # noqa: BLE001
                messagebox.showerror(APP, f"Installing numpy failed:\n{e}")
                sys.exit(1)
            subprocess.Popen([sys.executable] + sys.argv)  # start again, now with numpy
        sys.exit(0)
    try:
        App().mainloop()
    except Exception:  # noqa: BLE001  - never close silently: show and save the error
        text = log_error()
        try:
            if getattr(tk, "_default_root", None) is not None:
                tk._default_root.destroy()  # also removes a splash that may still be showing
        except Exception:  # noqa: BLE001
            pass
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(APP, f"MeshSwapper crashed:\n\n{text[-1500:]}\n\n(also saved to {ERRLOG})")
        sys.exit(1)


if __name__ == "__main__":
    main()
