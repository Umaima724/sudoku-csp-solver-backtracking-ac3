import copy
from collections import deque

calls    = 0
failures = 0


def read_puzzle(filename):
    grid = []
    with open(filename) as f:
        for line in f:
            digits = [int(ch) for ch in line.strip() if ch.isdigit()]
            if digits:
                grid.append(digits)
    return grid


def build_candidates(grid):
    candidates = {}
    for row in range(9):
        for col in range(9):
            if grid[row][col] != 0:
                candidates[(row, col)] = {grid[row][col]}
            else:
                candidates[(row, col)] = set(range(1, 10))
    return candidates


def neighbours(cell):
    row, col = cell
    peers = set()

    for c in range(9):
        if c != col:
            peers.add((row, c))

    for r in range(9):
        if r != row:
            peers.add((r, col))

    box_row = (row // 3) * 3
    box_col = (col // 3) * 3
    for r in range(box_row, box_row + 3):
        for c in range(box_col, box_col + 3):
            if (r, c) != cell:
                peers.add((r, c))

    return peers


def remove_impossible(candidates, cell_a, cell_b):
    removed = False
    if len(candidates[cell_b]) == 1:
        fixed_number = list(candidates[cell_b])[0]
        if fixed_number in candidates[cell_a]:
            candidates[cell_a].discard(fixed_number)
            removed = True
    return removed


def ac3(candidates):
    queue = deque()
    for cell in candidates:
        for peer in neighbours(cell):
            queue.append((cell, peer))

    while queue:
        cell_a, cell_b = queue.popleft()
        if remove_impossible(candidates, cell_a, cell_b):
            if len(candidates[cell_a]) == 0:
                return False
            for peer in neighbours(cell_a):
                if peer != cell_b:
                    queue.append((peer, cell_a))

    return True


def pick_cell(candidates):
    unsolved = [(cell, cands)
                for cell, cands in candidates.items()
                if len(cands) > 1]
    if not unsolved:
        return None
    unsolved.sort(key=lambda x: len(x[1]))
    return unsolved[0][0]


def backtrack(candidates):
    global calls, failures
    calls += 1

    if all(len(cands) == 1 for cands in candidates.values()):
        return candidates

    cell = pick_cell(candidates)
    if cell is None:
        return candidates

    for number in sorted(candidates[cell]):
        new_candidates = copy.deepcopy(candidates)
        new_candidates[cell] = {number}

        ok = True
        for peer in neighbours(cell):
            new_candidates[peer].discard(number)
            if len(new_candidates[peer]) == 0:
                ok = False
                break

        if ok and ac3(new_candidates):
            result = backtrack(new_candidates)
            if result is not None:
                return result

    failures += 1
    return None


def solve(grid):
    global calls, failures
    calls = 0
    failures = 0

    candidates = build_candidates(grid)

    if not ac3(candidates):
        return None

    result = backtrack(candidates)
    if result is None:
        return None

    solved_grid = [[0] * 9 for _ in range(9)]
    for (row, col), cands in result.items():
        solved_grid[row][col] = list(cands)[0]

    return solved_grid


def show(grid, title=""):
    if title:
        print(f"\n{'─'*31}  {title}")
    print("+-------+-------+-------+")
    for r in range(9):
        line = "| "
        for c in range(9):
            line += str(grid[r][c]) + " "
            if (c + 1) % 3 == 0:
                line += "| "
        print(line)
        if (r + 1) % 3 == 0:
            print("+-------+-------+-------+")


if __name__ == "__main__":
    puzzles = [
        ("easy.txt",     "Easy"),
        ("medium.txt",   "Medium"),
        ("hard.txt",     "Hard"),
        ("veryhard.txt", "Very Hard"),
    ]

    print("\nSudoku CSP Solver  -  Backtracking + AC-3 + Forward Checking\n")

    summary = []

    for filename, label in puzzles:
        try:
            grid = read_puzzle(filename)
        except FileNotFoundError:
            print(f"  [{label}] File not found: {filename}\n")
            continue

        show(grid, f"INPUT  ({label})")
        solution = solve(grid)

        if solution:
            show(solution, f"SOLVED ({label})")
        else:
            print(f"  No solution found for {label}.\n")
            continue

        if calls < 10:
            note = "AC-3 alone solved it - no real search needed."
        elif calls < 100:
            note = "Tiny bit of search - constraints did most of the work."
        elif calls < 1000:
            note = "Moderate search - puzzle genuinely needed exploration."
        else:
            note = "Heavy search - very few given clues, many possibilities."

        print(f"  Backtrack calls  : {calls}")
        print(f"  Backtrack fails  : {failures}")
        print(f"  Note             : {note}\n")

        summary.append((label, calls, failures, note))

    print("=" * 65)
    print(f"  {'Board':<12} {'Calls':>8} {'Failures':>10}   Note")
    print("=" * 65)
    for label, c, f, note in summary:
        print(f"  {label:<12} {c:>8} {f:>10}   {note}")
    print("=" * 65)