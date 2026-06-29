#!/usr/bin/env python3
"""Deterministic contract-closure gate for the math-modeling workflow."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Iterable

from verity_shared import (
    best_effort_relative,
    canonical_path_keys,
    canonical_ref_keys,
    read_utf8,
)


FIGURE_EXTS = {".pdf", ".png", ".jpg", ".jpeg", ".svg"}


class Reporter:
    def __init__(self) -> None:
        self.failures: list[str] = []
        self.warnings: list[str] = []

    def info(self, msg: str) -> None:
        print(f"INFO: {msg}")

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)
        print(f"WARN: {msg}")

    def fail(self, msg: str) -> None:
        self.failures.append(msg)
        print(f"FAIL: {msg}")

    @property
    def exit_code(self) -> int:
        return 1 if self.failures else 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Check contract closure in the order "
            "model_tasks.json -> all_results.json -> figure_manifest.json -> paper body."
        )
    )
    parser.add_argument("--root-dir", default=".", help="Project root directory.")
    parser.add_argument("--model-tasks", help="Path to reports/contracts/model_tasks.json.")
    parser.add_argument("--all-results", help="Path to results/all_results.json.")
    parser.add_argument("--figure-manifest", help="Path to figures/figure_manifest.json.")
    parser.add_argument("--paper-dir", help="Paper directory. Defaults to <root-dir>/paper.")
    parser.add_argument("--main", help="Typst entry file. Defaults to <paper-dir>/main.typ.")
    parser.add_argument(
        "--sections-dir",
        help="Section directory. Defaults to <paper-dir>/sections when it exists.",
    )
    return parser.parse_args()


def read_text(path: Path) -> str:
    return read_utf8(path)


def load_json(path: Path) -> object:
    return json.loads(read_text(path))


def load_manifest_entries(data: object) -> list[dict]:
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if isinstance(data, dict):
        for key in ("figures", "items", "entries"):
            value = data.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    return []


def load_subproblems(data: object) -> list[dict]:
    if isinstance(data, dict):
        for key in ("subproblems", "tasks"):
            value = data.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    return []


def flatten_strings(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        out: list[str] = []
        for item in value:
            out.extend(flatten_strings(item))
        return out
    return []


def has_validation(result_entry: dict) -> bool:
    for key in ("validation", "constraint_checks", "verification"):
        value = result_entry.get(key)
        if isinstance(value, dict) and value:
            return True
        if isinstance(value, list) and value:
            return True
        if isinstance(value, str) and value.strip():
            return True
    return False


def metric_candidates(contract_metric: str, contract_entry: dict, result_entry: dict) -> list[str]:
    candidates = {contract_metric}

    for alias_source in (contract_entry.get("metric_aliases"), result_entry.get("metric_aliases")):
        if not isinstance(alias_source, dict):
            continue
        direct = alias_source.get(contract_metric)
        if isinstance(direct, str):
            candidates.add(direct)
        elif isinstance(direct, list):
            candidates.update(item for item in direct if isinstance(item, str))
        for actual_name, canonical in alias_source.items():
            if canonical == contract_metric and isinstance(actual_name, str):
                candidates.add(actual_name)
            if isinstance(canonical, list) and contract_metric in canonical and isinstance(actual_name, str):
                candidates.add(actual_name)

    return [item for item in candidates if item]


def extract_typst_files(paper_dir: Path, main_file: Path, sections_dir: Path | None) -> list[Path]:
    files = [main_file]
    if sections_dir and sections_dir.exists():
        files.extend(sorted(sections_dir.glob("*.typ")))
    else:
        files.extend(sorted(path for path in paper_dir.rglob("*.typ") if path != main_file))
    seen: set[Path] = set()
    out: list[Path] = []
    for path in files:
        if path.exists() and path not in seen:
            out.append(path)
            seen.add(path)
    return out


def extract_image_paths(typst_files: Iterable[Path]) -> list[tuple[Path, str]]:
    image_re = re.compile(r'image\(\s*"([^"]+)"')
    refs: list[tuple[Path, str]] = []
    for path in typst_files:
        text = read_text(path)
        for raw in image_re.findall(text):
            refs.append((path, raw))
    return refs


def has_structured_evidence(result_entry: dict) -> bool:
    for key, value in result_entry.items():
        if key in {
            "id",
            "metrics",
            "metric_aliases",
            "figures",
            "tables",
            "artifacts",
            "outputs",
            "figure_absence_reason",
            "validation",
            "verification",
            "constraint_checks",
            "data_sources",
            "reproduce_command",
        }:
            continue
        if isinstance(value, (dict, list)) and value:
            return True
        if isinstance(value, str) and value.strip():
            return True
        if isinstance(value, (int, float, bool)):
            return True
    return False


def main() -> int:
    args = parse_args()
    reporter = Reporter()

    root = Path(args.root_dir).resolve()
    model_tasks = Path(args.model_tasks).resolve() if args.model_tasks else root / "reports/contracts/model_tasks.json"
    all_results = Path(args.all_results).resolve() if args.all_results else root / "results/all_results.json"
    figure_manifest = (
        Path(args.figure_manifest).resolve()
        if args.figure_manifest
        else root / "figures/figure_manifest.json"
    )
    paper_dir = Path(args.paper_dir).resolve() if args.paper_dir else root / "paper"
    main_file = Path(args.main).resolve() if args.main else paper_dir / "main.typ"
    if args.sections_dir:
        sections_dir = Path(args.sections_dir).resolve()
    else:
        default_sections = paper_dir / "sections"
        sections_dir = default_sections if default_sections.exists() else None

    reporter.info(f"root dir: {root}")
    reporter.info(f"model tasks: {model_tasks}")
    reporter.info(f"all-results: {all_results}")
    reporter.info(f"figure manifest: {figure_manifest}")
    reporter.info(f"paper dir: {paper_dir}")
    reporter.info(f"main file: {main_file}")

    required_files = {
        "model_tasks.json": model_tasks,
        "all_results.json": all_results,
        "figure_manifest.json": figure_manifest,
    }
    for label, path in required_files.items():
        if not path.exists():
            reporter.fail(f"missing required closure input: {label} -> {path}")
    if reporter.failures:
        print("FAIL: contract closure gate failed")
        return reporter.exit_code

    try:
        contract_data = load_json(model_tasks)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        reporter.fail(f"cannot parse model_tasks.json: {exc}")
        print("FAIL: contract closure gate failed")
        return reporter.exit_code

    try:
        result_data = load_json(all_results)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        reporter.fail(f"cannot parse all_results.json: {exc}")
        print("FAIL: contract closure gate failed")
        return reporter.exit_code

    try:
        manifest_data = load_json(figure_manifest)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        reporter.fail(f"cannot parse figure_manifest.json: {exc}")
        print("FAIL: contract closure gate failed")
        return reporter.exit_code

    contract_subproblems = load_subproblems(contract_data)
    result_subproblems = load_subproblems(result_data)
    manifest_entries = load_manifest_entries(manifest_data)

    if not contract_subproblems:
        reporter.fail("model_tasks.json has no contract subproblems")
    if not result_subproblems:
        reporter.fail("all_results.json has no subproblem results")
    if reporter.failures:
        print("FAIL: contract closure gate failed")
        return reporter.exit_code

    result_map = {
        str(item.get("id")).strip(): item
        for item in result_subproblems
        if str(item.get("id", "")).strip()
    }
    manifest_by_path: dict[str, dict] = {}
    for entry in manifest_entries:
        raw_path = str(entry.get("path", "")).strip()
        if not raw_path:
            continue
        for key in canonical_path_keys(root, raw_path):
            manifest_by_path[key] = entry

    for contract_entry in contract_subproblems:
        sub_id = str(contract_entry.get("id", "")).strip()
        if not sub_id:
            reporter.fail("contract subproblem missing id")
            continue
        if sub_id not in result_map:
            reporter.fail(f"[{sub_id}] missing subproblem result entry in all_results.json")
            continue

        result_entry = result_map[sub_id]
        metrics = result_entry.get("metrics")
        outputs = flatten_strings(contract_entry.get("outputs"))
        required_figures = [item for item in outputs if Path(item.split("#", 1)[0]).suffix.lower() in FIGURE_EXTS]
        required_nonfig_outputs = [
            item for item in outputs
            if item not in required_figures and "#" not in item
        ]

        declared_outputs = set()
        for key in ("tables", "figures", "artifacts", "outputs"):
            for item in flatten_strings(result_entry.get(key)):
                declared_outputs.update(canonical_ref_keys(root, item))

        data_sources = set()
        for item in flatten_strings(result_entry.get("data_sources")):
            data_sources.update(canonical_ref_keys(root, item))

        for required_input in flatten_strings(contract_entry.get("inputs")):
            normalized_required_inputs = canonical_ref_keys(root, required_input)
            if "#" in required_input:
                ref_file, _, ref_id = required_input.partition("#")
                if canonical_ref_keys(root, ref_file) == canonical_ref_keys(root, "results/all_results.json") and ref_id:
                    if ref_id not in result_map:
                        reporter.fail(
                            f"[{sub_id}] upstream dependency does not exist in all_results.json: {required_input}"
                        )
                if not normalized_required_inputs.intersection(data_sources):
                    reporter.fail(f"[{sub_id}] data_sources missing contract dependency: {required_input}")
            else:
                if not normalized_required_inputs.intersection(data_sources):
                    reporter.fail(f"[{sub_id}] data_sources missing contract input: {required_input}")

        key_metrics = flatten_strings(contract_entry.get("key_metrics"))
        if key_metrics:
            if not isinstance(metrics, dict) or not metrics:
                reporter.fail(f"[{sub_id}] missing metrics dictionary")
            else:
                for metric_name in key_metrics:
                    candidates = metric_candidates(metric_name, contract_entry, result_entry)
                    if not any(candidate in metrics for candidate in candidates):
                        reporter.fail(
                            f"[{sub_id}] missing key metric '{metric_name}'"
                            f" (allow by metric_aliases if renamed)"
                        )
        elif metrics is not None and not isinstance(metrics, dict):
            reporter.fail(f"[{sub_id}] metrics must be a dictionary when present")

        own_ref_keys = canonical_ref_keys(root, f"results/all_results.json#{sub_id}")
        contract_output_ref_keys = set()
        for item in outputs:
            contract_output_ref_keys.update(canonical_ref_keys(root, item))
        if not own_ref_keys.intersection(contract_output_ref_keys):
            reporter.warn(f"[{sub_id}] contract outputs do not include self all_results ref")

        for expected_output in required_nonfig_outputs:
            output_path_keys = canonical_path_keys(root, expected_output)
            if not any(Path(path_key).exists() for path_key in output_path_keys):
                reporter.fail(f"[{sub_id}] missing required output file: {expected_output}")
            output_ref_keys = canonical_ref_keys(root, expected_output)
            if not output_ref_keys.intersection(declared_outputs):
                reporter.fail(f"[{sub_id}] required output not declared in result entry: {expected_output}")

        for expected_figure in required_figures:
            figure_path_keys = canonical_path_keys(root, expected_figure)
            if not any(Path(path_key).exists() for path_key in figure_path_keys):
                reporter.fail(f"[{sub_id}] missing required figure file: {expected_figure}")
            figure_ref_keys = canonical_ref_keys(root, expected_figure)
            if not figure_ref_keys.intersection(declared_outputs):
                reporter.fail(f"[{sub_id}] required figure not declared in result entry: {expected_figure}")
            manifest_entry = next(
                (manifest_by_path[key] for key in figure_path_keys if key in manifest_by_path),
                None,
            )
            if not manifest_entry:
                reporter.fail(f"[{sub_id}] required figure missing from figure_manifest.json: {expected_figure}")
            else:
                source = str(manifest_entry.get("source", "")).strip()
                if sub_id not in source:
                    reporter.warn(
                        f"[{sub_id}] manifest source does not clearly point back to the subproblem: {expected_figure}"
                    )

        if not required_figures and not flatten_strings(result_entry.get("figures")):
            figure_absence_reason = str(result_entry.get("figure_absence_reason", "")).strip()
            has_metric_evidence = isinstance(metrics, dict) and bool(metrics)
            if not has_metric_evidence and not has_structured_evidence(result_entry):
                reporter.fail(
                    f"[{sub_id}] no contract-required figure, but no alternate evidence carrier was recorded"
                )
            if not figure_absence_reason:
                reporter.fail(
                    f"[{sub_id}] no contract-required figure, but figure_absence_reason is missing"
                )

        if not has_validation(result_entry):
            reporter.fail(f"[{sub_id}] missing validation evidence")

        reproduce_command = str(result_entry.get("reproduce_command", "")).strip()
        if not reproduce_command:
            fallback = ""
            if isinstance(result_data, dict):
                metadata = result_data.get("metadata")
                if isinstance(metadata, dict):
                    fallback = str(metadata.get("reproduce_command", "")).strip()
            if not fallback:
                reporter.fail(f"[{sub_id}] missing reproduce_command")

    if main_file.exists():
        try:
            typst_files = extract_typst_files(paper_dir, main_file, sections_dir)
            for owner, raw_ref in extract_image_paths(typst_files):
                if Path(raw_ref).suffix.lower() not in FIGURE_EXTS:
                    continue
                resolved_keys = canonical_path_keys(root, raw_ref, base_dir=owner.parent)
                if not any(key in manifest_by_path for key in resolved_keys):
                    reporter.fail(
                        f"paper figure not registered in figure_manifest.json: {raw_ref} "
                        f"(from {owner.name})"
                    )
        except UnicodeDecodeError as exc:
            reporter.fail(f"cannot decode paper body as utf-8: {exc}")
    else:
        reporter.warn(
            "paper main file not found, skip paper-body manifest closure: "
            f"{best_effort_relative(root, main_file)}"
        )

    if reporter.failures:
        print("FAIL: contract closure gate failed")
    elif reporter.warnings:
        print("PASS: contract closure gate passed with warnings")
    else:
        print("PASS: contract closure gate passed")
    return reporter.exit_code


if __name__ == "__main__":
    sys.exit(main())
