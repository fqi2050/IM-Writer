# IM Writer

将客户的非结构化资料整理成有来源依据的 Information Memorandum 初稿，输出 HTML 和可编辑 PowerPoint。

仓库包含可复用的 Codex skill，以及虚构公司 **Northbridge Field Services 的 10 页英文 sell-side IM**。所有示例公司、人物和业务数据均为虚构。

## 先选择你要做的事

| 目的 | 从这里开始 | 需要什么 |
| --- | --- | --- |
| 查看新版三页样张或原始 10 页 demo | 下载后打开 `START_HERE.html` | 浏览器；查看 PPT 需要 PowerPoint 或兼容软件 |
| 用自己的资料制作 IM | [Skill 安装与使用](docs/skill-usage.md) | Codex，以及文档与 PPT 生成所需运行环境 |
| 修改程序或重跑模拟案例 | [开发与复跑说明](docs/development.md) | Python、Node、Codex 配套库及 Presentations skill |

## 查看 demo：下载、解压、打开

1. 点击 [下载最新仓库 ZIP](https://github.com/fqi2050/IM-Writer/archive/refs/heads/main.zip)，或在仓库页面选择 **Code → Download ZIP**。
2. 完整解压，打开解压目录里的 **[START_HERE.html](START_HERE.html)**。
3. 在入口页选择 HTML IM、可编辑 PPT 或复核说明。仅查看成品无需安装 skill、Python 或 Node。

也可以单独进入文件页面，点击 **Download raw file / 下载图标** 下载：

- [10 页 HTML IM](demo-northbridge/outputs/northbridge-im.html)：浏览器本地打开；方向键翻页，Sources 查看来源，E 编辑文字，Save HTML 保存副本。
- [可编辑 PowerPoint](demo-northbridge/outputs/northbridge-im-editable.pptx)：原生文字、6 个表格、2 个图表及内嵌数据工作簿。
- [来源与复核说明](demo-northbridge/outputs/review-notes.html)：查看数据冲突和验证范围。

GitHub 文件页显示 HTML 源码，下载到本地后才是演示页面。修改 HTML 后需要重新转换才能得到新版 PPT；修改 PPT 也不会回写 HTML。

仓库只保留展开的项目文件，已移除重复的示范压缩包。上面的 ZIP 由 GitHub 根据当前 `main` 自动打包，无需另找安装包。

## 使用 skill

可复用部分是整个 [skills/mna-information-memo/](skills/mna-information-memo/) 文件夹，包括 `SKILL.md`、脚本、参考规范和样式资源。只复制 `SKILL.md` 会缺少运行文件。

按 [安装与使用指南](docs/skill-usage.md) 安装后，指定你的资料目录、输出目录、交易类型、语言、页数及适用模板。Skill 会组织以下流程：

客户资料 → 文件清单与提取 → 事实库及冲突清单 → IM 故事线 → HTML → 可编辑 PPTX → 质量检查。

**当前是依赖 Codex 环境的原型。** 下载仓库或安装 skill 不会自动安装转换运行时；生成 PPT 依赖 `@oai/artifact-tool` 等配套组件，不能仅通过 `npm install` 启动。环境要求见 [开发说明](docs/development.md)。

## 目录说明

```text
README.md                       GitHub 上的快速入口
START_HERE.html                  下载后在浏览器打开的入口
docs/
  skill-usage.md                 安装、调用、使用新客户资料
  development.md                 环境依赖、重跑与限制
skills/mna-information-memo/     可复用 skill 的完整文件夹
demo-northbridge/
  README.md                     模拟案例与数据说明
  inputs/                       Word、Excel、访谈、邮件原始资料
  working/                      提取结果、事实库、冲突清单、故事板
  outputs/                      原始 10 页 HTML、可编辑 PPTX、复核说明
  style-pilot/                  新版三页 HTML/PPT、故事板和来源映射
  scripts/                      仅用于该模拟案例的生成与复跑程序
  tests/                        检查程序和已保存的验证结果
```

`inputs`、`working`、`outputs` 是同一流程的不同阶段；HTML 与 PPT 是不同交付格式，均需保留。通用转换程序放在 `skills/`，模拟案例的专用程序放在 `demo-northbridge/scripts/`。

## 咨询报告式设计样张

已完成投资亮点、业务概览、历史财务三页样张，使用 Northbridge 的虚构证据验证新版配色和阅读式布局。

- [查看三页 HTML](demo-northbridge/style-pilot/northbridge-advisory.html)：下载后在浏览器打开。
- [下载三页可编辑 PPT](demo-northbridge/style-pilot/northbridge-advisory-editable.pptx)：包含原生文字和 3 个表格。
- [样张说明与来源映射](demo-northbridge/style-pilot/README.md)。
- [设计规则](skills/mna-information-memo/references/advisory-design.md)与[配色配置](skills/mna-information-memo/assets/advisory-dense.json)。

Skill 新增可选 `advisory-dense` 配置：在故事板中设置 `style_profile: "advisory-dense"`，并按设计规则编排内容。配置提供默认配色和表格样式，布局、文字与来源仍需编写。HTML 到 PPT 的表格转换保留填色、字重、数字对齐和内边距。

样张参考用户选定报告的视觉特征，标题使用 Arial 替代专用字体；它是 PDF 参考样式，不是 KPMG 原始母版。原始报告、报告截图、Logo 和字体文件均未上传。原始 10 页 demo 保留为改版前基线。

三页样张已完成视觉检查、表格样式/数值/来源映射检查与文件结构检查；旧版表格及图表转换已做回归验证。桌面 PowerPoint 编辑、保存、重开尚未实测。完整记录见 [检查结果](demo-northbridge/tests/advisory-test-results.json)。

## 后续模板改版

三页样张已完成，风格确认及完整 10 页改版仍待推进。后续取得团队的 KPMG 原始 PPTX 模板后，将进一步匹配母版、字体和布局。详细需求见 [Issue #1](https://github.com/fqi2050/IM-Writer/issues/1)。模板尚未加入仓库，当前示例不代表 KPMG 官方模板或认可。

本仓库仅包含虚构示范内容；真实客户资料和受限模板请保存在获准访问的位置。
