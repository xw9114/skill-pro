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
SOURCE_MODES = {"url", "user_file", "manual_note"}
REVIEW_MODES = {"formal", "preliminary"}
EVIDENCE_STATES = {"complete", "partial", "minimal", "missing", "unknown"}
TASK_STATUSES = ("mentioned", "answered", "evidenced", "validated")
TASK_STATUS_ORDER = {status: index for index, status in enumerate(TASK_STATUSES)}
OFFICIAL_STATUSES = {"PASS", "FAIL", "UNKNOWN"}
ISSUE_SEVERITIES = {"BLOCKER", "MAJOR", "MINOR"}
CONFIDENCE_LEVELS = {"low", "medium", "high"}
OVERALL_VERDICTS = {
    "BLOCKED_COMPLIANCE_AND_QUALITY",
    "BLOCKED_COMPLIANCE",
    "BLOCKED_QUALITY",
    "PRELIMINARY",
    "REVIEWED",
}
RULE_SOURCE_CATEGORIES = {
    "official_rule",
    "official_guidance",
    "user_provided_current_rule",
}
EVIDENCE_REF_PATTERN = re.compile(r"^[a-z][a-z0-9_-]*:[^\s]+$")
EVIDENCE_FAMILIES = {"paper", "problem", "results", "code", "attachments"}
EVIDENCE_FAMILY_ALIASES = {"attachment": "attachments"}
SUMMARY_LOCATOR_MARKERS = (
    "abstract",
    "summary",
    "summary sheet",
    "executive summary",
    "摘要",
    "总述",
    "概述",
)
VALIDATION_LOCATOR_MARKERS = (
    "validation",
    "validate",
    "verification",
    "verify",
    "robustness",
    "robust",
    "sensitivity",
    "backtest",
    "error",
    "constraint check",
    "constraint validation",
    "constraint verify",
    "ablation",
    "residual",
    "feasibility check",
    "验证",
    "稳健",
    "敏感性",
    "回测",
    "误差",
    "约束检查",
    "约束校验",
    "约束验证",
    "可行性检查",
    "检验",
    "对比",
)


class ValidationError(Exception):
    """输入不满足契约时抛出。"""


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def ensure_type(value: Any, expected_type: type, path: str) -> None:
    ensure(isinstance(value, expected_type), f"{path} 必须是 {expected_type.__name__}")


def ensure_bool(value: Any, path: str) -> bool:
    ensure(type(value) is bool, f"{path} 必须是 bool")
    return value


def ensure_positive_int(value: Any, path: str) -> int:
    ensure(type(value) is int and value > 0, f"{path} 必须是正整数")
    return value


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


def validate_optional_string(value: Any, path: str) -> str | None:
    if value is None:
        return None
    return non_empty_string(value, path)


def validate_year_or_text(value: Any, path: str) -> int | str:
    if type(value) is int:
        ensure(value > 0, f"{path} 必须是正整数或非空字符串")
        return value
    return non_empty_string(value, path)


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


def validate_evidence_ref_list(value: Any, path: str, *, allow_empty: bool) -> list[str]:
    ensure_type(value, list, path)
    refs: list[str] = []
    for index, item in enumerate(value):
        ref = non_empty_string(item, f"{path}[{index}]")
        ensure(
            bool(EVIDENCE_REF_PATTERN.match(ref)),
            f"{path} 存在非法 evidence_ref: {ref}",
        )
        refs.append(ref)
    if not allow_empty:
        ensure(bool(refs), f"{path} 不能为空")
    return refs


def collect_evidence_refs(value: Any) -> list[str]:
    refs: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "evidence_refs" and isinstance(child, list):
                refs.extend(item for item in child if isinstance(item, str))
            else:
                refs.extend(collect_evidence_refs(child))
    elif isinstance(value, list):
        for child in value:
            refs.extend(collect_evidence_refs(child))
    return refs


def split_evidence_ref(ref: str) -> tuple[str, str]:
    family, value = ref.split(":", 1)
    return EVIDENCE_FAMILY_ALIASES.get(family, family), value


def normalize_locator(locator: str) -> tuple[str, str]:
    normalized = re.sub(r"[_./#-]+", " ", locator.lower())
    compact = normalized.replace(" ", "")
    return normalized, compact


def locator_has_marker(locator: str, markers: tuple[str, ...]) -> bool:
    normalized, compact = normalize_locator(locator)
    for marker in markers:
        marker_normalized, marker_compact = normalize_locator(marker)
        if marker_normalized in normalized or marker_compact in compact:
            return True
    return False


def is_summary_only_paper_ref(ref: str) -> bool:
    family, value = split_evidence_ref(ref)
    if family != "paper":
        return False
    return locator_has_marker(value, SUMMARY_LOCATOR_MARKERS)


def has_non_summary_paper_ref(refs: list[str]) -> bool:
    return any(ref.startswith("paper:") and not is_summary_only_paper_ref(ref) for ref in refs)


def is_body_evidence_ref(ref: str) -> bool:
    family, _value = split_evidence_ref(ref)
    if family != "paper":
        return True
    return not is_summary_only_paper_ref(ref)


def is_validation_evidence_ref(ref: str) -> bool:
    _family, value = split_evidence_ref(ref)
    return locator_has_marker(value, VALIDATION_LOCATOR_MARKERS)


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
        source_mode = non_empty_string(source.get("source_mode"), f"{path}.source_mode")
        ensure(source_mode in SOURCE_MODES, f"{path}.source_mode 非法: {source_mode}")
        if source_mode == "url":
            non_empty_string(source.get("url"), f"{path}.url")
        else:
            if source.get("url") not in (None, ""):
                validate_optional_string(source.get("url"), f"{path}.url")
        if source_mode == "user_file":
            non_empty_string(source.get("local_path"), f"{path}.local_path")
            validate_optional_string(source.get("sha256"), f"{path}.sha256")
        elif "local_path" in source:
            validate_optional_string(source.get("local_path"), f"{path}.local_path")
        if source_mode == "manual_note":
            non_empty_string(source.get("notes"), f"{path}.notes")
        category = non_empty_string(source.get("category"), f"{path}.category")
        ensure(category in SOURCE_CATEGORIES, f"{path}.category 非法: {category}")
        non_empty_string(source.get("document_version"), f"{path}.document_version")
        validate_year_or_text(source.get("applies_to_year"), f"{path}.applies_to_year")
        validate_date(source.get("retrieved_at"), f"{path}.retrieved_at")
        source_categories[source_id] = category
    return source_categories


def validate_review_mode(payload: dict[str, Any]) -> str:
    review_mode = non_empty_string(payload.get("review_mode"), "review_mode")
    ensure(review_mode in REVIEW_MODES, f"review_mode 非法: {review_mode}")
    return review_mode


def validate_rubric(payload: dict[str, Any]) -> None:
    rubric = payload.get("rubric")
    ensure_type(rubric, dict, "rubric")
    non_empty_string(rubric.get("id"), "rubric.id")
    non_empty_string(rubric.get("origin"), "rubric.origin")
    ensure_bool(rubric.get("official_weight_available"), "rubric.official_weight_available")


def validate_artifacts(payload: dict[str, Any]) -> None:
    artifacts = payload.get("artifacts")
    ensure_type(artifacts, list, "artifacts")
    ensure(bool(artifacts), "artifacts 不能为空")
    seen_ids: set[str] = set()
    seen_kinds: set[str] = set()
    for index, artifact in enumerate(artifacts):
        path = f"artifacts[{index}]"
        ensure_type(artifact, dict, path)
        artifact_id = non_empty_string(artifact.get("id"), f"{path}.id")
        ensure(artifact_id not in seen_ids, f"{path}.id 重复: {artifact_id}")
        seen_ids.add(artifact_id)
        kind = non_empty_string(artifact.get("kind"), f"{path}.kind")
        ensure(kind in EVIDENCE_FAMILIES, f"{path}.kind 非法: {kind}")
        seen_kinds.add(kind)
        status = non_empty_string(artifact.get("status"), f"{path}.status")
        ensure(status in EVIDENCE_STATES, f"{path}.status 非法: {status}")
        validate_optional_string(artifact.get("path"), f"{path}.path")
        validate_optional_string(artifact.get("url"), f"{path}.url")
        validate_optional_string(artifact.get("sha256"), f"{path}.sha256")
        non_empty_string(artifact.get("notes"), f"{path}.notes")
    missing_kinds = sorted(EVIDENCE_FAMILIES - seen_kinds)
    ensure(not missing_kinds, f"artifacts 缺少工件状态记录: {', '.join(missing_kinds)}")


def validate_competition_profile(payload: dict[str, Any]) -> None:
    profile = payload.get("competition_profile")
    ensure_type(profile, dict, "competition_profile")
    non_empty_string(profile.get("profile_id"), "competition_profile.profile_id")
    non_empty_string(profile.get("competition"), "competition_profile.competition")
    ensure_positive_int(profile.get("year"), "competition_profile.year")
    non_empty_string(profile.get("rule_mode"), "competition_profile.rule_mode")


def validate_evidence_completeness(payload: dict[str, Any]) -> None:
    block = payload.get("evidence_completeness")
    ensure_type(block, dict, "evidence_completeness")
    for key in ("paper", "problem", "results", "code", "attachments"):
        state = non_empty_string(block.get(key), f"evidence_completeness.{key}")
        ensure(state in EVIDENCE_STATES, f"evidence_completeness.{key} 非法: {state}")
    non_empty_string(block.get("notes"), "evidence_completeness.notes")


def validate_task_coverage(payload: dict[str, Any]) -> list[str]:
    items = payload.get("task_coverage")
    ensure_type(items, list, "task_coverage")
    ensure(bool(items), "task_coverage 不能为空")

    seen_ids: set[str] = set()
    seen_problem_refs: set[str] = set()
    statuses: list[str] = []

    for index, item in enumerate(items):
        path = f"task_coverage[{index}]"
        ensure_type(item, dict, path)
        task_id = non_empty_string(item.get("task_id"), f"{path}.task_id")
        ensure(task_id not in seen_ids, f"{path}.task_id 重复: {task_id}")
        seen_ids.add(task_id)
        non_empty_string(item.get("task_label"), f"{path}.task_label")
        status = non_empty_string(item.get("status"), f"{path}.status")
        ensure(status in TASK_STATUS_ORDER, f"{path}.status 非法: {status}")
        statuses.append(status)
        problem_ref = non_empty_string(item.get("problem_ref"), f"{path}.problem_ref")
        ensure(problem_ref.startswith("problem:"), f"{path}.problem_ref 必须引用题面任务")
        ensure(bool(EVIDENCE_REF_PATTERN.match(problem_ref)), f"{path}.problem_ref 非法: {problem_ref}")
        ensure(problem_ref not in seen_problem_refs, f"{path}.problem_ref 重复: {problem_ref}")
        seen_problem_refs.add(problem_ref)

        paper_refs = validate_string_list(item.get("paper_refs"), f"{path}.paper_refs")
        for ref in paper_refs:
            ensure(ref.startswith("paper:"), f"{path}.paper_refs 只能引用论文位置: {ref}")
            ensure(bool(EVIDENCE_REF_PATTERN.match(ref)), f"{path}.paper_refs 非法: {ref}")

        body_evidence_refs = validate_evidence_ref_list(
            item.get("body_evidence_refs"),
            f"{path}.body_evidence_refs",
            allow_empty=True,
        )
        validation_evidence_refs = validate_evidence_ref_list(
            item.get("validation_evidence_refs"),
            f"{path}.validation_evidence_refs",
            allow_empty=True,
        )
        evidence_refs = validate_evidence_ref_list(
            item.get("evidence_refs"),
            f"{path}.evidence_refs",
            allow_empty=True,
        )
        ensure(
            evidence_refs == body_evidence_refs + validation_evidence_refs,
            f"{path}.evidence_refs 必须按顺序等于 body_evidence_refs + validation_evidence_refs",
        )
        non_empty_string(item.get("notes"), f"{path}.notes")

        if status == "mentioned":
            ensure(not body_evidence_refs, f"{path}.status=mentioned 时 body_evidence_refs 必须为空")
            ensure(not validation_evidence_refs, f"{path}.status=mentioned 时 validation_evidence_refs 必须为空")
            ensure(not evidence_refs, f"{path}.status=mentioned 时 evidence_refs 必须为空")
            continue
        ensure(
            has_non_summary_paper_ref(paper_refs),
            f"{path}.status 至少为 answered 时，paper_refs 必须包含正文位置；摘要单独提及不算正文证据",
        )
        if status == "answered":
            ensure(not body_evidence_refs, f"{path}.status=answered 时 body_evidence_refs 必须为空")
            ensure(not validation_evidence_refs, f"{path}.status=answered 时 validation_evidence_refs 必须为空")
            ensure(not evidence_refs, f"{path}.status=answered 时 evidence_refs 必须为空")
            continue
        ensure(
            bool(body_evidence_refs),
            f"{path}.status 至少为 evidenced 时，body_evidence_refs 不能为空",
        )
        for ref in body_evidence_refs:
            ensure(
                is_body_evidence_ref(ref),
                f"{path}.body_evidence_refs 不能只引用摘要/总述/abstract/summary-sheet 等非正文定位: {ref}",
            )
        if status == "validated":
            ensure(
                bool(validation_evidence_refs),
                f"{path}.status=validated 时 validation_evidence_refs 不能为空",
            )
            for ref in validation_evidence_refs:
                ensure(
                    is_validation_evidence_ref(ref),
                    f"{path}.validation_evidence_refs 必须显式标记 validation/robustness/sensitivity/backtest/error/constraint-check 等验证语义: {ref}",
                )
        else:
            ensure(
                not validation_evidence_refs,
                f"{path}.status 低于 validated 时 validation_evidence_refs 必须为空",
            )

    return statuses


def validate_review_mode_consistency(payload: dict[str, Any], review_mode: str) -> None:
    if review_mode != "formal":
        return
    completeness = payload["evidence_completeness"]
    for family in ("paper", "problem"):
        state = completeness[family]
        ensure(
            state not in {"missing", "unknown"},
            f"review_mode=formal 时 evidence_completeness.{family} 不能是 {state}",
        )


def validate_evidence_consistency(payload: dict[str, Any]) -> None:
    completeness = payload["evidence_completeness"]
    refs = collect_evidence_refs(payload)
    for ref in refs:
        family, value = split_evidence_ref(ref)
        if family not in EVIDENCE_FAMILIES:
            continue
        if completeness.get(family) == "missing":
            ensure(
                value == "missing",
                f"evidence_refs 不能在 evidence_completeness.{family}=missing 时引用 {ref}",
            )


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


def validate_quality_blockers(payload: dict[str, Any], known_source_ids: set[str]) -> bool:
    blockers = payload.get("quality_blockers")
    ensure_type(blockers, list, "quality_blockers")
    seen_ids: set[str] = set()
    quality_blocked = False
    for index, blocker in enumerate(blockers):
        path = f"quality_blockers[{index}]"
        ensure_type(blocker, dict, path)
        blocker_id = non_empty_string(blocker.get("id"), f"{path}.id")
        ensure(blocker_id not in seen_ids, f"{path}.id 重复: {blocker_id}")
        seen_ids.add(blocker_id)
        severity = non_empty_string(blocker.get("severity"), f"{path}.severity")
        ensure(severity in ISSUE_SEVERITIES, f"{path}.severity 非法: {severity}")
        if severity == "BLOCKER":
            quality_blocked = True
        non_empty_string(blocker.get("summary"), f"{path}.summary")
        dimension_ids = validate_optional_string_list(blocker.get("dimension_ids"), f"{path}.dimension_ids")
        for dimension_id in dimension_ids:
            ensure(dimension_id in DIMENSION_WEIGHTS, f"{path}.dimension_ids 引用了未知维度: {dimension_id}")
        validate_evidence_refs(blocker.get("evidence_refs"), f"{path}.evidence_refs")
        source_ids = validate_optional_string_list(blocker.get("source_ids"), f"{path}.source_ids")
        validate_source_ids(source_ids, known_source_ids, f"{path}.source_ids")
    return quality_blocked


def cap_dimension_rating(scores: dict[str, Any], dimension_id: str, cap: int) -> None:
    item = scores.get(dimension_id)
    if not isinstance(item, dict):
        return
    rating = item.get("rating")
    if type(rating) is int and rating > cap:
        item["rating"] = cap


def apply_task_coverage_caps(payload: dict[str, Any], task_statuses: list[str]) -> bool:
    scores = payload.get("dimension_scores")
    ensure_type(scores, dict, "dimension_scores")

    if "mentioned" in task_statuses:
        cap_dimension_rating(scores, "results_and_interpretation", 1)
    elif "answered" in task_statuses:
        cap_dimension_rating(scores, "results_and_interpretation", 2)

    if any(status != "validated" for status in task_statuses):
        cap_dimension_rating(scores, "validation_sensitivity_robustness", 3)

    return any(TASK_STATUS_ORDER[status] < TASK_STATUS_ORDER["evidenced"] for status in task_statuses)


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
        ensure(type(priority) is int and 1 <= priority <= 3, f"{path}.priority 必须是 1 到 3 的整数")
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


def compute_scores(payload: dict[str, Any], assessed_weight: int, total_points: float, review_mode: str) -> None:
    payload["assessed_weight"] = assessed_weight
    score_coverage = round(assessed_weight / 100.0, 4)
    payload["score_coverage"] = score_coverage
    payload.pop("provisional_score", None)
    payload.pop("final_score", None)
    if review_mode == "formal" and assessed_weight == 100:
        payload["final_score"] = total_points
    else:
        payload["provisional_score"] = total_points


def compute_verdict(
    payload: dict[str, Any],
    review_mode: str,
    compliance_blocked: bool,
    quality_blocked: bool,
) -> None:
    payload["quality_blocked"] = quality_blocked
    payload["submission_blocked"] = compliance_blocked or quality_blocked or review_mode == "preliminary"
    if compliance_blocked and quality_blocked:
        verdict = "BLOCKED_COMPLIANCE_AND_QUALITY"
    elif compliance_blocked:
        verdict = "BLOCKED_COMPLIANCE"
    elif quality_blocked:
        verdict = "BLOCKED_QUALITY"
    elif review_mode == "preliminary":
        verdict = "PRELIMINARY"
    else:
        verdict = "REVIEWED"
    ensure(verdict in OVERALL_VERDICTS, f"overall_verdict 非法: {verdict}")
    payload["overall_verdict"] = verdict


def reject_json_constant(value: str) -> None:
    raise ValueError(f"JSON 不允许非有限数值: {value}")


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"JSON 存在重复 key: {key}")
        result[key] = value
    return result


def load_payload(path: Path) -> dict[str, Any]:
    try:
        text = path.read_bytes().decode("utf-8-sig")
        return json.loads(
            text,
            parse_constant=reject_json_constant,
            object_pairs_hook=reject_duplicate_keys,
        )
    except FileNotFoundError as exc:
        raise ValidationError(f"输入文件不存在: {path}") from exc
    except UnicodeDecodeError as exc:
        raise ValidationError(f"输入文件必须是 UTF-8 或 UTF-8 BOM 编码: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"JSON 解析失败: {exc}") from exc
    except ValueError as exc:
        raise ValidationError(str(exc)) from exc


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Validate and score paper_evaluation.json")
    parser.add_argument("json_path", help="待校验的 JSON 文件路径")
    args = parser.parse_args()

    payload = load_payload(Path(args.json_path))
    ensure_type(payload, dict, "root")

    review_mode = validate_review_mode(payload)
    validate_rubric(payload)
    validate_competition_profile(payload)
    validate_date(payload.get("retrieval_date"), "retrieval_date")
    source_categories = validate_sources(payload)
    known_source_ids = set(source_categories)
    validate_artifacts(payload)
    validate_evidence_completeness(payload)
    validate_review_mode_consistency(payload, review_mode)
    task_statuses = validate_task_coverage(payload)
    task_quality_blocked = apply_task_coverage_caps(payload, task_statuses)
    _overall, compliance_blocked = validate_official_compliance(payload, known_source_ids, source_categories)
    quality_blocked = validate_quality_blockers(payload, known_source_ids) or task_quality_blocked
    assessed_weight, total_points = validate_dimension_scores(payload, known_source_ids)
    validate_confidence(payload)
    validate_priority_fixes(payload, known_source_ids)
    validate_evidence_consistency(payload)
    compute_scores(payload, assessed_weight, total_points, review_mode)
    compute_verdict(payload, review_mode, compliance_blocked, quality_blocked)

    sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValidationError as exc:
        sys.stderr.write(str(exc) + "\n")
        raise SystemExit(1)
