#!/usr/bin/env python3
"""Validate the multilingual Markdown documentation tree."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git"}
REQUIRED = [
    ROOT / "README.md",
    ROOT / "AGENTS.md",
    ROOT / "SECURITY.md",
    ROOT / "LOCALIZATION.md",
    ROOT / "en" / "README.md",
    ROOT / "en" / "AGENTS.md",
    ROOT / "en" / "SECURITY.md",
]
MIRROR_EXEMPT = {
    Path("README.md"),
    Path("AGENTS.md"),
    Path("SECURITY.md"),
}
LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")


def markdown_files(base: Path) -> list[Path]:
    return sorted(
        path
        for path in base.rglob("*.md")
        if not any(part in SKIP_DIRS for part in path.parts)
    )


def check_fences(path: Path, text: str, errors: list[str]) -> None:
    if sum(1 for line in text.splitlines() if line.lstrip().startswith("```")) % 2:
        errors.append(f"unbalanced fenced code block: {path.relative_to(ROOT)}")


def check_links(path: Path, text: str, errors: list[str]) -> None:
    for raw in LINK_RE.findall(text):
        target = raw.strip().split(maxsplit=1)[0].strip("<>")
        if not target or target.startswith(("#", "http://", "https://", "mailto:")):
            continue
        target_path = unquote(target.split("#", 1)[0])
        if not target_path:
            continue
        resolved = (path.parent / target_path).resolve()
        try:
            resolved.relative_to(ROOT)
        except ValueError:
            errors.append(f"link escapes repository: {path.relative_to(ROOT)} -> {target}")
            continue
        if not resolved.exists():
            errors.append(f"broken local link: {path.relative_to(ROOT)} -> {target}")


def main() -> int:
    errors: list[str] = []
    for path in REQUIRED:
        if not path.is_file() or path.stat().st_size == 0:
            errors.append(f"missing required entry point: {path.relative_to(ROOT)}")

    files = markdown_files(ROOT)
    for path in files:
        text = path.read_text(encoding="utf-8")
        check_fences(path, text, errors)
        check_links(path, text, errors)

    source_files = [
        path
        for path in files
        if "en" not in path.relative_to(ROOT).parts
        and path.relative_to(ROOT) not in MIRROR_EXEMPT
    ]
    for source in source_files:
        relative = source.relative_to(ROOT)
        mirror = ROOT / "en" / relative
        if not mirror.is_file() or mirror.stat().st_size == 0:
            errors.append(f"missing English mirror: {relative}")

    if errors:
        print("Documentation checks failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Documentation checks passed: {len(files)} Markdown files validated.")
    print(f"English mirrors covered: {len(source_files)}/{len(source_files)}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
