#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "score_evaluation.py"
TESTDATA = ROOT / "scripts" / "testdata"
DEFAULT_TMP_VERIFY = Path("E:/codex/_tmp_skill_verify")
PROJECTION_KEYS = ("review_mode", "quality_blocked", "submission_blocked", "overall_verdict")

VERIFIED_CASES = (
    {
        "label": "formal compliance-blocked",
        "input": "valid_paper_evaluation.json",
        "tmp_output": "valid.out.json",
        "expected": {
            "review_mode": "formal",
            "quality_blocked": False,
            "submission_blocked": True,
            "overall_verdict": "BLOCKED_COMPLIANCE",
        },
    },
    {
        "label": "formal quality-blocked",
        "input": "regression_task_coverage_insufficient.json",
        "tmp_output": "regression_insufficient.out.json",
        "expected": {
            "review_mode": "formal",
            "quality_blocked": True,
            "submission_blocked": True,
            "overall_verdict": "BLOCKED_QUALITY",
        },
    },
)

INVALID_CASES = (
    {
        "label": "missing task_coverage",
        "input": "invalid_missing_task_coverage.json",
        "tmp_error": "invalid_missing_task_coverage.err.txt",
        "expected_error": "task_coverage",
    },
    {
        "label": "summary cannot fake body evidence",
        "input": "invalid_summary_as_body_evidence.json",
        "tmp_error": "invalid_summary_as_body_evidence.err.txt",
        "expected_error": "不能只引用摘要/总述/abstract/summary-sheet 等非正文定位",
    },
    {
        "label": "validated needs validation semantics",
        "input": "invalid_validated_without_validation_semantics.json",
        "tmp_error": "invalid_validated_without_validation_semantics.err.txt",
        "expected_error": "必须显式标记 validation/robustness/sensitivity/backtest/error/constraint-check",
    },
)

COMPATIBILITY_ONLY = {
    "review_mode": ("preliminary",),
    "submission_blocked": (
        "false",
        "true via preliminary-only trigger",
    ),
    "overall_verdict": (
        "BLOCKED_COMPLIANCE_AND_QUALITY",
        "PRELIMINARY",
        "REVIEWED",
    ),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="核对 evaluate-math-modeling-paper 当前已验证 / 兼容保留边界。"
    )
    parser.add_argument(
        "--tmp-skill-verify",
        type=Path,
        default=DEFAULT_TMP_VERIFY,
        help="只读验证产物目录；默认读取 E:/codex/_tmp_skill_verify",
    )
    return parser.parse_args()


def run_score(input_path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(input_path)],
        check=False,
        text=True,
        encoding="utf-8",
        capture_output=True,
    )


def load_text(path: Path) -> str:
    raw = path.read_bytes()
    for encoding in ("utf-8", "utf-8-sig", "utf-16", "utf-16-le", "gb18030"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError("decode", raw, 0, 1, f"无法识别文件编码: {path}")


def ensure_tmp_verify_dir(tmp_dir: Path) -> None:
    if not tmp_dir.exists():
        raise AssertionError(f"_tmp_skill_verify 目录不存在: {tmp_dir}")
    if not tmp_dir.is_dir():
        raise AssertionError(f"_tmp_skill_verify 路径不是目录: {tmp_dir}")


def assert_projection(payload: dict[str, object], expected: dict[str, object], label: str) -> None:
    actual = {key: payload.get(key) for key in expected}
    if actual != expected:
        raise AssertionError(f"{label} 投影不匹配: expected={expected}, actual={actual}")


def verify_verified_cases(tmp_dir: Path) -> list[str]:
    results: list[str] = []
    for case in VERIFIED_CASES:
        input_path = TESTDATA / case["input"]
        completed = run_score(input_path)
        if completed.returncode != 0:
            raise AssertionError(
                f"{case['label']} 运行失败: returncode={completed.returncode}, stderr={completed.stderr.strip()}"
            )

        payload = json.loads(completed.stdout)
        assert_projection(payload, case["expected"], case["label"])

        tmp_output = tmp_dir / case["tmp_output"]
        if not tmp_output.exists():
            raise AssertionError(f"{case['label']} baseline 缺失: {tmp_output}")
        baseline = json.loads(load_text(tmp_output))
        assert_projection(baseline, case["expected"], f"{case['label']} baseline")

        results.append(
            f"{case['label']}: "
            f"review_mode={case['expected']['review_mode']}, "
            f"quality_blocked={str(case['expected']['quality_blocked']).lower()}, "
            f"submission_blocked={str(case['expected']['submission_blocked']).lower()}, "
            f"overall_verdict={case['expected']['overall_verdict']}"
        )
    return results


def verify_invalid_cases(tmp_dir: Path) -> list[str]:
    results: list[str] = []
    for case in INVALID_CASES:
        input_path = TESTDATA / case["input"]
        completed = run_score(input_path)
        combined_output = "\n".join(
            part for part in (completed.stdout.strip(), completed.stderr.strip()) if part
        )
        if completed.returncode == 0:
            raise AssertionError(f"{case['label']} 应失败但返回成功")
        if case["expected_error"] not in combined_output:
            raise AssertionError(
                f"{case['label']} 未命中期望错误片段: {case['expected_error']}"
            )

        tmp_error = tmp_dir / case["tmp_error"]
        if not tmp_error.exists():
            raise AssertionError(f"{case['label']} baseline 缺失: {tmp_error}")
        baseline_text = load_text(tmp_error)
        if case["expected_error"] not in baseline_text:
            raise AssertionError(
                f"{case['label']} baseline 未命中期望错误片段: {case['expected_error']}"
            )

        results.append(f"{case['label']}: {case['expected_error']}")
    return results


def verify_tmp_success_projection_boundary(tmp_dir: Path) -> list[str]:
    expected_projections = {
        tuple(case["expected"][key] for key in PROJECTION_KEYS) for case in VERIFIED_CASES
    }
    observed: list[str] = []

    for tmp_output in sorted(tmp_dir.glob("*.out.json")):
        if tmp_output.stat().st_size == 0:
            continue

        payload = json.loads(load_text(tmp_output))
        projection = {key: payload.get(key) for key in PROJECTION_KEYS}
        projection_key = tuple(projection[key] for key in PROJECTION_KEYS)
        if projection_key not in expected_projections:
            raise AssertionError(
                "发现超出已验证边界的成功产物: "
                f"{tmp_output.name} -> {projection}"
            )

        observed.append(
            f"{tmp_output.name}: "
            f"review_mode={projection['review_mode']}, "
            f"quality_blocked={str(projection['quality_blocked']).lower()}, "
            f"submission_blocked={str(projection['submission_blocked']).lower()}, "
            f"overall_verdict={projection['overall_verdict']}"
        )

    if not observed:
        raise AssertionError(f"_tmp_skill_verify 缺少可用的成功基线: {tmp_dir}")
    return observed


def main() -> int:
    args = parse_args()
    ensure_tmp_verify_dir(args.tmp_skill_verify)
    verified = verify_verified_cases(args.tmp_skill_verify)
    invalid = verify_invalid_cases(args.tmp_skill_verify)
    observed_success = verify_tmp_success_projection_boundary(args.tmp_skill_verify)

    print("verified_branch_projection:")
    for line in verified:
        print(f"- {line}")

    print("tmp_success_projection_boundary:")
    for line in observed_success:
        print(f"- {line}")

    print("verified_rejection_projection:")
    for line in invalid:
        print(f"- {line}")

    print("compatibility_only_boundary:")
    for field, values in COMPATIBILITY_ONLY.items():
        print(f"- {field}: {', '.join(values)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
