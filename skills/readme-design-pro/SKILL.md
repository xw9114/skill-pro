---
name: readme-design-pro
description: Create, restructure, visually polish, or audit GitHub repository README.md files using verified repository facts and optional visual references. Use when Codex needs to turn a minimal README into a professional project landing page, match the information architecture of a reference screenshot, reposition a repository, document a single Skill or multi-Skill collection, add factual badges, tables, Mermaid diagrams, installation and usage examples, FAQ sections, or validate README encoding and links.
---

# README Design Pro

## Role

Build a useful repository entry point, not a decorative marketing page. Derive every command, feature, version, license claim, compatibility statement, and link from repository evidence or explicit user input.

Treat a reference screenshot as a structure and visual-rhythm reference. Do not copy its project-specific claims, wording, badges, metrics, people, or branding.

## Modes

- `create`: write a README for a repository that has none or only a placeholder.
- `reference-redesign`: reproduce the information hierarchy of a supplied screenshot or example.
- `reposition`: update the README when the repository's audience, scope, or product identity changes.
- `targeted-edit`: add or fix bounded sections without rewriting unrelated content.
- `audit`: review the README and return prioritized findings without editing unless requested.

## Workflow

1. Inspect before writing:
   - read the existing README, top-level files, manifests, documentation, license, Skill metadata, examples, and relevant source entry points.
   - inspect Git status and remotes when working in a repository.
   - distinguish verified facts from proposals and future plans.
2. Inspect visual references when provided:
   - use image inspection to identify hierarchy, spacing rhythm, component types, and section order.
   - extract reusable patterns such as centered header, badges, comparison tables, code blocks, FAQ, and charts.
3. Choose the README architecture:
   - identify the primary audience, promise, first action, proof, and maintenance model.
   - read `references/readme-patterns.md` and select only components that serve the repository.
   - for a collection repository, lead with the collection purpose and catalog; present individual projects as entries, not as the repository identity.
4. Draft with factual constraints:
   - use one clear H1 and a concise value statement.
   - make installation and usage commands directly runnable.
   - use tables for comparison and catalogs, Mermaid for workflows, and `<details>` for secondary FAQ content.
   - add badges only when their claims are verifiable. Never claim a license without a license file or explicit user decision.
   - do not invent versions, download counts, supported platforms, benchmarks, roadmaps, contributors, or testimonials.
5. Edit narrowly:
   - modify `README.md` with `apply_patch`.
   - preserve correct project-specific content and user-authored constraints.
   - do not add screenshots, logos, license files, or auxiliary documentation unless requested or genuinely required.
6. Validate:
   - run `python scripts/check_readme.py <path-to-README.md> --repo-root <repo-root>`.
   - run `git diff --check` in Git repositories.
   - verify UTF-8 text, relative links, code-fence balance, commands, anchors, and repository status.
   - inspect the final diff to confirm no unrelated files changed.
7. Report:
   - summarize the new information architecture and validation results.
   - state whether changes are local-only.
   - do not commit or push unless the user explicitly requests it; follow any required confirmation process before publishing.

## Content Rules

- Put the repository's identity and literal purpose first; supporting value propositions belong below it.
- Prefer concrete capabilities and examples over adjectives such as "powerful", "best", or "complete".
- Keep badges factual and limited. Broken or misleading badges reduce trust.
- Match navigation links to real headings and repository paths.
- Use a "planned" or "roadmap" label for unimplemented features.
- Separate repository-level instructions from component- or Skill-level instructions.
- Keep README commands platform-aware when path syntax differs.
- Do not expose private absolute paths, credentials, local usernames, access tokens, or internal-only URLs.

## Repository Repositioning

When a repository changes scope:

1. Replace the H1, opening statement, navigation, badges, and first explanatory section to match the new identity.
2. Reorder the catalog and architecture before detailed documentation of the original component.
3. Preserve the original component as a current entry when it still exists.
4. Explain transitional directory or repository naming only when it helps users avoid broken installs.
5. Do not claim that a planned multi-project structure already exists; label target structures as recommendations or plans.

## Audit Output

For review-only requests, report findings in this order:

1. incorrect, unsupported, or stale claims.
2. broken installation or usage paths.
3. missing repository identity and first action.
4. information architecture and scanability problems.
5. visual components, badges, diagrams, and FAQ improvements.

## Resources

- `references/readme-patterns.md`: component patterns, repository-type structures, badge rules, and reference-image translation.
- `scripts/check_readme.py`: deterministic UTF-8, Markdown-fence, relative-link, and placeholder checks.
