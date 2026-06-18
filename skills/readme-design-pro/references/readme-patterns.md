# README Patterns

Use this reference to select a small set of components that match the repository. Do not include every pattern by default.

## Header

A strong GitHub header usually contains:

1. one literal H1 with the project or collection name.
2. one sentence explaining the concrete outcome.
3. optional short navigation links to major sections.
4. a restrained badge row containing only verified claims.

Use `<div align="center">` when a centered project header improves scanning. Keep operational sections left-aligned.

## Badge Rules

Good badge candidates:

- current version derived from a manifest or release.
- build or validation status backed by an actual workflow.
- license backed by a repository license file.
- GitHub stars, issues, pull requests, and last commit for the current repository.
- supported runtime versions backed by manifests or tested constraints.

Avoid:

- badges copied from another project.
- static claims that look dynamic but are not maintained.
- download, benchmark, platform, or compatibility claims without evidence.
- license badges when no license has been selected.
- large badge walls that push the real purpose below the fold.

## Repository-Type Structures

### Single Skill

1. identity and value statement.
2. problem and capability comparison.
3. prerequisites and installation.
4. invocation examples.
5. workflow and output structure.
6. resource navigation and FAQ.

### Skill Collection

1. collection identity and maintenance philosophy.
2. catalog of available Skills with status and entry paths.
3. installation model for one Skill or the collection.
4. shared quality standard and repository layout.
5. contribution workflow.
6. detailed spotlight for current Skills.

Do not let the first Skill remain the repository's headline after the repository becomes a collection.

### Library or CLI

1. literal product name and outcome.
2. install command.
3. minimal working example.
4. supported environments.
5. API or command navigation.
6. development, testing, release, and support information.

### Application

1. literal application name and purpose.
2. real product screenshot when available and useful.
3. setup and run commands.
4. configuration and architecture.
5. deployment and contribution guidance.

## Component Selection

- Use tables for catalogs, comparisons, compatibility, or resource navigation.
- Use fenced code blocks for commands and copyable configuration.
- Use Mermaid for workflows and architecture that are easier to scan visually than as prose.
- Use `<details>` for FAQ and secondary explanations.
- Use a repository tree only when it explains installation or ownership boundaries.
- Use Star History only for public repositories where historical stars provide meaningful context.
- Use screenshots only when they reveal the actual product or output; do not use atmospheric images.

## Translating A Reference Image

Extract:

- header alignment and hierarchy.
- section order and density.
- recurring components such as badges, tables, code panels, FAQ, and charts.
- spacing rhythm and where the reader receives the first runnable action.

Do not copy:

- project name, metrics, versions, license, commands, people, logos, or feature claims.
- broken badges or private service links visible in the reference.
- sections that do not apply to the target repository.

## Integrity Checklist

- Every install command matches the actual repository layout.
- Every relative link resolves from the README directory.
- Every feature is implemented or clearly labeled as planned.
- Every license claim matches a license file.
- Every version claim comes from a source of truth.
- Every external identity asset is official or user-provided.
- No private local path or credential appears in prose or examples.
