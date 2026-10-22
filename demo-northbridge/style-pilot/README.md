# 三页咨询报告式样张

这组三页沿用 Northbridge 的虚构证据，验证新增的 `advisory-dense` 设计配置。原始 10 页 demo 保留为基线。

- [HTML 样张](northbridge-advisory.html)：下载后本地打开。
- [可编辑 PPT](northbridge-advisory-editable.pptx)：三页均包含原生可编辑表格和文字。
- [设计规则](../../skills/mna-information-memo/references/advisory-design.md)：配色、密度、布局与写作原则。
- `storyboard.json`：三页的布局和事实引用；`claim-map.json`：映射到原有事实库的来源。

参考 PDF 的主蓝、浅蓝表格和阅读式布局；标题以 Arial 替代 KPMG 专用字体。它是参考报告的视觉近似，并非原始 PPTX 母版。样张依次为投资亮点、业务概览和历史财务。没有复用参考报告的业务数据、Logo 或字体文件。

运行 `demo-northbridge/scripts/build_style_pilot.py` 可从现有模拟事实库重建故事板；然后按通用渲染与转换流程输出 HTML/PPT，并执行 `demo-northbridge/tests/test_advisory_style.py`。若更新原始客户输入，先重建事实库；该脚本仍是固定模拟案例，不是通用客户分析器。

已验证原生表格样式、财务表显示值计算、来源映射和文件结构。桌面 PowerPoint 的实际编辑、保存和重开尚未实测。
