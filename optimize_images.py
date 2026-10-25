#!/usr/bin/env python3
"""Shrink wp-content/uploads images after each Simply Static export.

Runs on every deploy (invoked from deploy.sh). Source images in Local WP are
always the pristine originals, so this always re-derives from them instead of
re-compressing an already-compressed file.

- JPEG: recompressed in place at quality 78 if that's smaller.
- PNG: if fully opaque, converted to JPEG (quality 78) and every HTML/CSS/XML
  reference to the old filename is rewritten to the new one.
"""
import re
import subprocess
import sys
from pathlib import Path

JPEG_QUALITY = "78"
TEXT_EXTS = {".html", ".css", ".js", ".xml", ".json", ".xsl", ".txt"}


def is_opaque(path: Path) -> bool:
    try:
        out = subprocess.run(
            ["convert", str(path), "-format", "%[opaque]", "info:"],
            capture_output=True, text=True, timeout=30,
        ).stdout.strip()
    except Exception:
        return False
    return out == "True"


def recompress_jpeg(path: Path) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    r = subprocess.run(
        ["sips", "-s", "format", "jpeg", "-s", "formatOptions", JPEG_QUALITY,
         str(path), "--out", str(tmp)],
        capture_output=True, timeout=60,
    )
    if r.returncode != 0 or not tmp.exists() or tmp.stat().st_size == 0:
        tmp.unlink(missing_ok=True)
        return
    if tmp.stat().st_size < path.stat().st_size:
        tmp.replace(path)
    else:
        tmp.unlink(missing_ok=True)


def png_to_jpeg(path: Path) -> Path | None:
    tmp = path.with_suffix(".jpg.tmp")
    r = subprocess.run(
        ["sips", "-s", "format", "jpeg", "-s", "formatOptions", JPEG_QUALITY,
         str(path), "--out", str(tmp)],
        capture_output=True, timeout=60,
    )
    if r.returncode != 0 or not tmp.exists() or tmp.stat().st_size == 0:
        tmp.unlink(missing_ok=True)
        return None
    if tmp.stat().st_size >= path.stat().st_size:
        tmp.unlink(missing_ok=True)
        return None
    new_path = path.with_suffix(".jpg")
    tmp.replace(new_path)
    path.unlink()
    return new_path


def main() -> None:
    repo_dir = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    uploads_dir = repo_dir / "wp-content" / "uploads"
    if not uploads_dir.is_dir():
        print("==> uploads フォルダが見つからないためスキップします")
        return

    renames: dict[str, str] = {}
    jpeg_count = 0

    for path in uploads_dir.rglob("*"):
        if not path.is_file():
            continue
        suffix = path.suffix.lower()
        if suffix in (".jpg", ".jpeg"):
            recompress_jpeg(path)
            jpeg_count += 1
        elif suffix == ".png":
            if is_opaque(path):
                new_path = png_to_jpeg(path)
                if new_path is not None:
                    renames[path.name] = new_path.name

    print(f"==> JPEG再圧縮: {jpeg_count}件")
    print(f"==> PNG->JPEG変換: {len(renames)}件")

    if not renames:
        return

    pattern = re.compile("|".join(re.escape(k) for k in renames.keys()))
    changed_files = 0
    for path in repo_dir.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_EXTS:
            continue
        if ".git" in path.parts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        new_text, n = pattern.subn(lambda m: renames[m.group(0)], text)
        if n:
            path.write_text(new_text, encoding="utf-8")
            changed_files += 1

    print(f"==> ファイル名参照を更新したファイル数: {changed_files}")


if __name__ == "__main__":
    main()
