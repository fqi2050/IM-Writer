# 开发与模拟案例复跑

[返回首页](../README.md) · [Skill 使用指南](skill-usage.md) · [模拟案例说明](../demo-northbridge/README.md)

## Windows / GitHub Copilot

推荐先按 [公开依赖路径](../skills/mna-information-memo/references/portable-runtime.md) 安装。此路径不需要 Codex runtime、Presentations skill、浏览器自动化或 Windows 符号链接权限。

在仓库根目录的 PowerShell 中：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r skills\mna-information-memo\requirements.txt
npm.cmd ci --prefix skills\mna-information-memo --ignore-scripts --no-audit --no-fund
.\.venv\Scripts\python.exe demo-northbridge\scripts\rebuild.py --backend portable --output-dir "demo-northbridge\runs\copilot-01"
```

`--backend auto` 为默认：Codex 环境变量齐备时使用 Codex，否则使用 portable。可显式指定 `--backend codex` 或 `--backend portable`。portable 从同一份故事板生成 HTML/PPT，不转换手工编辑过的 HTML。只安装 skill、不下载 demo 时，直接使用 skill 内的 `build_portable.py`。

## Codex 专用运行环境

仅打开现有 HTML/PPT 不需要下列依赖。重新生成时，需要在 Codex 环境中取得实际路径：

| 组件 | 用途 |
| --- | --- |
| Python 3.12+，含 `python-docx`、`openpyxl`、`Pillow` | 读取 Word/Excel，建立工作文件，渲染 HTML |
| Node.js，含 `@oai/artifact-tool`、`playwright` | HTML 转原生可编辑 PPT，渲染检查 |
| Google Chrome 或兼容 Chromium | 读取并检查 HTML 页面 |
| 已安装的 Presentations skill | 图表字体辅助、最终检查与工作簿打包 |

让 Codex 调用工作区依赖工具 `load_workspace_dependencies` 定位运行时，并确认 Presentations skill 的安装路径。`@oai/artifact-tool` 与这些辅助工具由运行环境提供，仓库不包含它们。缺少该环境时仍可查看成品，但不能保证完成重新生成；没有通用的 `npm install` 启动命令。

## 重跑 Northbridge 示例

在仓库根目录运行。先将以下占位符替换为实际路径：

```sh
export IM_NODE="<bundled-node-executable>"
export RUNTIME_NODE_MODULES="<bundled-node-modules-directory>"
export IM_PRESENTATIONS_SKILL="<installed-presentations-skill-directory>"
# 使用非默认 Chrome 时设置：
# export IM_BROWSER_PATH="<chromium-executable>"

"<bundled-python-executable>" demo-northbridge/scripts/rebuild.py \
  --output-dir "demo-northbridge/runs/run-01"
```

输出目录必须尚不存在。脚本会复制模拟输入，依次提取、生成案例故事板、渲染 HTML、转换 PPT 并完成最终处理。运行完成后打开：

```text
demo-northbridge/runs/run-01/outputs/northbridge-im.html
demo-northbridge/runs/run-01/outputs/northbridge-im-editable.pptx
```

`runs/` 和临时构建目录已被 Git 忽略。脚本不覆盖原始模拟输入。该流程是 Northbridge 案例的固定映射，新客户使用 [skill 工作流](skill-usage.md) 重新分析。

## 修改位置

- 通用提取、HTML 渲染、PPT 转换：[skill scripts](../skills/mna-information-memo/scripts/)。
- 支持的 HTML 元素与格式：[渲染约定](../skills/mna-information-memo/references/rendering-contract.md)。
- 模拟案例的内容和财务计算：[build_storyboard.py](../demo-northbridge/scripts/build_storyboard.py)。
- 检查程序及上次保存的结果：[tests](../demo-northbridge/tests/)。结果文件描述对应示例的已执行检查，不代表每次修改后自动重新验证。

修改后按 [质量检查规范](../skills/mna-information-memo/references/quality-checks.md) 检查受影响的证据、页面和 PPT 对象。

## 已知限制

- 转换器支持本项目约定的 HTML 文字、表格与柱状图，不支持任意网页或任意 PPT 模板直接转换。
- 图表工作簿是可编辑快照，不保留客户 Excel 的实时连接。
- HTML、PPT 与事实库之间不自动双向同步；内容变更后要核对并重新生成相关交付物。
- 现有示例已做文件结构、页面边界、来源追溯和回归检查；桌面 Microsoft PowerPoint 的实际编辑、保存和重开尚未实测。
- 完整 10 页已采用强制的 KPMG 报告参考风格；正式 PPTX 母版尚未提供，后续匹配由 [Issue #1](https://github.com/fqi2050/IM-Writer/issues/1) 跟踪。

## 丰富版资料与检查

仓库已包含 13 份输入，无需先重新生成。`create_enrichment.py` 仅重建编号 05–13 的虚构资料；它会覆盖这些固定模拟文件。`rebuild.py` 会输出 HTML、最终 PPT、复核说明及工作文件。

数据口径及来源检查：`test_evidence.py`；完整成品和强制风格检查：`test_full_deck.py`；原生 PPT 包检查：`check_package.py`；浏览器检查：`test_browser.mjs`。Python 检查使用上述 bundled Python，浏览器检查使用 bundled Node 并设置 `IM_PYTHON`。测试脚本旁需链接运行时 `node_modules`，链接不提交到 Git。

## 无浏览器生成方式

在获准浏览器不可用时，给 `rebuild.py` 添加 `--native-from-storyboard`。此模式将同一份已测量故事板分别渲染为 HTML 和原生 PPT，不读取 HTML DOM，因此不会转换用户手工修改过的 HTML。默认方式仍为 HTML 转 PPT。

`prepare_layout.py` 使用 Arial 字体度量来检查文本并分配表格行高，随后将行高同时用于 HTML 和 PPT。自动识别 Windows 和 macOS 系统 Arial；其他环境通过 `IM_FONT_REGULAR` 和 `IM_FONT_BOLD` 指向合法安装的 Arial 字体文件。

当前高密度版使用无浏览器模式。HTML 已做源代码和结构检查，本轮未进行浏览器视觉或交互复测；`browser-test-results.json` 标记保留的上一版测试。最终 PPT 已重新导入生成工具并逐页查看，桌面 PowerPoint 未实测。
