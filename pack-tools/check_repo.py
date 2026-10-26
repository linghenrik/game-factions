# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""The content repo's one check: repo rules, the pack lint, the audio licence gate and a change summary.

Standard library only and no sibling imports (it runs its siblings as subprocesses).

    uv run pack-tools/check_repo.py [--root <clone>] [--base <rev>] [--ci]
"""

from __future__ import annotations

import argparse
import io
import os
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
LFS_EXTS = ("glb", "png", "ogg", "wav")
LFS_HEADER = b"version https://git-lfs.github.com/spec/v1\n"
LFS_MAX = 1024
GITATTRIBUTES = "* -text\n" + "".join(
    f"*.{ext} filter=lfs diff=lfs merge=lfs -text\n" for ext in LFS_EXTS
)
NOT_PACKS = ("pack-tools", "docs")
SIBLINGS = (
    "lint_pack.py",
    "change_summary.py",
    "audio_credits.py",
    "art_credits.py",
    "pack_categories.json",
)
NO_KIT_NOTE = "the kit is incomplete: skipped the lint, the audio and art licence checks and the change summary"
NO_BASE_NOTE = "no origin/main: skipped the change summary (run git fetch)"


class GitError(Exception):
    """A git call the check cannot go on without."""


def _item(file: str, rule: str, message: str) -> dict:
    return {"file": file, "rule": rule, "message": message}


def _git(root: Path, *args: str, data: bytes | None = None) -> subprocess.CompletedProcess:
    env = dict(os.environ, GIT_LFS_SKIP_SMUDGE="1")
    return subprocess.run(
        ["git", "-C", str(root), *args], input=data, capture_output=True, env=env, check=False
    )


def _must(root: Path, *args: str, data: bytes | None = None) -> bytes:
    r = _git(root, *args, data=data)
    if r.returncode != 0:
        err = r.stderr.decode("utf-8", "replace").strip().splitlines()
        raise GitError(f"git {args[0]} failed: {err[-1] if err else 'no message'}")
    return r.stdout


def _listing(root: Path, *args: str) -> list[str]:
    out = _git(root, *args).stdout
    return [p.decode("utf-8", "surrogateescape") for p in out.split(b"\0") if p]


def packs(root: Path) -> list[str]:
    return sorted(
        d.name
        for d in Path(root).iterdir()
        if d.is_dir() and not d.name.startswith(".") and d.name not in NOT_PACKS
    )


def _ext(path: str) -> str:
    return path.rsplit(".", 1)[1] if "." in path.rsplit("/", 1)[-1] else ""


def _is_pointer(blob: bytes) -> bool:
    return len(blob) < LFS_MAX and blob.startswith(LFS_HEADER)


def _head_blobs(root: Path, wanted: list[str]) -> dict[str, bytes]:
    """Blob contents at HEAD for the wanted paths, through one `git cat-file --batch`."""
    entries = _must(root, "ls-tree", "-r", "-z", "HEAD").split(b"\0")
    shas = {}
    for e in entries:
        meta, _, path = e.partition(b"\t")
        if path:
            shas[path.decode("utf-8", "surrogateescape")] = meta.split()[2].decode()
    todo = [p for p in wanted if p in shas]
    if not todo:
        return {}
    req = "".join(f"{shas[p]}\n" for p in todo).encode()
    buf = io.BytesIO(_must(root, "cat-file", "--batch", data=req))
    out = {}
    for p in todo:
        head = buf.readline().split()
        if len(head) != 3 or head[1] == b"missing":
            raise GitError(f"git object for {p} is missing: run `git fetch` or clone again")
        size = head[2]
        out[p] = buf.read(int(size))
        buf.read(1)
    return out


def check(root: Path, ci: bool) -> list[dict]:
    root = Path(root)
    items: list[dict] = []
    for name in SIBLINGS:
        if not (HERE / name).is_file():
            items.append(
                _item(
                    f"pack-tools/{name}",
                    "kit",
                    "the kit is incomplete: ask the owner to run `content.py kit`",
                )
            )
    tracked = _listing(root, "ls-files", "-z", "-c")
    for f in tracked:
        if f != ".gitattributes" and f.rsplit("/", 1)[-1] == ".gitattributes":
            items.append(
                _item(
                    f,
                    "gitattributes",
                    f'only the root .gitattributes is allowed: run `git rm --cached "{f}"`',
                )
            )
        if f.rsplit("/", 1)[-1] == ".lfsconfig":
            items.append(
                _item(
                    f,
                    "lfsconfig",
                    "remove it: it would send the repo's big files to another server",
                )
            )
    candidates = []
    for f in tracked:
        ext = _ext(f)
        if ext in LFS_EXTS:
            candidates.append(f)
        elif ext.lower() in LFS_EXTS:
            items.append(
                _item(
                    f,
                    "lfs-case",
                    f"rename it to lower case (.{ext.lower()}): Git LFS only picks up "
                    "lower-case names",
                )
            )
    for f, blob in _head_blobs(root, candidates).items():
        if blob and not _is_pointer(blob):  # git-lfs stores an empty file as an empty blob
            items.append(
                _item(
                    f,
                    "lfs-raw",
                    "stored in git, not Git LFS: run `git lfs install`, then "
                    f'`git rm --cached "{f}"`, `git add "{f}"` and commit. '
                    "Squash merging keeps the raw copy out of main",
                )
            )
    for f in _listing(root, "ls-files", "-z", "-c", "-i", "--exclude-standard"):
        items.append(
            _item(
                f,
                "ignored",
                f'.import files and extracted textures stay out: run `git rm --cached "{f}"`',
            )
        )
    head = _git(root, "show", "HEAD:.gitattributes")
    if _git(root, "rev-parse", "--verify", "-q", "HEAD").returncode == 0 and (
        head.returncode != 0 or head.stdout.decode("utf-8", "replace") != GITATTRIBUTES
    ):
        items.append(
            _item(
                ".gitattributes",
                "gitattributes",
                "the LFS rules changed: restore .gitattributes from main",
            )
        )
    if not ci and not _git(root, "config", "--get", "filter.lfs.process").stdout.strip():
        for pack in packs(root):
            hit = next(
                (p for p in (root / pack).rglob("*") if p.is_file() and p.suffix[1:] in LFS_EXTS),
                None,
            )
            if hit is not None:
                items.append(
                    _item(
                        hit.relative_to(root).as_posix(),
                        "lfs-setup",
                        "git-lfs is not set up: install it before committing "
                        "(`brew install git-lfs` on macOS, or https://git-lfs.com), "
                        "then run `git lfs install`",
                    )
                )
                break
    return items


def _extract(root: Path, rev: str, dest: Path) -> None:
    tar = _must(root, "archive", "--format=tar", rev)
    try:
        with tarfile.open(fileobj=io.BytesIO(tar)) as t:
            t.extractall(dest, filter="data")
    except (tarfile.TarError, OSError) as e:
        raise GitError(f"cannot unpack {rev}: {e}") from e


def summary(root: Path, base: str) -> str | None:
    root = Path(root)
    if _git(root, "rev-parse", "--verify", "-q", f"{base}^{{commit}}").returncode != 0:
        return None
    note = ""
    mb = _git(root, "merge-base", base, "HEAD")
    if mb.returncode == 0 and mb.stdout.strip():
        base = mb.stdout.decode().strip()
    else:
        note = "(no common ancestor with the base: compared with its tip)\n\n"
    with tempfile.TemporaryDirectory() as tmp:
        old, new = Path(tmp) / "base", Path(tmp) / "head"
        old.mkdir()
        new.mkdir()
        _extract(root, base, old)
        _extract(root, "HEAD", new)
        r = subprocess.run(
            [sys.executable, str(HERE / "change_summary.py"), str(old), str(new)],
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            env=dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8"),
            check=False,
        )
    return note + r.stdout if r.returncode == 0 else f"change_summary failed: {r.stderr.strip()}\n"


def _toplevel() -> Path:
    r = subprocess.run(
        ["git", "-C", str(HERE), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=False,
    )
    return Path(r.stdout.strip()) if r.returncode == 0 else HERE.parent


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Check a content repo.")
    ap.add_argument("--root")
    ap.add_argument("--base")
    ap.add_argument("--ci", action="store_true")
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="replace")
    root = Path(args.root).resolve() if args.root else _toplevel()
    try:
        return _run(root, args)
    except GitError as e:
        print(f"check_repo: {e}", file=sys.stderr)
        return 2


def _run(root: Path, args: argparse.Namespace) -> int:
    items = check(root, args.ci)
    for it in items:
        print(f"{it['file']}: [{it['rule']}] {it['message']}")
    problems = len(items)
    names = packs(root)
    kit_ok = not any(i["rule"] == "kit" for i in items)
    if not names:
        print("no packs yet")
    elif kit_ok:
        cmd = [
            sys.executable,
            str(HERE / "lint_pack.py"),
            "--categories",
            str(HERE / "pack_categories.json"),
            *(["--allow-lfs-pointers"] if args.ci else []),
            *names,
        ]
        r = subprocess.run(
            cmd,
            cwd=root,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            env=dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8"),
            check=False,
        )
        sys.stdout.write(r.stdout)
        sys.stderr.write(r.stderr)
        lines = [ln for ln in r.stdout.splitlines() if ln.strip()]
        problems += len(lines) if r.returncode == 0 else max(len(lines), 1)
        # Every sound must be credited and free to share (audio_credits.py, TODO step 29).
        r = subprocess.run(
            [sys.executable, str(HERE / "audio_credits.py"), *names],
            cwd=root,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            env=dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8"),
            check=False,
        )
        sys.stdout.write(r.stdout)
        sys.stderr.write(r.stderr)
        lines = [ln for ln in r.stdout.splitlines() if ln.strip()]
        problems += 0 if r.returncode == 0 else max(len(lines), 1)
        # Every model, icon and texture must be credited and allowed (art_credits.py).
        r = subprocess.run(
            [sys.executable, str(HERE / "art_credits.py"), *names],
            cwd=root,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            env=dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8"),
            check=False,
        )
        sys.stdout.write(r.stdout)
        sys.stderr.write(r.stderr)
        lines = [ln for ln in r.stdout.splitlines() if ln.strip()]
        problems += 0 if r.returncode == 0 else max(len(lines), 1)
    base = args.base or "origin/main"
    text = summary(root, base) if kit_ok else None
    print("## Change summary")
    if text is None:
        if not kit_ok:
            note = NO_KIT_NOTE
        elif args.base:
            note = f"base {args.base} not found: skipped the summary"
        else:
            note = NO_BASE_NOTE
        print(note)
    else:
        print("(committed changes only)\n")
        print(text)
        target = os.environ.get("GITHUB_STEP_SUMMARY")
        if args.ci and target:
            with open(target, "a", encoding="utf-8") as fh:
                fh.write("## Change summary\n\n(committed changes only)\n\n" + text + "\n")
    print(
        f"check_repo: {problems} problems" if problems else f"check_repo: OK ({len(names)} packs)"
    )
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
