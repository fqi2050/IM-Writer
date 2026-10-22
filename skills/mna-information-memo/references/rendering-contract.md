# Semantic slide format v1

The JSON root has `title`, `synthetic`, `slides`. Each slide has `title`, `background`, `notes` and `elements`. The design coordinates use a 1280 x 720 frame. HTML expands coordinates uniformly to a fixed 1920 x 1080 stage. PPT uses the 1280 x 720 frame.

All elements have `id`, `type`, `x`, `y`, `w`, `h`, `fact_ids` and optionally `calc_ids`. Text: `text`, `size` (CSS pixels at 1280 width), `color`, `bold`, `align`. Tables: rectangular string `rows`, proportional `widths`, `size`. Charts: `categories`, one numeric `values` series, `series_name`, `color`, `max`, `unit`, `format` (`0.0` or `0.0%`). Chart v1 is a vertical column chart, with values on top of bars. Lines: `color`; these are layout rules, not illustrations.

HTML contract: `.slide` elements contain `[data-pptx]` elements with types text, table, chart or rule. Layout, text styles and values come from the DOM. Table headers use `th`; body uses `td`. Chart configuration is JSON in `data-chart`. Source notes are JSON in a child `script[data-notes]`. The converter uses Playwright with network blocked and disabled source scripts, validates fixed slide sizes and simple styles, and maps these objects to native PowerPoint elements. Inline table cells are plain text. Images, arbitrary CSS, rotations, nested rich text, custom SVG illustrations, stacked/combo charts and arbitrary HTML pages are not supported by v1.

Browser edits to text and table cells survive Save HTML and reconversion. Chart SVG is only its preview: edit `data-chart` or storyboard data to change chart values, then regenerate the preview. Reconcile numerical edits with the fact ledger. Output charts contain editable snapshot workbooks, not source formula links.

CLI:

```text
python3 scripts/extract_sources.py input_folder working/extracted.json
python3 scripts/render_html.py working/storyboard.json outputs/im.html
node scripts/html_to_pptx.mjs outputs/im.html .build/draft.pptx .build/previews
```

Use the host's bundled runtimes/package path. The converter defaults to an isolated headless Google Chrome process; set IM_BROWSER_PATH for another compatible Chromium executable. Set IM_PRESENTATIONS_SKILL to the installed Presentations skill folder so chart fonts use its shared helper. The demo contains its own rebuild script and authored evidence/storyboard generator. Those scripts replay the fixture and do not implement a universal autonomous extraction-to-narrative engine.
