# Evidence and traceability

Use a JSON object with `sources`, `facts`, `calculations`, `issues` and `slide_claims`.

A source records ID, relative path, SHA-256, version/date when known, extraction status and locators. DOCX paragraph numbers count nonempty body paragraphs from 1; table cells have separate table/row/column locators. XLSX uses sheet names and A1 addresses, with formula text and cached values preserved. Text/email uses line numbers. A locator should still be usable without the pipeline.

A fact records `id`, `claim`, `raw_value`, `value`, `unit`, `period`, `basis` (actual, forecast, management assertion, proposal), `scope`, `source_refs`, `status` and `limitations`. Supported statuses: source_supported, provisional_conflict, management_unverified, missing. Source-supported means supported by the supplied file, not independently audited. Synthetic examples have an additional `synthetic: true` flag.

A calculation records `id`, formula, input IDs/source references, result, unit and rounding. Reuse the result across HTML, slide titles, tables and charts. Preserve full precision until display.

An issue records ID, severity, competing values/references or missing evidence, treatment in draft, requested evidence and proposed owner role. Do not invent a resolved status or an actual assigned owner.

A slide_claim records slide number, element ID, fact IDs, calculation IDs and source references. Table/chart cells can be covered by a precise source range plus a calculation definition. Claims added while writing must be added to the ledger.

Avoid numerical confidence scores without a calibrated method. Actual/forecast, currency, unit and entity scope cannot be inferred from formatting alone. Ask or mark unknown. Customer aggregates must not be treated as individual customers.
