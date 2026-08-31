"""lineage — values that remember where they came from.

The problem: a pipeline extracts a number from a document, transforms it four
times, and lands it in a report. When someone disputes the number, nobody can
say which characters produced it. Logging the extraction does not help, because
the transformations are where the value actually changed.

This library makes provenance a property of the VALUE rather than of the
pipeline. A `Tracked` value carries its source spans, and arithmetic on tracked
values propagates them, so the final number knows every span that contributed to
it -- without the pipeline having to thread anything through by hand.
"""

from .core import (Source, Span, Tracked, extract, track, untrack)
from .graph import LineageGraph, explain, to_dot
from .verify import VerificationError, verify_against

__version__ = "0.1.0"

__all__ = ["Source", "Span", "Tracked", "extract", "track", "untrack",
           "LineageGraph", "explain", "to_dot",
           "VerificationError", "verify_against", "__version__"]
