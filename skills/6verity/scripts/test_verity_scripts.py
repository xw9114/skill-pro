#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from verity_shared import extract_typst_includes


SCRIPTS_DIR = Path(__file__).resolve().parent
CONTRACT_SCRIPT = SCRIPTS_DIR / "contract_closure_check.py"


class VerityScriptTests(unittest.TestCase):
    def test_extract_typst_includes_supports_both_forms(self) -> None:
        text = '\n'.join(
            [
                '#include ("sections/1_intro.typ")',
                '#include "sections/2_method.typ"',
            ]
        )
        self.assertEqual(
            extract_typst_includes(text),
            ["sections/1_intro.typ", "sections/2_method.typ"],
        )

    def test_contract_closure_accepts_metrics_only_no_figure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._create_common_tree(root)
            self._write_json(
                root / "reports/contracts/model_tasks.json",
                {
                    "subproblems": [
                        {
                            "id": "q1",
                            "inputs": ["data/input.csv"],
                            "outputs": ["results/all_results.json#q1"],
                            "key_metrics": ["score"],
                        }
                    ]
                },
            )
            self._write_json(
                root / "results/all_results.json",
                {
                    "subproblems": [
                        {
                            "id": "q1",
                            "metrics": {"score": 0.91},
                            "figure_absence_reason": "该问只产数值评分，不需要图。",
                            "validation": {"consistency": "PASS"},
                            "data_sources": ["data/input.csv"],
                            "reproduce_command": "python code/q1.py",
                        }
                    ]
                },
            )
            self._write_json(root / "figures/figure_manifest.json", [])
            self._write_typst_paper(root)
            completed = self._run_contract(root)
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

    def test_contract_closure_accepts_structured_field_no_figure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._create_common_tree(root)
            self._write_json(
                root / "reports/contracts/model_tasks.json",
                {
                    "subproblems": [
                        {
                            "id": "q2",
                            "inputs": ["data/input.csv"],
                            "outputs": ["results/all_results.json#q2"],
                            "key_metrics": [],
                        }
                    ]
                },
            )
            self._write_json(
                root / "results/all_results.json",
                {
                    "subproblems": [
                        {
                            "id": "q2",
                            "metrics": {},
                            "summary_table": [
                                {"team": "A", "score": 12},
                                {"team": "B", "score": 9},
                            ],
                            "figure_absence_reason": "该问用结构化表回答，不生成图。",
                            "validation": {"schema": "PASS"},
                            "data_sources": ["data/input.csv"],
                            "reproduce_command": "python code/q2.py",
                        }
                    ]
                },
            )
            self._write_json(root / "figures/figure_manifest.json", [])
            self._write_typst_paper(root)
            completed = self._run_contract(root)
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

    def test_contract_closure_normalizes_path_variants(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._create_common_tree(root)
            figure_path = root / "figures/chart.pdf"
            figure_path.write_bytes(b"%PDF-1.4\n%fixture\n")

            self._write_json(
                root / "reports/contracts/model_tasks.json",
                {
                    "subproblems": [
                        {
                            "id": "q3",
                            "inputs": ["data/input.csv"],
                            "outputs": [
                                "results/all_results.json#q3",
                                "/figures/chart.pdf",
                            ],
                            "key_metrics": ["score"],
                        }
                    ]
                },
            )
            self._write_json(
                root / "results/all_results.json",
                {
                    "subproblems": [
                        {
                            "id": "q3",
                            "metrics": {"score": 1.0},
                            "figures": ["./figures\\chart.pdf"],
                            "validation": {"plot_check": "PASS"},
                            "data_sources": ["data/input.csv"],
                            "reproduce_command": "python code/q3.py",
                        }
                    ]
                },
            )
            self._write_json(
                root / "figures/figure_manifest.json",
                [
                    {
                        "id": "fig_chart",
                        "path": str(figure_path),
                        "source": "results/all_results.json:q3",
                    }
                ],
            )
            self._write_typst_paper(
                root,
                section_body='= Solution\n\n#figure(image("../../figures/chart.pdf"), caption: [Chart.])\n\nText.\n',
            )
            completed = self._run_contract(root)
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

    def _run_contract(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(CONTRACT_SCRIPT),
                "--root-dir",
                str(root),
                "--model-tasks",
                str(root / "reports/contracts/model_tasks.json"),
                "--all-results",
                str(root / "results/all_results.json"),
                "--figure-manifest",
                str(root / "figures/figure_manifest.json"),
                "--paper-dir",
                str(root / "paper"),
                "--main",
                str(root / "paper/main.typ"),
                "--sections-dir",
                str(root / "paper/sections"),
            ],
            capture_output=True,
            text=True,
        )

    def _create_common_tree(self, root: Path) -> None:
        for rel in [
            "reports/contracts",
            "results",
            "figures",
            "paper/sections",
            "data",
            "code",
        ]:
            (root / rel).mkdir(parents=True, exist_ok=True)
        (root / "data/input.csv").write_text("x,y\n1,2\n", encoding="utf-8")

    def _write_typst_paper(self, root: Path, section_body: str | None = None) -> None:
        (root / "paper/main.typ").write_text(
            '#include("sections/1_intro.typ")\n#include "sections/2_solution.typ"\n',
            encoding="utf-8",
        )
        (root / "paper/sections/1_intro.typ").write_text(
            "= Intro\n\nShort intro.\n",
            encoding="utf-8",
        )
        body = section_body or "= Solution\n\nThis section answers the question.\n"
        (root / "paper/sections/2_solution.typ").write_text(body, encoding="utf-8")

    def _write_json(self, path: Path, payload: object) -> None:
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


if __name__ == "__main__":
    unittest.main()
