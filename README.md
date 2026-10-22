# IM Writer

将客户的非结构化资料整理成有来源依据的 Information Memorandum 初稿，输出 HTML 和可编辑 PowerPoint。

仓库包含可复用的 Codex skill，以及虚构公司 **Northbridge Field Services 的 10 页英文 sell-side IM**。所有示例公司、人物和业务数据均为虚构。

## 先选择你要做的事

| 目的 | 从这里开始 | 需要什么 |
| --- | --- | --- |
| 查看 demo | 下载后打开 `START_HERE.html` | 浏览器；查看 PPT 需要 PowerPoint 或兼容软件 |
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
  outputs/                      HTML、可编辑 PPTX、复核说明
  scripts/                      仅用于该模拟案例的生成与复跑程序
  tests/                        检查程序和已保存的验证结果
```

`inputs`、`working`、`outputs` 是同一流程的不同阶段；HTML 与 PPT 是不同交付格式，均需保留。通用转换程序放在 `skills/`，模拟案例的专用程序放在 `demo-northbridge/scripts/`。

## 后续模板改版

当前版式用于验证流程。下一阶段使用团队提供的 KPMG 原始 PPTX 模板和获准使用的脱敏 IM 参考页，减少套话、调整版式及信息密度。详细需求见 [Issue #1](https://github.com/fqi2050/IM-Writer/issues/1)。模板尚未加入仓库，当前示例不代表 KPMG 官方模板或认可。

本仓库仅包含虚构示范内容；真实客户资料和受限模板请保存在获准访问的位置。
