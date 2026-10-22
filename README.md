# IM Writer

将客户的非结构化资料整理成有来源依据的 Information Memorandum 初稿，输出 HTML 和可编辑 PowerPoint。

仓库包含可复用的 Codex skill，以及虚构公司 **Northbridge Field Services 的 10 页英文 sell-side IM**。所有示例公司、人物和业务数据均为虚构。

## 先选择你要做的事

| 目的 | 从这里开始 | 需要什么 |
| --- | --- | --- |
| 查看新版完整 10 页 demo | 下载后打开 `START_HERE.html` | 浏览器；查看 PPT 需要 PowerPoint 或兼容软件 |
| 用自己的资料制作 IM | [Skill 安装与使用](docs/skill-usage.md) | Codex，以及文档与 PPT 生成所需运行环境 |
| 修改程序或重跑模拟案例 | [开发与复跑说明](docs/development.md) | Python、Node、Codex 配套库及 Presentations skill |

## 查看 demo：下载、解压、打开

1. 点击 [下载最新仓库 ZIP](https://github.com/fqi2050/IM-Writer/archive/refs/heads/main.zip)，或在仓库页面选择 **Code → Download ZIP**。
2. 完整解压，打开解压目录里的 **[START_HERE.html](START_HERE.html)**。
3. 在入口页选择 HTML IM、可编辑 PPT 或复核说明。仅查看成品无需安装 skill、Python 或 Node。

也可以单独进入文件页面，点击 **Download raw file / 下载图标** 下载：

- [10 页 HTML IM](demo-northbridge/outputs/northbridge-im.html)：浏览器本地打开；方向键翻页，Sources 查看来源，E 编辑文字，Save HTML 保存副本。
- [可编辑 PowerPoint](demo-northbridge/outputs/northbridge-im-editable.pptx)：原生文字、14 个表格、2 个图表及内嵌数据工作簿。
- [来源与复核说明](demo-northbridge/outputs/review-notes.html)：查看数据冲突和验证范围。

GitHub 文件页显示 HTML 源码，下载到本地后才是演示页面。修改 HTML 后需要重新转换才能得到新版 PPT；修改 PPT 也不会回写 HTML。

仓库只保留展开的项目文件，已移除重复的示范压缩包。上面的 ZIP 由 GitHub 根据当前 `main` 自动打包，无需另找安装包。

## 使用 skill

可复用部分是整个 [skills/mna-information-memo/](skills/mna-information-memo/) 文件夹，包括 `SKILL.md`、脚本、参考规范和样式资源。只复制 `SKILL.md` 会缺少运行文件。安装包内已包含 `assets/storyboard-example.json` 小型格式示例；完整 `demo-northbridge/` 仅用于查看和开发测试，不需要一起安装。

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
  inputs/                       13 份虚构 Word、Excel、访谈、邮件与 CSV 资料
  working/                      提取结果、事实库、冲突清单、故事板
  outputs/                      新版完整 10 页 HTML、可编辑 PPTX、复核说明
  style-pilot/                  早期三页风格参考快照（非最新内容）
  scripts/                      仅用于该模拟案例的生成与复跑程序
  tests/                        检查程序和已保存的验证结果
```

`inputs`、`working`、`outputs` 是同一流程的不同阶段；HTML 与 PPT 是不同交付格式，均需保留。通用转换程序放在 `skills/`，模拟案例的专用程序放在 `demo-northbridge/scripts/`。

## 本次更新：丰富资料并完成 10 页改版

输入从 4 份扩展到 **13 份**。新增商业访谈、区域收入与人员、服务 KPI、合同到期结构、季度财务、CFO 补充邮件、预测收入桥接、行业收入及交易准备纪要。所有新增资料仍是虚构数据，不来自参考 KPMG 报告。

完整 10 页已采用三页样张的白底蓝色标题、浅蓝表格与阅读式信息密度。PPT 包含 **14 个原生表格、2 个原生图表及 2 个内嵌数据工作簿**，来源在 HTML Sources 和 PPT 备注中。13 份输入对应 30 条事实记录、16 项计算。旧版成品由 Git 历史保留，日常查看只需 `outputs/`。

Skill 的 **KPMG 报告参考风格为必遵循要求**。每次生成均需读取 [设计规则](skills/mna-information-memo/references/advisory-design.md)，采用 `style_profile: "advisory-dense"`，按内容选择分析表、图表和注释布局。缺省配置自动采用该风格，其他配置名会报错。原始参考 PDF 和完整 demo 都不是 skill 的运行依赖。

早期 [三页样张](demo-northbridge/style-pilot/README.md) 保留作风格参考，使用补充资料前的证据快照；其中“现金、债务及预测桥接未提供”等状态已由本次补充资料部分更新，阅读最新内容请打开完整 10 页。

## 检查与后续模板工作

已逐页检查 HTML/PPT，核对全部原生表格单元格和文字与故事板一致，并执行资料变更回归、来源定位、表格算术及可编辑图表工作簿检查。可查阅 [完整 10 页检查结果](demo-northbridge/tests/full-deck-test-results.json) 和 [复核说明](demo-northbridge/outputs/review-notes.html)。

当前采用 PDF 报告参考样式，Arial 替代专用标题字体，尚非正式 KPMG PPTX 母版。桌面 PowerPoint 的实际编辑、保存和重开尚未实测。后续母版匹配及应用测试由 [Issue #1](https://github.com/fqi2050/IM-Writer/issues/1) 跟踪。

原始 KPMG 报告、报告截图、Logo 和专用字体均未上传。真实客户资料和受限模板请保存在获准访问的位置。
