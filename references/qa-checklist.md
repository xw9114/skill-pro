# QA Checklist

Run this after rendering every slide at full size. Fix and rerender when any item fails.

## Story

- The title sequence passes the ghost-deck test.
- Each content slide has one main claim.
- Every major claim is supported by visible evidence or source notes.
- The close slide states the decision, implication, recommendation, or next step.

## Visual

- No text overflow, clipping, accidental wrapping, or illegible small text.
- No incoherent overlap between text, charts, images, tables, icons, or footers.
- Alignment follows a consistent grid.
- Spacing is intentional and repeated.
- Contrast is strong enough for projection.
- Layouts vary for a reason and do not feel templated by accident.
- Page numbers, footers, and source notes are consistent.

## Data And Assets

- Chart values match the source notes.
- Labels, legends, units, and time ranges are visible and correct.
- Logos, screenshots, product UI, and brand marks are user-provided, official, or omitted.
- Generated images are documented as generated assets.

## PPTX Quality

- Slides remain editable with native text, shapes, charts, tables, and images.
- Full-slide bitmaps are not used as a substitute for editable slides.
- The exported PPTX exists, is non-empty, and has the expected slide count.
- The output directory contains only the final PPTX and explicitly requested deliverables.

## Output Package

- `<OUTPUT_DIR>/<TOPIC_SLUG>-files/` exists beside the final PPTX.
- The package includes build source, plan, source notes, final slide renders, layout JSON, full contact sheet, visual QA, and structural inspection output when available.
- The retained external scratch workspace still exists for follow-up edits.
- Source files are copied only when redistribution is permitted; otherwise provenance remains in `source-notes.txt`.
- The package contains no secrets, caches, unrelated files, private path disclosures, or unlicensed identity assets.
- The final response links both the `.pptx` and the intermediate package directory.

## Common Fixes

- If a slide is too dense, split it or turn bullets into a diagram/table.
- If a slide feels empty, strengthen the claim or increase exhibit scale instead of adding decoration.
- If a deck feels monotonous, remap page types and vary the evidence layout.
- If a chart is unclear, annotate the takeaway directly on the chart.
- If the deck looks generic, tighten palette, type scale, and spacing before adding new visuals.
