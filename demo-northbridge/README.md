# Northbridge 模拟案例

[返回仓库首页](../README.md) · [打开本地入口](../START_HERE.html)

Northbridge Field Services 是虚构的英国 B2B 维护服务公司。本案例用 10 页英文 sell-side IM 验证资料提取、来源追溯、HTML 与可编辑 PPT 生成流程。所有人物和业务数据均为虚构，不应复用为真实客户陈述。

## 查看成品

- [HTML IM](outputs/northbridge-im.html)：下载后用浏览器打开。
- [可编辑 PowerPoint](outputs/northbridge-im-editable.pptx)：下载后用 PowerPoint 打开。
- [复核说明](outputs/review-notes.html)：数据问题及验证范围。

## 文件如何对应

| 目录 | 内容 | 用途 |
| --- | --- | --- |
| `inputs/` | 公司简介 Word、管理层模型 Excel、访谈、CFO 邮件 | 模拟客户原始资料 |
| `working/` | 清单、提取结果、事实库、问题清单、故事板 | 核查每个重要结论的来源及计算 |
| `outputs/` | HTML、PPTX、复核说明 | 阅读、演示和审阅 |
| `scripts/` | 案例资料生成、故事板构建、复跑和最终处理 | 开发时重放固定案例 |
| `tests/` | 检查程序及保存的检查结果 | 记录和复核验证范围 |

本例故意保留收入口径冲突（FY2025 模型 £25.0m、旧简介 £26.2m）、GBP million 与 thousand 的单位差异，以及缺乏定义的 94% 留存率。市场规模、市场份额、QoE、现金、债务和标准化营运资金等证据缺失；这些问题应进入复核流程，不应自动补成事实。

需要重跑时参见 [开发说明](../docs/development.md)。真实客户项目参见 [Skill 使用指南](../docs/skill-usage.md)，请使用独立项目目录。
