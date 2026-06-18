---
name: ppt-design-pro
description: Improve the quality of generated PowerPoint decks by adding a design, story, template, QA, and reproducible-output layer on top of PPTX generation. Use when Codex needs to create, improve, redesign, polish, or critique a PPT, PowerPoint, presentation, deck, slide deck, pitch deck, report deck, academic talk, business review, product deck, training deck, or any .pptx deliverable where visual quality, narrative structure, editable slides, template fidelity, or packaged source and QA artifacts matter.
---

# PPT Design Pro

## Role

Use this skill as the design-quality layer for PPT work. For final `.pptx` creation, editing, rendering, and export, also use `presentations:Presentations`; this skill defines what "good" means before that lower-level skill builds the file.

Do not optimize for decorative slides. Optimize for a deck that an experienced presenter could actually use: clear story, strong evidence, varied page types, editable native objects, disciplined spacing, and a visible QA loop.

## Workflow

1. Determine the mode:
   - `create`: build a new deck.
   - `template-following`: use a provided PPTX as visual source of truth.
   - `targeted-polish`: improve an existing deck's structure, layout, style, or clarity.
   - `critique`: review a deck and return prioritized fixes.
2. Write a compact design brief before generating slides:
   - audience, occasion, decision the deck should support, tone, slide count, format, deadline.
   - source material and evidence boundaries.
   - visual direction, density, chart/table needs, template constraints.
3. Build an action-title outline:
   - every content slide title must state a conclusion, not a topic.
   - the title sequence alone must tell the story.
   - each slide gets one main job and one primary exhibit.
4. Map each slide to a page type and layout archetype before authoring:
   - use the page taxonomy in `references/slide-playbook.md`.
   - vary layouts intentionally; do not repeat title + bullets across the deck.
5. Define a visual system:
   - read `references/style-recipes.md` when no user template or brand guide is provided.
   - choose one dominant color, one neutral text/background pair, one support tone, and one accent.
   - define fonts, type scale, grid, spacing rhythm, chart style, and footer/source-note style.
6. Produce the PPTX with `presentations:Presentations`:
   - keep slides editable with native text, shapes, charts, tables, and images.
   - do not use full-slide screenshots as the final slide unless the user explicitly requests image-only output.
   - keep source notes and asset provenance.
7. Render every final slide and run the QA gate in `references/qa-checklist.md`.
8. Fix visible problems, rerender, and only then deliver the `.pptx`.
9. Package reproducible intermediate artifacts beside the final PPTX:
   - keep the final PPTX at `<OUTPUT_DIR>/<TOPIC_SLUG>.pptx`.
   - create `<OUTPUT_DIR>/<TOPIC_SLUG>-files/` for the intermediate bundle.
   - preserve the retained external scratch workspace; copy artifacts instead of moving or deleting it.
   - include the build source, `slide-plan.txt` or `edit-plan.txt`, `source-notes.txt`, final slide renders, layout JSON, full contact sheet, `visual-qa.txt`, and structural inspection output when available.
   - include source copies only when redistribution is permitted; otherwise keep the source title and URL in `source-notes.txt`.
   - exclude secrets, credentials, caches, unrelated files, private local-path disclosures, and unlicensed identity assets.
10. Return links to both the final PPTX and the `<TOPIC_SLUG>-files/` directory.

## Content Rules

- Prefer action titles: "Enterprise adoption is blocked by procurement latency" beats "Procurement".
- Use the ghost-deck test: if only slide titles are visible, the argument should still make sense.
- Put the main point close to the main evidence. Do not bury conclusions in footnotes.
- Avoid generic agenda filler. If a TOC is needed, make it a navigation device, not a formality.
- Keep one primary exhibit per content slide: chart, table, diagram, comparison, timeline, screenshot, quote, or framework.
- For quantitative claims, include traceable source notes. Do not invent numbers, dates, logos, screenshots, or product UI.
- For academic or analytical decks, prioritize argument structure, evidence, and citation clarity over visual flourish.

## Visual Rules

- Reject the default AI look: white background, centered title, thin accent line, three bullet cards, random icons, and repeated layouts.
- Use whitespace as structure. Do not add decoration to fill emptiness.
- Use charts and diagrams when they compress reasoning better than prose.
- Use tables only when comparison matters; otherwise use ranked lists, matrices, or callouts.
- Avoid visual monotony: alternate between full-bleed statement pages, split evidence pages, comparison pages, timelines, process flows, matrices, and section dividers as appropriate.
- Keep typography stable. Use no more than two families and a clear scale.
- Keep contrast high enough for projection. Treat small gray text as a failure unless it is a noncritical source note.
- Use verified official assets for logos, product UI, screenshots, and brand marks; otherwise omit them.

## Template Handling

If the user provides a PPTX template, treat it as the visual source of truth:

- inspect it before planning.
- map each output slide to the closest source slide or layout.
- preserve typography, palette, spacing, footers, page markers, image crops, chart frames, and brand chrome unless asked to restyle.
- edit inherited objects where possible instead of rebuilding from blank slides.
- if the template cannot support requested content cleanly, report the closest viable options before forcing an awkward slide.

## Critique Output

For review-only tasks, return findings in this order:

1. story and decision clarity.
2. evidence and claim support.
3. page-type variety and information density.
4. layout, typography, color, chart, and accessibility issues.
5. prioritized fixes with slide numbers.

Do not rewrite the whole deck unless the user asks for implementation.

## References

- `references/slide-playbook.md`: page types, layout archetypes, and when to use each.
- `references/style-recipes.md`: practical visual systems for business, technical, academic, pitch, and training decks.
- `references/qa-checklist.md`: final render QA and failure modes to fix before delivery.
