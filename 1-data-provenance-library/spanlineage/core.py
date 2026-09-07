"""Tracked values and span propagation."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Source:
    doc_id: str
    text: str

    @property
    def sha(self) -> str:
        return hashlib.sha256(self.text.encode()).hexdigest()[:16]

    def slice(self, start: int, end: int) -> str:
        return self.text[start:end]


@dataclass(frozen=True)
class Span:
    doc_id: str
    start: int
    end: int
    doc_sha: str = ""

    def __len__(self) -> int:
        return self.end - self.start

    def as_dict(self) -> dict:
        return {"doc_id": self.doc_id, "start": self.start, "end": self.end,
                "doc_sha": self.doc_sha}


@dataclass
class Tracked:
    """A value plus the spans that produced it, plus how it got here.

    Operations return new Tracked values whose spans are the union of their
    inputs'. That union is deliberately lossy about *which* input contributed
    what -- it records that the result depends on all of them, which is the
    question an auditor asks. Attributing a share of a sum to each input is a
    different question, and pretending a span set answers it would be worse than
    not answering.
    """

    value: object
    spans: tuple = ()
    op: str = "extract"
    inputs: tuple = ()
    note: str = ""

    # --- construction -----------------------------------------------------

    def derive(self, value, op: str, others=(), note: str = "") -> "Tracked":
        spans = list(self.spans)
        for o in others:
            if isinstance(o, Tracked):
                spans.extend(o.spans)
        return Tracked(value=value, spans=tuple(dict.fromkeys(spans)), op=op,
                       inputs=(self,) + tuple(o for o in others
                                              if isinstance(o, Tracked)),
                       note=note)

    # --- arithmetic -------------------------------------------------------

    def _binop(self, other, fn, name):
        ov = other.value if isinstance(other, Tracked) else other
        return self.derive(fn(self.value, ov), name,
                           (other,) if isinstance(other, Tracked) else ())

    def __add__(self, o):
        return self._binop(o, lambda a, b: a + b, "add")

    def __radd__(self, o):
        return self._binop(o, lambda a, b: b + a, "add")

    def __sub__(self, o):
        return self._binop(o, lambda a, b: a - b, "sub")

    def __mul__(self, o):
        return self._binop(o, lambda a, b: a * b, "mul")

    def __rmul__(self, o):
        return self._binop(o, lambda a, b: b * a, "mul")

    def __truediv__(self, o):
        return self._binop(o, lambda a, b: a / b, "div")

    def __neg__(self):
        return self.derive(-self.value, "neg")

    # --- comparison (untracked: a bool is not a provenanced value) --------

    def __eq__(self, o):
        return self.value == (o.value if isinstance(o, Tracked) else o)

    def __lt__(self, o):
        return self.value < (o.value if isinstance(o, Tracked) else o)

    def __hash__(self):
        return hash((id(self),))

    def __repr__(self):
        return f"Tracked({self.value!r}, {len(self.spans)} span(s), op={self.op})"

    def apply(self, fn, name: str | None = None, note: str = "") -> "Tracked":
        """Lift an arbitrary function while keeping the spans."""
        return self.derive(fn(self.value), name or getattr(fn, "__name__", "apply"),
                           note=note)

    def evidence(self, sources: dict) -> list:
        out = []
        for sp in self.spans:
            src = sources.get(sp.doc_id)
            out.append({"span": sp.as_dict(),
                        "text": src.slice(sp.start, sp.end) if src else None})
        return out


def track(value, source: Source, start: int, end: int, note: str = "") -> Tracked:
    return Tracked(value=value,
                   spans=(Span(source.doc_id, start, end, source.sha),),
                   op="extract", note=note)


def untrack(x):
    return x.value if isinstance(x, Tracked) else x


def extract(source: Source, pattern: str, cast=float, group: int = 1,
            note: str = "") -> Tracked | None:
    """Regex extraction that records the matched span automatically."""
    m = re.search(pattern, source.text, re.I)
    if not m:
        return None
    raw = m.group(group)
    try:
        value = cast(raw.replace(",", "")) if cast in (float, int) else cast(raw)
    except (TypeError, ValueError):
        return None
    return track(value, source, m.start(group), m.end(group),
                 note=note or f"matched {pattern!r}")
