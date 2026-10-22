# Consulting report design: PDF-derived profile

This is the mandatory design reference for IMs created with this skill. Apply it on every run, including when the user only supplies source materials and does not repeat the style request. The rules and profile are bundled inside the skill; the original PDF and repository pilot are not required at runtime. These are rules derived from the user-selected KPMG report, not an official brand manual. A supplied authorized native KPMG template takes precedence for exact master/layout matching.

## What was observed

The design profile was derived from a user-selected July 2023 benchmark-study PDF (July 2023, 189 pages, 960 × 540 PDF points, 16:9). Visual sampling covered PDF pages 5, 8, 17, 35, 45, 49, 75, 139, 144 and 153. These are page indices, not an assertion of reviewing all 189 pages. Reference PDF/images and business text are not bundled with this skill.

- Pages 8 and 49: charts with direct data labels, an explanatory title and nearby analysis; color differentiates series rather than decorating every block.
- Pages 35, 45 and 144: comparison matrices, aligned columns, selective light-blue row fills, narrow rules and specific commercial details.
- Pages 75, 139 and 153: composition changes with the evidence; maps, operating standards and organization charts use distinct structures. Rounded blocks appear in the source but are not a default for every IM page.
- Page 5: unusually dense executive summary, roughly 480 whitespace-separated words. Other sampled pages contain roughly 104–287 words, including labels and notes. This range describes the sample, not a target to fill.
- The reference uses condensed KPMG-Bold titles, Arial body text, predominantly white backgrounds, blue source notes and lower-right page numbers. Extracted body sizes are commonly 12–14 PDF points; source notes around 9.1. Do not transfer the extracted title size mechanically: the proprietary title face is unusually condensed.

## Palette and typography

Colors below are rounded RGB values extracted from PDF vector/text objects. They describe this document, not current official brand specifications.

| Role | Color | Application |
| --- | --- | --- |
| Primary blue | `#00338D` | Titles, section headings, main series and source notes |
| Secondary blue | `#1E49E2` | Secondary series or table headers |
| Cyan | `#00B8F5` | Limited secondary emphasis; avoid small text on white |
| Purple | `#7213EA` | A distinct comparison category when needed |
| Light blue | `#DBE8F8` | Table bands and selected analytical rows |
| Light grey | `#F2F2F2` | Neutral grouping |
| Black / white | `#000000` / `#FFFFFF` | Body text / background |

The executable defaults are in `assets/advisory-dense.json`. At this project's 1280 × 720 design scale, start with Arial title 32–36, body/table 16–19, subsection 20–22, source notes 12–13. These are implementation choices for an available substitute, not measured KPMG font sizes. Keep the header within about the top 18% and reserve a source/footer band. Use 64–80 side margins and 24–32 gutters as starting points. Allow a supported takeaway title two lines; don't force every title to be a claim.

Never extract or distribute proprietary fonts from a PDF. Use a supplied authorized font when available, otherwise disclose the substitute. Do not invent a KPMG logo, confidentiality wording, copyright footer or claim of approval. Label any synthetic examples visibly as fictional.

## Choose a layout by the question

| Page purpose | Useful composition | Evidence to preserve |
| --- | --- | --- |
| Investment case | Theme / supporting evidence / qualification matrix | Metric, period, commercial mechanism, diligence dependency |
| Business overview | Service comparison table plus concise operating context | Revenue and share, contract basis, customers/applications |
| Historical financials | P&L on left, analytical commentary on right | Units, actual/forecast, margin, reconciliation and source caveats |
| Customer quality | Concentration chart with contracts and cohort commentary | Denominator, top-customer share, limits of retention evidence |
| Forecast | Forecast table/chart with assumptions alongside | Hiring, renewals, pipeline support and actual/forecast labels |
| Diligence | Topic / current evidence / requested evidence matrix | Open issue, materiality and source owner where supplied |

Use a few aligned analytical regions with meaningful labels. Prefer flat tables and rules to repeated KPI cards. Use bullets only where the items are genuinely parallel. A well-designed data chart may have fewer words than a narrative page; allow that difference. If evidence is sparse, leave space or combine related content instead of inventing findings. Do not reproduce the source report's crowded summary as a blanket density standard.

## Reduce generic AI writing

Replace unqualified slogans such as “a resilient platform poised for growth” with evidence such as “Scheduled maintenance represents 60% of FY2025 revenue; renewal performance is not yet evidenced.” Use the actual client's values and sources; that example is illustrative, not a reusable fact.

For each page, ask: what can the reader verify, compare or decide? Remove repeated benefits, unsupported causal explanations, forced sets of three and adjectives that add no evidence. Preserve substantive caveats adjacent to the relevant figure. Do not turn “share of maintenance revenue” into ARR, or historical EBITDA into adjusted earnings. Visible source footers identify the new project's files and relevant sheets; full locators remain in speaker notes and the evidence ledger. Never copy “KPMG Analysis” from the reference as the provenance of newly authored work.

## Apply and verify

Always set storyboard `style_profile` to `advisory-dense`; use the profile's roles for explicit text colors/sizes and chart colors. The renderer uses the profile for default table styling and otherwise unspecified text/chart colors. It does not replace explicit old colors, move objects, write analysis or populate source footers automatically.

First validate investment case, business overview and financial analysis layouts against the user's materials. Use the bundled [format example](../assets/storyboard-example.json) when checking the semantic schema; author actual project layouts from the client evidence. Inspect rendered HTML and native PPT at the intended reading size. Before shrinking text, shorten repetition or rebalance columns. Keep all important financial rows, qualifications and source mappings. Native PPTX master matching remains a separate task once the original template is available.
