# IM Writer

将客户的非结构化资料整理为可追溯的 Information Memorandum 初稿，并生成 HTML 与可编辑 PowerPoint。

当前版本包含一套 **10 页英文 sell-side IM**、可复用的 Codex skill，以及完整的虚构公司测试资料。示例公司 Northbridge Field Services 的所有人物、业务和财务数据均为虚构。

## 查看示范

- [下载完整示范包](mna-im-starter-kit.zip)，解压后打开 `START_HERE.html`。
- [可编辑 PowerPoint](demo-northbridge/outputs/northbridge-im-editable.pptx)：原生文字、6 个表格、2 个图表及内嵌数据工作簿。
- [HTML IM](demo-northbridge/outputs/northbridge-im.html)：下载后在浏览器打开，方向键翻页，Sources 查看来源，E 编辑文字，Save HTML 保存。
- [Skill 初稿](skills/mna-information-memo/SKILL.md)。
- [来源与复核说明](demo-northbridge/outputs/review-notes.html)。

GitHub 文件页面展示 HTML 源码；请下载后本地打开。仓库未配置网站发布。

## 工作流程

客户资料 → 文件清单与提取 → 事实库及冲突清单 → IM 故事线 → HTML → 可编辑 PPTX → 质量检查。

输入示例包含 Word 公司简介、Excel 管理层模型、访谈文本和 CFO 邮件。财务模型包含历史数据、管理层预测、客户销售和服务收入。

示例故意保留以下问题，用来测试分析与披露：

- FY2025 收入在模型中为 £25.0m，在旧简介中为 £26.2m。
- 财务模型使用 GBP million，销售明细使用 GBP thousand。
- 管理层的 94% 留存率没有明确定义或客户群计算依据。
- 市场规模、市场份额、QoE、现金、债务和标准化营运资金等证据缺失。

数据冲突会进入相关页面和问题清单。缺失信息不会自动填成零或编造为事实。来源定位保存在事实库和 PPT 每页备注中。

## 目录

```text
skills/mna-information-memo/   Skill、参考规范、HTML/PPT 转换程序
 demo-northbridge/
   inputs/                    虚构客户原始资料
   working/                   文件清单、提取结果、事实库、故事板
   outputs/                   HTML、PPTX、复核说明
   scripts/                   示例生成与复跑程序
   tests/                     数据、文件结构及浏览器回归检查
START_HERE.html               中文使用入口
mna-im-starter-kit.zip         可下载的完整示范包
```

## 使用与复跑

将 `skills/mna-information-memo` 复制到 Codex 的本地 skills 目录，或在任务中直接指定该目录下的 `SKILL.md`。新项目需要提供资料目录、交易类型、语言、页数和适用模板。

示例重跑使用 Codex 工作区的依赖运行时：

- Python：`python-docx`、`openpyxl`。
- Node.js：`@oai/artifact-tool`、`playwright`。
- 本地 Google Chrome，或通过 `IM_BROWSER_PATH` 指定兼容的 Chromium。
- 已安装的 Presentations skill，用于 PPT 最终检查和图表工作簿打包。

通过工作区依赖工具取得实际路径，再设置环境变量：

```sh
export IM_NODE="<bundled-node-executable>"
export RUNTIME_NODE_MODULES="<bundled-node-modules-directory>"
export IM_PRESENTATIONS_SKILL="<installed-presentations-skill-directory>"
"<bundled-python-executable>" demo-northbridge/scripts/rebuild.py --output-dir "<new-run-directory>"
```

程序在新目录重跑，保留原始模拟输入。该运行流程已经执行验证。`@oai/artifact-tool` 与相关工具由 Codex 环境提供，仓库不包含这些运行时，因此当前不是可直接 `npm install` 的独立应用。

## 当前边界和设计方向

当前版式用于验证端到端流程。下一阶段将采用团队提供的 **KPMG 原始 PPTX 模板**和获准使用的脱敏 IM 示例，调整章节结构、信息密度、财务图表、母版、品牌及来源格式。模板尚未加入本仓库，当前版本不代表 KPMG 官方模板或认可。

转换器支持本项目定义的 HTML 文字、表格与柱状图格式，不是任意网页转 PPT 的通用转换器。Northbridge 的示例生成器使用预先编写的案例映射；新客户仍需重新提取、分析并建立事实库和故事线。

图表工作簿保存的是可编辑数据快照，不会自动链接或刷新客户 Excel。修改 HTML 中的数字后，应重新核对事实库。文件结构、页面边界、来源追溯及回归测试已检查，桌面 Microsoft PowerPoint 的实际编辑、保存和重开尚未实测。

本仓库仅包含本次生成的虚构示范内容，不包含原工作目录中的会议纪要、其他项目 PPT 或客户财务资料。
