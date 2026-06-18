#!/usr/bin/env python3
"""Run lightweight deterministic checks on a GitHub README."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import unquote


LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
WINDOWS_PATH_RE = re.compile(r"(?<![A-Za-z0-9_])[A-Za-z]:[\\/](?:Users|Documents|Desktop|AppData)[\\/]", re.I)
PLACEHOLDER_RE = re.compile(r"\b(?:TODO|TBD|YOUR_USERNAME|YOUR_ORG|REPLACE_ME)\b", re.I)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("readme", type=Path, help="README.md path")
    parser.add_argument(
        "--repo-root",
        type=Path,
        help="Repository root used to resolve root-relative links; defaults to README parent",
    )
    return parser.parse_args()


def local_target(raw_target: str) -> str | None:
    target = raw_target.strip().strip("<>")
    if not target or target.startswith(("#", "http://", "https://", "mailto:", "data:")):
        return None
    # Drop optional Markdown title after a whitespace separator.
    target = re.split(r"\s+[\"']", target, maxsplit=1)[0]
    return unquote(target.split("#", 1)[0])


def main() -> int:
    args = parse_args()
    readme = args.readme.resolve()
    repo_root = (args.repo_root or readme.parent).resolve()
    errors: list[str] = []
    warnings: list[str] = []

    if not readme.is_file():
        print(f"ERROR: README not found: {readme}")
        return 1

    try:
        text = readme.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        print(f"ERROR: README is not valid UTF-8: {exc}")
        return 1

    if not text.strip():
        errors.append("README is empty")
    if "\ufffd" in text:
        errors.append("README contains Unicode replacement characters")
    if text.count("```") % 2:
        errors.append("fenced code blocks are unbalanced")
    if not re.search(r"(?m)^#\s+\S", text):
        warnings.append("README has no level-1 heading")
    if WINDOWS_PATH_RE.search(text):
        warnings.append("README may expose a private Windows user path")

    placeholders = sorted({match.group(0) for match in PLACEHOLDER_RE.finditer(text)})
    if placeholders:
        warnings.append("possible placeholders: " + ", ".join(placeholders))

    checked_links = 0
    for match in LINK_RE.finditer(text):
        target = local_target(match.group(1))
        if target is None:
            continue
        checked_links += 1
        candidate = (repo_root / target.lstrip("/")) if target.startswith("/") else (readme.parent / target)
        if not candidate.resolve().exists():
            errors.append(f"broken relative link: {match.group(1)}")

    for message in errors:
        print(f"ERROR: {message}")
    for message in warnings:
        print(f"WARN: {message}")

    if errors:
        print(f"FAIL: {len(errors)} error(s), {len(warnings)} warning(s), {checked_links} local link(s) checked")
        return 1

    print(f"PASS: UTF-8, code fences, and {checked_links} local link(s) checked; {len(warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
