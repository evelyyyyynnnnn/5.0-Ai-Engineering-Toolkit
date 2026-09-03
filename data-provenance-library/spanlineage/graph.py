"""Walking a tracked value's derivation."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LineageGraph:
    nodes: list
    edges: list

    def depth(self) -> int:
        depths = {}

        def d(n):
            if id(n) in depths:
                return depths[id(n)]
            depths[id(n)] = 0 if not n.inputs else 1 + max(d(i) for i in n.inputs)
            return depths[id(n)]

        return max((d(n) for n in self.nodes), default=0)

    def leaves(self) -> list:
        return [n for n in self.nodes if not n.inputs]

    def stats(self) -> dict:
        return {"n_nodes": len(self.nodes), "n_edges": len(self.edges),
                "depth": self.depth(), "n_leaves": len(self.leaves()),
                "ops": sorted({n.op for n in self.nodes})}


def build_graph(value) -> LineageGraph:
    nodes, edges, seen = [], [], set()

    def walk(n):
        if id(n) in seen:
            return
        seen.add(id(n))
        nodes.append(n)
        for i in n.inputs:
            edges.append((id(i), id(n)))
            walk(i)

    walk(value)
    return LineageGraph(nodes=nodes, edges=edges)


def explain(value, sources: dict, max_depth: int = 6) -> list:
    """A readable derivation, root first."""
    out = []

    def walk(n, depth):
        if depth > max_depth:
            return
        ev = n.evidence(sources) if not n.inputs else []
        out.append({"depth": depth, "op": n.op, "value": n.value,
                    "note": n.note,
                    "evidence": [e["text"] for e in ev if e["text"]]})
        for i in n.inputs:
            walk(i, depth + 1)

    walk(value, 0)
    return out


def to_dot(value) -> str:
    """Graphviz source, for looking at a derivation that got complicated."""
    g = build_graph(value)
    lines = ["digraph lineage {", "  rankdir=BT;", "  node [shape=box];"]
    for n in g.nodes:
        label = f"{n.op}\\n{n.value}"
        lines.append(f'  n{id(n)} [label="{label}"];')
    for a, b in g.edges:
        lines.append(f"  n{a} -> n{b};")
    lines.append("}")
    return "\n".join(lines)
