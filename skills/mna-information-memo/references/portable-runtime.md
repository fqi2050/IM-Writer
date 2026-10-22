# Portable runtime for VS Code / GitHub Copilot

Use this path when Codex's dependency loader or `@oai/artifact-tool` is absent. Copilot can execute ordinary local programs through the user's enabled tools. Skill files do not supply Python, Node, or private Codex packages. Do not ask Copilot to find Codex-specific runtime directories or install an unverified `@oai/artifact-tool` package.

## One-time setup (Windows PowerShell)

Install Python **3.12+** and Node.js **20+** using the team's approved installation method. Reopen the VS Code terminal after installation. Run from the directory containing this skill's `SKILL.md`:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
npm.cmd ci --ignore-scripts --no-audit --no-fund
```

If a newer Python is installed, replace `py -3.12` with that launcher version. Using the venv executable directly does not require changing PowerShell execution policy. `npm.cmd` avoids the separate npm.ps1 execution-policy issue. Do not disable corporate proxy or security settings to install dependencies.

PptxGenJS is pinned in `package-lock.json`. [Official installation](https://gitbrent.github.io/PptxGenJS/docs/installation/), [native tables](https://gitbrent.github.io/PptxGenJS/docs/api-tables/), [native charts](https://gitbrent.github.io/PptxGenJS/docs/api-charts/).

## Smoke test without client data

From the same skill folder:

```powershell
.\.venv\Scripts\python.exe scripts\build_portable.py assets\storyboard-example.json "$env:TEMP\im-format-check-01"
```

Choose a new output directory each time. The bundled example is synthetic schema data, not client content. Outputs are `outputs/im.html`, `outputs/im-editable.pptx`, structural `validation.json` and `build-info.json`.

## New client build

Create a fresh source inventory, fact ledger, issue register and semantic storyboard using this skill. Keep all substantive claims and calculations source-linked. Then:

```powershell
.\.venv\Scripts\python.exe scripts\build_portable.py "C:\Client Project\working\storyboard.json" "C:\Client Project\runs\draft-01"
```

The workflow measures Arial text and row heights, builds HTML, authors native PPT text/tables/charts with PptxGenJS, and checks content and embedded chart data. No browser automation, `IM_PRESENTATIONS_SKILL`, private finalizer or directory symlink is required. Chart workbooks are editable snapshots. The mandatory `advisory-dense` style still applies.

This mode generates HTML and PPT from the **same storyboard**. It does **not** convert arbitrary HTML or incorporate manual HTML edits. Reconcile edited content into the storyboard and ledger before regeneration. Keep the selected rendering mode visible in the build report.

## Dependencies and failures

- `py` missing: install/locate Python 3.12+ and use its full executable path.
- `node` missing: install/locate Node.js 20+ and reopen the terminal, or set `IM_NODE` to its executable.
- `pptxgenjs` missing: run `npm.cmd ci` in the skill folder, not a different project folder. The exporter resolves modules from its own installed location.
- Python package missing: use the same Python/venv for installation and execution.
- Arial missing: Windows defaults to `%WINDIR%\Fonts\arial.ttf` and `arialbd.ttf`. Set `IM_FONT_REGULAR` and `IM_FONT_BOLD` to existing licensed font files if necessary. macOS Arial paths are detected separately. Fonts are not distributed.
- Fit validation fails: edit copy or layout before shrinking type. Do not ignore overflow.
- Network installation fails: report the actual registry/proxy error. Do not repeatedly retry a private Codex dependency in Copilot.

Structural checks do not establish visual fit in PowerPoint. Open every generated slide, check sources and footer visibility, and test editing/saving/reopening in the target PowerPoint installation. The portable route has been exercised on macOS with public dependencies, including paths with spaces and Chinese characters. Windows desktop execution remains untested until explicitly verified there.
