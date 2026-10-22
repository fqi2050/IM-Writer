# Skill 安装与使用

[返回首页](../README.md) · [运行环境与复跑](development.md)

## 先确认目标

只看 demo：完整解压仓库后打开 [START_HERE.html](../START_HERE.html)，无需安装。

制作新 IM：需要可访问本地文件的 Codex 环境，以及本项目要求的文档、浏览器和 PPT 运行依赖。先让 Codex 按 [环境清单](development.md#运行环境) 检查依赖是否可用，再执行生成。

## 安装完整 skill 文件夹

将仓库中的 `skills/mna-information-memo/` 整个文件夹复制到用户级目录 `~/.agents/skills/`，得到：

```text
~/.agents/skills/mna-information-memo/
  SKILL.md
  agents/
  assets/
  references/
  scripts/
```

`assets/storyboard-example.json` 是随 skill 安装的最小格式示例。完整的 `demo-northbridge/` 留在仓库中，不需要复制到 skills 目录；skill 不依赖其路径或业务数据。客户资料与生成结果也保存在独立项目目录。

已有同名 skill 时先比较版本，避免形成多份同名安装。Codex 会自动发现变化；如果未显示，重启 Codex。目录与发现机制参见 [OpenAI 官方 skill 文档](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)。

安装的是工作流和程序文件，运行依赖仍需另行确认。仓库中的 `skills/` 是分发目录，单纯下载到这里不等于完成自动发现配置。

## 用自己的资料开始

在仓库以外建立独立客户项目，避免混入 Northbridge 的虚构资料：

```text
client-project/
  inputs/                  客户提供的原始资料
  templates/               获准使用的 PPTX 模板和参考页（如有）
  runs/                    每次生成使用新的子目录
```

在 Codex 中使用下面的请求，替换尖括号中的路径：

```text
使用 mna-information-memo skill。
客户资料目录：<客户项目绝对路径>/inputs
本次输出目录：<客户项目绝对路径>/runs/draft-01
目标：10 页英文 sell-side Information Memorandum，面向潜在收购方。
模板：<获准使用的 PPTX 绝对路径；尚未提供则注明未提供>。

先检查生成所需运行环境，然后盘点资料、建立有来源定位的事实库、
记录重大数据冲突及缺失证据，再制作故事板、HTML 和可编辑 PPTX。
请保留原始资料，将本次工作文件和输出写入新的输出目录。
附上事实库、问题清单、输入文件清单及质量检查结果。
```

如果尚未安装，也可以在任务中明确指定下载目录内 `skills/mna-information-memo/SKILL.md` 的绝对路径，让 Codex 读取并按其工作流处理。

## 输入、输出与复核

提取脚本支持 DOCX、XLSX、文本、邮件文本、CSV、TSV 和 JSON 等格式。PDF、扫描件及其他格式需要另选读取或 OCR 工具，并记录无法读取的内容。

交付应包括 HTML、可编辑 PPTX、事实库、未决问题清单和输入文件清单。先检查数据口径、预测假设和重要投资陈述，再检查版式。

HTML 的文字编辑功能用于修改副本；财务数字变化还需同步核对事实库，重新转换并检查 PPT。图表的数值通过故事板或图表元数据修改，不能仅修改图表预览文字。PPT 内嵌图表工作簿是数据快照，不会自动刷新客户 Excel。

Northbridge 的 `rebuild.py` 只重放既定模拟案例。新客户需要重新建立事实库和故事线，不能仅替换 demo 的输入文件后运行该脚本。

## 使用团队模板

提供原始 PPTX 模板与获准使用的参考 IM 页，并说明适用团队/地区版本。当前渲染器支持的布局有限，应用完整模板可能需要扩展转换程序。三页样张和完整 10 页的 PDF 参考风格改版现已完成，原始 PPTX 母版匹配仍待模板提供；详见 [Issue #1](https://github.com/fqi2050/IM-Writer/issues/1)。

## 必遵循的 KPMG 报告参考风格

无需另行选择。Skill 每次生成都必须读取内置 [设计规则](../skills/mna-information-memo/references/advisory-design.md)，在故事板使用 `style_profile: "advisory-dense"`，并按报告的配色、表格、页脚、信息密度和阅读式布局编写内容。渲染器缺省采用此风格，并拒绝其他配置名。具体布局仍需根据证据编写，不能只换颜色。

有获准使用的原始 KPMG PPTX 模板时，进一步遵循其母版及字体。当前使用 Arial 替代专用字体，不包含原始报告、Logo 或专用字体，也不宣称官方认可。内置规则及最小格式示例随 skill 安装，不需要复制完整 demo 或原始参考 PDF。
