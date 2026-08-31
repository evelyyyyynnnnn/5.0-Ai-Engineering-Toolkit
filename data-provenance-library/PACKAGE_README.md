# spanlineage

Values that remember where they came from.

A pipeline extracts a number from a document, transforms it four times, and lands
it in a report. When someone disputes the number, nobody can say which characters
produced it. Logging the extraction does not help — the transformations are where
the value actually changed.

`spanlineage` makes provenance a property of the **value** rather than of the
pipeline. Arithmetic propagates source spans, so the final number knows every
span that contributed to it without any code in between threading anything
through by hand.

## Install

```bash
pip install spanlineage
```

Python 3.9+. No dependencies.

## Thirty seconds

```python
import spanlineage as L

src  = L.Source("FILING-2024", "Total revenue was 1,284,500 and cost of revenue was 742,100.")
rev  = L.extract(src, r"revenue was ([\d,]+)")
cost = L.extract(src, r"cost of revenue was ([\d,]+)")

margin = (rev - cost) / rev

print(margin.value)                                   # 0.4223...
print([e["text"] for e in margin.evidence({"FILING-2024": src})])
# ['1,284,500', '742,100']
```

The margin is three transformations deep and still points at the characters
underneath it.

## Across documents

Spans carry their document id, so a metric built from two sources knows both:

```python
opex          = L.extract(filing, r"Operating expenses totalled ([\d,]+)")
restructuring = L.extract(notes,  r"restructuring charge of ([\d,]+)")
adjusted      = opex - restructuring

{s.doc_id for s in adjusted.spans}   # {'FILING-2024', 'NOTES-2024'}
```

## Verification

Each span records a hash of its source document, so a record notices when the
document moves underneath it:

```python
report = L.verify_against(margin, {"FILING-2024": src})
print(report["ok"])                  # True

edited = L.Source("FILING-2024", src.text.replace("1,284,500", "1,384,500"))
print(L.verify_against(margin, {"FILING-2024": edited})["problems"])
# [{'issue': 'document has changed', ...}]
```

Two failure modes are reported separately, because they mean different things: a
changed hash means the *source* moved; an out-of-bounds span means the *record*
is wrong. Only one of those is the pipeline's fault.

## Explaining a derivation

```python
from spanlineage import explain, to_dot

for step in explain(margin, sources):
    print("  " * step["depth"], step["op"], step["value"], step["evidence"])

open("lineage.dot", "w").write(to_dot(margin))   # graphviz
```

## Command line

```bash
spanlineage extract filing.txt 'revenue was ([0-9,]+)'
spanlineage verify  filing.txt record.json
```

## What a span set does and does not say

The union records that a result *depends on* all of these spans. It deliberately
does not say which input contributed how much — that is an attribution question,
and a span set pretending to answer it would be worse than not answering.

## Limitations

- Propagation covers arithmetic and lifted single-argument functions.
  Aggregations, joins and group-bys are not implemented, and real pipelines
  spend most of their time there.
- Every operation widens the span set, so a value derived from many extractions
  cites all of them. Correct, and not very useful at scale.
- Spans index into plain text. No PDF, OCR or layout handling.
- Verification detects a changed document; it does not tell you whether the new
  document would change the answer.

## Licence

MIT.
