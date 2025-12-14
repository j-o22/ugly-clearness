"""
This work uses Pythonic materials (data types, generators, exceptions,
context managers, metaprogramming, hashing, non-determinism) to inscribe
a contemplation on dialogue without quoting it.
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Dict, Iterable, Iterator, List, Optional, Set, Tuple, Type
import contextlib
import itertools as it
import math
import os
import random
import sys
import time
import uuid

random.seed(113)  # deterministic enough to be revisited

# ==============================
# I. PRIMITIVES
# ==============================

@dataclass(frozen=True)
class Mark:
    """A single inscription on an abstract plane."""
    x: int
    y: int
    tone: float        # weight in [0,1]
    tag: str           # 'ask','answer','turn','doubt','care','resolve','gap'

@dataclass
class Layer:
    marks: List[Mark] = field(default_factory=list)
    def add(self, *m: Mark) -> None:
        self.marks.extend(m)

@dataclass
class Field:
    width: int
    height: int
    layers: List[Layer] = field(default_factory=list)

    def deposit(self, layer: Layer) -> None:
        self.layers.append(layer)

    def render(self, legend: bool = True) -> str:
        # Compose layers by tone; higher tone overrides
        grid: List[List[Tuple[float, str]]] = [[(0.0, ' ') for _ in range(self.width)] for _ in range(self.height)]
        for layer in self.layers:
            for m in layer.marks:
                if 0 <= m.x < self.width and 0 <= m.y < self.height:
                    old_tone, old_ch = grid[m.y][m.x]
                    if m.tone >= old_tone:
                        grid[m.y][m.x] = (m.tone, symbol(m.tag, m.tone))
        lines = [''.join(ch for _, ch in row).rstrip() for row in grid]
        s = '\n'.join(lines)
        if legend:
            s += "\n legend: " + '  '.join(f"{symbol(t,0.7)}={t}" for t in ORDER if t != 'gap')
        return s

# ==============================
# II. LEXICON
# ==============================

ORDER = ['gap','ask','answer','turn','doubt','care','resolve']

PALETTE = {
    'gap'    : ' ',
    'ask'    : '·',
    'answer' : '—',
    'turn'   : '∧',
    'doubt'  : '~',
    'care'   : '*',
    'resolve': '∎',
}

def symbol(tag: str, tone: float) -> str:
    base = PALETTE.get(tag, '?')
    k = 1 + int(max(0.0, min(1.0, tone)) * 2)
    return base * k

# ==============================
# III. DYNAMICS (non-musical transformations)
# ==============================

class Expectation:
    """A scalar that, when lowered, reveals more of what already was."""
    def __init__(self, level: float = 1.0) -> None:
        self.level = level
    def lower(self, by: float) -> None:
        self.level = max(0.0, self.level - by)

@contextlib.contextmanager
def without(burden: str) -> Iterator[None]:
    """Context where a burden is named, acknowledged, and set aside."""
    # We keep no global state; the act is ceremonial.
    _ = burden  # binding gives it form; release gives it air.
    try:
        yield
    finally:
        pass

class Misunderstanding(Exception):
    """Raised internally to mark a discontinuity of sense."""

def perturb(x: int, y: int, seed: int) -> Tuple[int, int]:
    """Small deterministic drift; not noise, a reminder."""
    r = (seed * 6364136223846793005 + 1) & 0xFFFFFFFF
    dx = (r >> 8) % 3 - 1
    dy = (r >> 16) % 3 - 1
    return x + dx, y + dy

def fold_trace(trace: Iterable[str]) -> int:
    """Hash-like folding of a tag trace into a compact coordinate bias."""
    h = 0
    for t in trace:
        h = ((h << 5) - h) ^ (ord(t[0]) if t else 0)
    return h

# ==============================
# IV. MAKERS (constructive idioms)
# ==============================

def inscribe(field: Field, origin: Tuple[int,int], steps: int, tag: str, stride: int = 1, tone: float = 0.5) -> Layer:
    """Draw a directed path by writing Marks, bending gently when stressed."""
    ox, oy = origin
    layer = Layer()
    x, y = ox, oy
    for i in range(steps):
        px, py = perturb(x, y, i + fold_trace([tag]))
        layer.add(Mark(px, py, tone, tag))
        # torsion: tag influences direction without "being" direction
        if tag == 'ask':
            x += stride; y -= (i % 2 == 0)
        elif tag == 'answer':
            x += stride; y += (i % 3 == 0)
        elif tag == 'turn':
            x += (1 if i % 2 == 0 else 0); y += (1 if i % 2 else -1)
        elif tag == 'doubt':
            x += stride; y += (1 if (i//2) % 2 else -1)
        elif tag == 'care':
            x += stride; y += 0
        elif tag == 'resolve':
            x += stride; y += (0 if i else 0)
        else:
            x += stride
    field.deposit(layer)
    return layer

def braid(*layers: Layer) -> Layer:
    """Composite layer where later marks override earlier by tone."""
    merged = Layer()
    bag: Dict[Tuple[int,int], Mark] = {}
    for layer in layers:
        for m in layer.marks:
            key = (m.x, m.y)
            if key not in bag or bag[key].tone <= m.tone:
                bag[key] = m
    merged.marks = list(bag.values())
    return merged

# ==============================
# V. METAPATTERN (metaclass as quiet signature)
# ==============================

class Signature(type):
    def __new__(mcls, name, bases, ns, token=None):
        ns['_token'] = token or uuid.uuid4().hex[:8]
        return super().__new__(mcls, name, bases, ns)

class Witness(metaclass=Signature, token="silent"):
    """Exists only to remind us that form carries an unseen key."""
    def key(self) -> str:
        return self._token

# ==============================
# VI. SCENES (No quotes; comments indicate prompt/answer)
# ==============================

def scene(field: Field) -> None:
    E = Expectation(1.0)

    # --- Scene A ---------------------------------------------
    # Prompt A: (on difficulty of being understood)
    with without("demand to be mirrored"):
        inscribe(field, origin=(2, 3),  steps=22, tag='ask', stride=1, tone=0.45)
    # Answer A: (on resonance instead of replication)
    with without("defensiveness"):
        inscribe(field, origin=(4, 5),  steps=20, tag='answer', stride=1, tone=0.60)

    # --- Scene B ---------------------------------------------
    # Prompt B: (gentle approach; dropping expectation)
    E.lower(0.25)
    with without("insistence"):
        inscribe(field, origin=(8, 7),  steps=14, tag='turn', stride=1, tone=0.70)
    # Answer B: (leave a door open)
    inscribe(field, origin=(10, 7), steps=12, tag='care', stride=1, tone=0.40)

    # --- Scene C ---------------------------------------------
    # Prompt C: (no obligation to be understood)
    with without("transaction"):
        inscribe(field, origin=(16, 9), steps=6,  tag='resolve', stride=2, tone=0.90)
    # Answer C: (difference as condition, not error)
    inscribe(field, origin=(17, 6), steps=18, tag='answer', stride=1, tone=0.55)

    # --- Scene D ---------------------------------------------
    # Prompt D: (clarity that erases illusions)
    with without("ornament"):
        inscribe(field, origin=(22, 8), steps=16, tag='doubt', stride=1, tone=0.50)
    # Answer D: (naming, then resting)
    inscribe(field, origin=(23, 8), steps=10, tag='care', stride=1, tone=0.45)

    # --- Afterword -------------------------------------------
    inscribe(field, origin=(30, 9), steps=4, tag='resolve', stride=2, tone=0.90)

# ==============================
# VII. RENDERING
# ==============================

def draw(field: Field) -> str:
    return field.render(legend=True)

# ==============================
# VIII. EXECUTION
# ==============================

def main(argv: List[str]) -> int:
    W, H = 84, 20
    f = Field(W, H)
    try:
        scene(f)
    except Misunderstanding:
        # Even a controlled failure leaves a readable residue.
        pass
    # a quiet metapoint: the class carries a key we never use
    w = Witness()
    print("— python inscription —", w.key(), "\n")
    print(draw(f))
    print("\n(There is no center here. Only traces that refuse to become a map.)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
