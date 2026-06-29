#!/usr/bin/env python3
"""Shared helpers for the math-modeling verification scripts."""

from __future__ import annotations

import os
import re
from pathlib import Path


INCLUDE_RE = re.compile(
    r'#include\s*(?:\(\s*"([^"]+\.typ)"\s*\)|"([^"]+\.typ)")'
)


def read_utf8(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_typst_includes(text: str) -> list[str]:
    includes: list[str] = []
    for paren_form, bare_form in INCLUDE_RE.findall(text):
        include = paren_form or bare_form
        if include:
            includes.append(include)
    return includes


def _looks_windows_absolute(raw: str) -> bool:
    return bool(re.match(r"^[A-Za-z]:[\\/]", raw))


def candidate_repo_paths(root: Path, raw_ref: str, base_dir: Path | None = None) -> list[Path]:
    text = str(raw_ref).strip()
    if not text:
        return []

    root = root.resolve()
    base_dir = (base_dir or root).resolve()
    candidates: list[Path] = []
    seen: set[str] = set()

    def add(path: Path) -> None:
        resolved = path.resolve(strict=False)
        key = os.path.normcase(str(resolved))
        if key not in seen:
            candidates.append(resolved)
            seen.add(key)

    if _looks_windows_absolute(text) or text.startswith("\\\\"):
        add(Path(text))
        return candidates

    if text.startswith(("/", "\\")):
        add(root / text.lstrip("/\\"))
        if os.path.isabs(text):
            add(Path(text))
        return candidates

    add(base_dir / Path(text))
    if base_dir != root:
        add(root / Path(text))
    return candidates


def canonical_path_keys(root: Path, raw_ref: str, base_dir: Path | None = None) -> set[str]:
    return {
        os.path.normcase(str(path.resolve(strict=False)))
        for path in candidate_repo_paths(root, raw_ref, base_dir=base_dir)
    }


def canonical_ref_keys(root: Path, raw_ref: str, base_dir: Path | None = None) -> set[str]:
    text = str(raw_ref).strip()
    if not text:
        return set()

    path_part, sep, fragment = text.partition("#")
    suffix = f"#{fragment.strip()}" if sep else ""
    return {
        f"{path_key}{suffix}"
        for path_key in canonical_path_keys(root, path_part, base_dir=base_dir)
    }


def best_effort_relative(root: Path, path: Path) -> str:
    try:
        return str(path.resolve(strict=False).relative_to(root.resolve())).replace("\\", "/")
    except Exception:
        return str(path)
