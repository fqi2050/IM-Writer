# Semantic slide format v1

The JSON root has `title`, `synthetic`, `slides`. Each slide has `title`, `background`, `notes` and `elements`. The design coordinates use a 1280 x 720 frame. HTML expands coordinates uniformly to a fixed 1920 x 1080 stage. PPT uses the 1280 x 720 frame.

All elements have `id`, `type`, `x`, `y`, `w`, `h`, `fact_ids` and optionally `calc_ids`. Text: `text`, `size` (CSS pixels at 1280 width), `color`, `bold`, `align`. Tables: rectangular string `rows`, proportional `widths`, `size`. Charts: `categories`, one numeric `values` series, `series_name`, `color`, `max`, `unit`, `format` (`0.0` or `0.0%`). Chart v1 is a vertical column chart, with values on top of bars. Lines: `color`; these are layout rules, not illustrations.

Optional root `style_profile: "advisory-dense"` loads `assets/advisory-dense.json`. Omit it to retain the original palette. Unknown profiles fail explicitly. It sets default text/chart colors and table header, band, border and padding styles; explicit element colors take precedence. Layout, typography size choices and source footers remain authored in the storyboard. Read [advisory-design.md](advisory-design.md) before using the profile.

Optional table `column_align` is one `left`, `center` or `right` value per column; default is all left. `emphasis_rows` is a list of zero-based row indices to bold (header is row 0 and always bold). Numeric financial columns should normally align right. The converter reads table cell fills, colors, font weights, sizes, alignments and padding from the DOM so those choices persist in native PowerPoint tables.

HTML contract: `.slide` elements contain `[data-pptx]` elements with types text, table, chart or rule. Layout, text styles and values come from the DOM. Table headers use `th`; body uses `td`. Chart configuration is JSON in `data-chart`. Source notes are JSON in a child `script[data-notes]`. The converter uses Playwright with network blocked and disabled source scripts, validates fixed slide sizes and simple styles, and maps these objects to native PowerPoint elements. Inline table cells are plain text. Images, arbitrary CSS, rotations, nested rich text, custom SVG illustrations, stacked/combo charts and arbitrary HTML pages are not supported by v1.

Browser edits to text and table cells survive Save HTML and reconversion. Chart SVG is only its preview: edit `data-chart` or storyboard data to change chart values, then regenerate the preview. Reconcile numerical edits with the fact ledger. Output charts contain editable snapshot workbooks, not source formula links.

CLI:

```text
"<python>" "<skill-directory>/scripts/extract_sources.py" "<client-input-directory>" "<run-directory>/working/extracted.json"
"<python>" "<skill-directory>/scripts/render_html.py" "<run-directory>/working/storyboard.json" "<run-directory>/outputs/im.html"
"<node>" "<skill-directory>/scripts/html_to_pptx.mjs" "<run-directory>/outputs/im.html" "<run-directory>/.build/draft.pptx" "<run-directory>/.build/previews"
```

The commands in this section are for the Codex HTML DOM exporter. For Copilot or a missing private runtime, use [portable-runtime.md](portable-runtime.md) instead. Use the host's bundled runtimes/package path only when available. The converter defaults to an isolated headless Google Chrome process; set IM_BROWSER_PATH for another compatible Chromium executable. Set IM_PRESENTATIONS_SKILL to the installed Presentations skill folder so chart fonts use its shared helper. Build a fresh evidence ledger and storyboard from the client inputs. The skill does not require a repository demo or a demo rebuild script.

## Bundled format example

[storyboard-example.json](../assets/storyboard-example.json) is included in the installed skill. It demonstrates text, a rule, a table, a chart, source notes and the advisory profile on one synthetic page. It is a schema/rendering example, not an IM or a client evidence ledger. All example values are fictional.

From any working directory, use absolute paths (replace placeholders):

```sh
"<python>" "<skill-directory>/scripts/render_html.py" \
  "<skill-directory>/assets/storyboard-example.json" \
  "<new-run-directory>/format-example.html"
```

The renderer reads its CSS and design profile from the installed skill assets. The generated HTML is standalone. Do not write run outputs into the installed skill folder.

The `advisory-dense` style is mandatory. The renderer applies it when the field is omitted and rejects null or alternative profile names. Authors must still use the prescribed palette and page layouts for explicit element styles.

Optional table `row_heights` lists positive heights in storyboard units, one per row, totalling the declared table height. Use measured content fit to allocate rows. HTML preserves these authored row heights; its DOM converter measures the resulting table. Native storyboard authoring must apply the same row heights.
