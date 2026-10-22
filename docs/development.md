# 开发与模拟案例复跑

[返回首页](../README.md) · [Skill 使用指南](skill-usage.md) · [模拟案例说明](../demo-northbridge/README.md)

## 运行环境

仅打开现有 HTML/PPT 不需要下列依赖。重新生成时，需要在 Codex 环境中取得实际路径：

| 组件 | 用途 |
| --- | --- |
| Python，含 `python-docx`、`openpyxl` | 读取 Word/Excel，建立工作文件，渲染 HTML |
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
- KPMG 模板尚未提供，后续改版由 [Issue #1](https://github.com/fqi2050/IM-Writer/issues/1) 跟踪。
