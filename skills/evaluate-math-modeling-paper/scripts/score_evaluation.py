#!/usr/bin/env python3
"""校验 paper_evaluation.json 并计算综合分数。"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any


DIMENSION_WEIGHTS = {
    "summary_and_task_coverage": 10,
    "problem_understanding": 10,
    "assumptions_data_variables_units": 10,
    "model_and_mathematical_correctness": 20,
    "computation_and_reproducibility": 10,
    "results_and_interpretation": 15,
    "validation_sensitivity_robustness": 10,
    "limitations_applicability_improvement": 5,
    "writing_organization_figures_citations": 5,
    "innovation_and_insight": 5,
}

SOURCE_CATEGORIES = {
    "official_rule",
    "official_guidance",
    "educational_rubric",
    "user_provided_current_rule",
}
EVIDENCE_STATES = {"complete", "partial", "minimal", "missing", "unknown"}
OFFICIAL_STATUSES = {"PASS", "FAIL", "UNKNOWN"}
ISSUE_SEVERITIES = {"BLOCKER", "MAJOR", "MINOR"}
CONFIDENCE_LEVELS = {"low", "medium", "high"}
RULE_SOURCE_CATEGORIES = {
    "official_rule",
    "official_guidance",
    "user_provided_current_rule",
}
EVIDENCE_REF_PATTERN = re.compile(r"^[a-z][a-z0-9_-]*:[^\s]+$")


class ValidationError(Exception):
    """输入不满足契约时抛出。"""


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def ensure_type(value: Any, expected_type: type, path: str) -> None:
    ensure(isinstance(value, expected_type), f"{path} 必须是 {expected_type.__name__}")


def non_empty_string(value: Any, path: str) -> str:
    ensure_type(value, str, path)
    text = value.strip()
    ensure(bool(text), f"{path} 不能为空")
    return text


def validate_date(value: Any, path: str) -> str:
    text = non_empty_string(value, path)
    try:
        date.fromisoformat(text)
    except ValueError as exc:
        raise ValidationError(f"{path} 必须是 YYYY-MM-DD") from exc
    return text


def validate_string_list(value: Any, path: str) -> list[str]:
    ensure_type(value, list, path)
    items: list[str] = []
    for index, item in enumerate(value):
        items.append(non_empty_string(item, f"{path}[{index}]"))
    ensure(bool(items), f"{path} 不能为空")
    return items


def validate_optional_string_list(value: Any, path: str) -> list[str]:
    if value is None:
        return []
    ensure_type(value, list, path)
    items: list[str] = []
    for index, item in enumerate(value):
        items.append(non_empty_string(item, f"{path}[{index}]"))
    return items


def validate_source_ids(source_ids: list[str], known_source_ids: set[str], path: str) -> None:
    for source_id in source_ids:
        ensure(source_id in known_source_ids, f"{path} 引用了未知 source_id: {source_id}")


def validate_evidence_refs(value: Any, path: str) -> list[str]:
    refs = validate_string_list(value, path)
    for ref in refs:
        ensure(
            bool(EVIDENCE_REF_PATTERN.match(ref)),
            f"{path} 存在非法 evidence_ref: {ref}",
        )
    return refs


def validate_rule_source_ids(
    source_ids: list[str],
    known_source_ids: set[str],
    source_categories: dict[str, str],
    path: str,
) -> None:
    validate_source_ids(source_ids, known_source_ids, path)
    for source_id in source_ids:
        category = source_categories[source_id]
        ensure(
            category in RULE_SOURCE_CATEGORIES,
            f"{path} 只能引用官方或用户提供的当前规则来源: {source_id}",
        )


def validate_sources(payload: dict[str, Any]) -> dict[str, str]:
    sources = payload.get("sources")
    ensure_type(sources, list, "sources")
    ensure(bool(sources), "sources 不能为空")

    source_categories: dict[str, str] = {}
    for index, source in enumerate(sources):
        path = f"sources[{index}]"
        ensure_type(source, dict, path)
        source_id = non_empty_string(source.get("id"), f"{path}.id")
        ensure(source_id not in source_categories, f"{path}.id 重复: {source_id}")
        non_empty_string(source.get("title"), f"{path}.title")
        non_empty_string(source.get("authority"), f"{path}.authority")
        non_empty_string(source.get("url"), f"{path}.url")
        category = non_empty_string(source.get("category"), f"{path}.category")
        ensure(category in SOURCE_CATEGORIES, f"{path}.category 非法: {category}")
        source_categories[source_id] = category
    return source_categories


def validate_competition_profile(payload: dict[str, Any]) -> None:
    profile = payload.get("competition_profile")
    ensure_type(profile, dict, "competition_profile")
    non_empty_string(profile.get("profile_id"), "competition_profile.profile_id")
    non_empty_string(profile.get("competition"), "competition_profile.competition")
    year = profile.get("year")
    ensure(isinstance(year, int) and year > 0, "competition_profile.year 必须是正整数")
    non_empty_string(profile.get("rule_mode"), "competition_profile.rule_mode")


def validate_evidence_completeness(payload: dict[str, Any]) -> None:
    block = payload.get("evidence_completeness")
    ensure_type(block, dict, "evidence_completeness")
    for key in ("paper", "problem", "results", "code", "attachments"):
        state = non_empty_string(block.get(key), f"evidence_completeness.{key}")
        ensure(state in EVIDENCE_STATES, f"evidence_completeness.{key} 非法: {state}")
    non_empty_string(block.get("notes"), "evidence_completeness.notes")


def validate_official_compliance(
    payload: dict[str, Any],
    known_source_ids: set[str],
    source_categories: dict[str, str],
) -> tuple[str, bool]:
    block = payload.get("official_compliance")
    ensure_type(block, dict, "official_compliance")
    checks = block.get("checks")
    ensure_type(checks, list, "official_compliance.checks")
    ensure(bool(checks), "official_compliance.checks 不能为空")

    seen_ids: set[str] = set()
    statuses: list[str] = []
    for index, check in enumerate(checks):
        path = f"official_compliance.checks[{index}]"
        ensure_type(check, dict, path)
        check_id = non_empty_string(check.get("id"), f"{path}.id")
        ensure(check_id not in seen_ids, f"{path}.id 重复: {check_id}")
        seen_ids.add(check_id)
        non_empty_string(check.get("label"), f"{path}.label")
        status = non_empty_string(check.get("status"), f"{path}.status")
        ensure(status in OFFICIAL_STATUSES, f"{path}.status 非法: {status}")
        statuses.append(status)
        rule_source_ids = validate_string_list(check.get("rule_source_ids"), f"{path}.rule_source_ids")
        validate_rule_source_ids(
            rule_source_ids,
            known_source_ids,
            source_categories,
            f"{path}.rule_source_ids",
        )
        validate_evidence_refs(check.get("evidence_refs"), f"{path}.evidence_refs")
        non_empty_string(check.get("notes"), f"{path}.notes")

    overall = "PASS"
    if "FAIL" in statuses:
        overall = "FAIL"
    elif "UNKNOWN" in statuses:
        overall = "UNKNOWN"

    block["overall"] = overall
    block["compliance_blocked"] = overall == "FAIL"
    return overall, overall == "FAIL"


def validate_quality_blockers(payload: dict[str, Any], known_source_ids: set[str]) -> None:
    blockers = payload.get("quality_blockers")
    ensure_type(blockers, list, "quality_blockers")
    seen_ids: set[str] = set()
    for index, blocker in enumerate(blockers):
        path = f"quality_blockers[{index}]"
        ensure_type(blocker, dict, path)
        blocker_id = non_empty_string(blocker.get("id"), f"{path}.id")
        ensure(blocker_id not in seen_ids, f"{path}.id 重复: {blocker_id}")
        seen_ids.add(blocker_id)
        severity = non_empty_string(blocker.get("severity"), f"{path}.severity")
        ensure(severity in ISSUE_SEVERITIES, f"{path}.severity 非法: {severity}")
        non_empty_string(blocker.get("summary"), f"{path}.summary")
        dimension_ids = validate_optional_string_list(blocker.get("dimension_ids"), f"{path}.dimension_ids")
        for dimension_id in dimension_ids:
            ensure(dimension_id in DIMENSION_WEIGHTS, f"{path}.dimension_ids 引用了未知维度: {dimension_id}")
        validate_evidence_refs(blocker.get("evidence_refs"), f"{path}.evidence_refs")
        source_ids = validate_optional_string_list(blocker.get("source_ids"), f"{path}.source_ids")
        validate_source_ids(source_ids, known_source_ids, f"{path}.source_ids")


def validate_dimension_scores(payload: dict[str, Any], known_source_ids: set[str]) -> tuple[int, float]:
    scores = payload.get("dimension_scores")
    ensure_type(scores, dict, "dimension_scores")

    expected_ids = set(DIMENSION_WEIGHTS)
    actual_ids = set(scores)
    missing = sorted(expected_ids - actual_ids)
    extra = sorted(actual_ids - expected_ids)
    ensure(not missing, f"dimension_scores 缺少维度: {', '.join(missing)}")
    ensure(not extra, f"dimension_scores 存在未知维度: {', '.join(extra)}")

    assessed_weight = 0
    total_points = 0.0

    for dimension_id, weight in DIMENSION_WEIGHTS.items():
        item = scores.get(dimension_id)
        path = f"dimension_scores.{dimension_id}"
        ensure_type(item, dict, path)
        actual_weight = item.get("weight")
        ensure(actual_weight == weight, f"{path}.weight 必须等于 {weight}")
        rating = item.get("rating")
        if isinstance(rating, bool):
            raise ValidationError(f"{path}.rating 不能是布尔值")
        if isinstance(rating, int):
            ensure(0 <= rating <= 5, f"{path}.rating 必须在 0 到 5 之间")
            points = round(weight * rating / 5.0, 2)
            assessed_weight += weight
            total_points += points
            item["points_awarded"] = points
        else:
            rating_text = non_empty_string(rating, f"{path}.rating")
            ensure(rating_text == "NOT_ASSESSABLE", f"{path}.rating 非法: {rating_text}")
            item["points_awarded"] = None
        non_empty_string(item.get("rationale"), f"{path}.rationale")
        validate_evidence_refs(item.get("evidence_refs"), f"{path}.evidence_refs")
        source_ids = validate_optional_string_list(item.get("source_ids"), f"{path}.source_ids")
        validate_source_ids(source_ids, known_source_ids, f"{path}.source_ids")

    return assessed_weight, round(total_points, 2)


def validate_confidence(payload: dict[str, Any]) -> None:
    confidence = payload.get("confidence")
    ensure_type(confidence, dict, "confidence")
    level = non_empty_string(confidence.get("level"), "confidence.level")
    ensure(level in CONFIDENCE_LEVELS, f"confidence.level 非法: {level}")
    non_empty_string(confidence.get("notes"), "confidence.notes")
    validate_evidence_refs(confidence.get("evidence_refs"), "confidence.evidence_refs")


def validate_priority_fixes(payload: dict[str, Any], known_source_ids: set[str]) -> None:
    fixes = payload.get("priority_fixes")
    ensure_type(fixes, list, "priority_fixes")
    seen_ids: set[str] = set()
    for index, fix in enumerate(fixes):
        path = f"priority_fixes[{index}]"
        ensure_type(fix, dict, path)
        fix_id = non_empty_string(fix.get("id"), f"{path}.id")
        ensure(fix_id not in seen_ids, f"{path}.id 重复: {fix_id}")
        seen_ids.add(fix_id)
        priority = fix.get("priority")
        ensure(isinstance(priority, int) and 1 <= priority <= 3, f"{path}.priority 必须是 1 到 3 的整数")
        non_empty_string(fix.get("title"), f"{path}.title")
        severity = non_empty_string(fix.get("severity"), f"{path}.severity")
        ensure(severity in ISSUE_SEVERITIES, f"{path}.severity 非法: {severity}")
        non_empty_string(fix.get("expected_gain"), f"{path}.expected_gain")
        validate_evidence_refs(fix.get("evidence_refs"), f"{path}.evidence_refs")
        source_ids = validate_optional_string_list(fix.get("source_ids"), f"{path}.source_ids")
        validate_source_ids(source_ids, known_source_ids, f"{path}.source_ids")
        related_dimensions = validate_optional_string_list(fix.get("related_dimensions"), f"{path}.related_dimensions")
        for dimension_id in related_dimensions:
            ensure(dimension_id in DIMENSION_WEIGHTS, f"{path}.related_dimensions 引用了未知维度: {dimension_id}")


def compute_scores(payload: dict[str, Any], assessed_weight: int, total_points: float) -> None:
    payload["assessed_weight"] = assessed_weight
    score_coverage = round(assessed_weight / 100.0, 4)
    payload["score_coverage"] = score_coverage
    payload.pop("provisional_score", None)
    payload.pop("final_score", None)
    if assessed_weight == 100:
        payload["final_score"] = total_points
    else:
        payload["provisional_score"] = total_points


def load_payload(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValidationError(f"输入文件不存在: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"JSON 解析失败: {exc}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and score paper_evaluation.json")
    parser.add_argument("json_path", help="待校验的 JSON 文件路径")
    args = parser.parse_args()

    payload = load_payload(Path(args.json_path))
    ensure_type(payload, dict, "root")

    validate_competition_profile(payload)
    validate_date(payload.get("retrieval_date"), "retrieval_date")
    source_categories = validate_sources(payload)
    known_source_ids = set(source_categories)
    validate_evidence_completeness(payload)
    validate_official_compliance(payload, known_source_ids, source_categories)
    validate_quality_blockers(payload, known_source_ids)
    assessed_weight, total_points = validate_dimension_scores(payload, known_source_ids)
    validate_confidence(payload)
    validate_priority_fixes(payload, known_source_ids)
    compute_scores(payload, assessed_weight, total_points)

    sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValidationError as exc:
        sys.stderr.write(str(exc) + "\n")
        raise SystemExit(1)
