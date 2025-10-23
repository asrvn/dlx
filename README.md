# Dancing Links

A compact, dependency-free 9x9 Sudoku solver that reduces Sudoku to an *exact cover* problem and solves it with Donald Knuth’s **Algorithm X** implemented via **Dancing Links (DLX)**. Course rules restricted third-party and array libraries.

> Built November 2023 the Artificial Intelligence course at TJHSST. Kept as a reference implementation. I later replaced it with an optimized backtracking solver for performance reasons.

---
## Requirements

- **9×9 Sudoku**: (81 chars per puzzle).
- **Format:** Digits `1–9` for givens; `.` or `0` for blanks.
- **Input File:** A multiline .txt of puzzles, one per line.

---
## How it works

Sudoku is modeled as an exact-cover over four constraint families:

1. **Cell occupancy:** each (row, col) has exactly one value.  
2. **Row values:** each (row, value) appears exactly once.  
3. **Column values:** each (col, value) appears exactly once.  
4. **Block values:** each (block, value) appears exactly once.

The solver builds a sparse binary matrix with one row per candidate assignment and four `N²` columns (total `4N²` columns). DLX links nodes in four directions and uses the “smallest column” heuristic to choose the next constraint to cover.

---
## Usage

```bash
# Python ≥ 3.8 (due to walrus operator)
python solver.py path/to/puzzles.txt
```
