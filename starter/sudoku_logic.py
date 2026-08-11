from __future__ import annotations

import copy
import random
from typing import List, Tuple, Union

SIZE = 9
EMPTY = 0


Board = List[List[int]]


def deep_copy(board: Board) -> Board:
    """Return a deep copy of the board."""
    return copy.deepcopy(board)


def create_empty_board() -> Board:
    """Create and return an empty SIZE x SIZE Sudoku board."""
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]


def is_safe(board: Board, row: int, col: int, num: int) -> bool:
    """Check whether placing `num` at (row, col) violates Sudoku constraints.

    This checks the row, column and 3x3 box.
    """
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True


def _possible_values(board: Board, row: int, col: int) -> List[int]:
    """Return a list of possible values for a cell (unsorted).

    Used by the solver and generation algorithms.
    """
    if board[row][col] != EMPTY:
        return []
    return [n for n in range(1, SIZE + 1) if is_safe(board, row, col, n)]


def _find_empty_mrv(board: Board) -> Tuple[int, int] | None:
    """Find an empty cell using Minimum Remaining Values heuristic.

    Returns a tuple (row, col) or None if board is complete.
    """
    best = None
    best_count = SIZE + 1
    for r in range(SIZE):
        for c in range(SIZE):
            if board[r][c] == EMPTY:
                candidates = _possible_values(board, r, c)
                if len(candidates) < best_count:
                    best_count = len(candidates)
                    best = (r, c)
                    if best_count == 1:
                        return best
    return best


def solve_board(board: Board) -> bool:
    """Solve the Sudoku board in-place using backtracking.

    Returns True if solved, False if no solution exists.
    """
    pos = _find_empty_mrv(board)
    if pos is None:
        return True
    row, col = pos
    for val in _possible_values(board, row, col):
        board[row][col] = val
        if solve_board(board):
            return True
        board[row][col] = EMPTY
    return False


def count_solutions(board: Board, max_solutions: int = 2) -> int:
    """Count solutions for `board` using backtracking, stopping at `max_solutions`.

    This function does not modify the provided board.
    """
    b = deep_copy(board)
    count = 0

    def _search() -> bool:
        nonlocal count, b
        if count >= max_solutions:
            return True
        pos = _find_empty_mrv(b)
        if pos is None:
            count += 1
            return False
        row, col = pos
        for val in _possible_values(b, row, col):
            b[row][col] = val
            stop = _search()
            b[row][col] = EMPTY
            if stop:
                return True
        return False

    _search()
    return count


def _fill_board_random(board: Board) -> bool:
    """Fill the board completely with a valid solution (in-place).

    Uses randomized backtracking to produce varied full boards.
    """
    pos = _find_empty_mrv(board)
    if pos is None:
        return True
    row, col = pos
    candidates = _possible_values(board, row, col)
    random.shuffle(candidates)
    for val in candidates:
        board[row][col] = val
        if _fill_board_random(board):
            return True
        board[row][col] = EMPTY
    return False


DIFFICULTY_LEVELS = {
    'easy': 45,
    'medium': 35,
    'hard': 25,
}


def generate_puzzle(clues: Union[int, str] = 35) -> Tuple[Board, Board]:
    """Generate a puzzle with the requested number of `clues` or difficulty.

    `clues` may be an integer number of prefilled cells or one of the
    difficulty strings: 'easy', 'medium', 'hard'. Returns a tuple
    `(puzzle, solution)` where `solution` is the completed board and `puzzle`
    is the board with removed cells. The generator tries to preserve
    uniqueness of the solution; if it cannot remove enough cells it will
    return the closest valid puzzle.
    """
    if isinstance(clues, str):
        key = clues.lower()
        if key not in DIFFICULTY_LEVELS:
            raise ValueError(f"unknown difficulty: {clues}")
        clues = DIFFICULTY_LEVELS[key]

    if not isinstance(clues, int) or not 0 <= clues <= SIZE * SIZE:
        raise ValueError("clues must be between 0 and 81")

    board = create_empty_board()
    _fill_board_random(board)
    solution = deep_copy(board)

    # Create list of all cell positions and try removing while preserving uniqueness
    positions = [(r, c) for r in range(SIZE) for c in range(SIZE)]
    random.shuffle(positions)

    # We want exactly `clues` non-empty cells; start with full board and remove
    target_removals = SIZE * SIZE - clues
    removals = 0

    for (r, c) in positions:
        if removals >= target_removals:
            break
        saved = board[r][c]
        board[r][c] = EMPTY
        sols = count_solutions(board, max_solutions=2)
        if sols == 1:
            removals += 1
        else:
            board[r][c] = saved

    puzzle = deep_copy(board)
    return puzzle, solution


def remove_cells(board: Board, clues: int) -> None:
    """Backward compatible helper; modifies board in-place by removing random cells.

    This function is less careful than `generate_puzzle` and kept for
    compatibility only.
    """
    attempts = SIZE * SIZE - clues
    while attempts > 0:
        r = random.randrange(SIZE)
        c = random.randrange(SIZE)
        if board[r][c] != EMPTY:
            board[r][c] = EMPTY
            attempts -= 1


def provide_hint(puzzle: Board, solution: Board) -> Tuple[int, int, int] | None:
    """Fill one currently empty cell in `puzzle` using `solution`.

    Modifies `puzzle` in-place and returns a tuple `(row, col, value)` for
    the hinted cell. Returns `None` if there are no empty cells.
    """
    empties = [(r, c) for r in range(SIZE) for c in range(SIZE) if puzzle[r][c] == EMPTY]
    if not empties:
        return None
    r, c = random.choice(empties)
    val = solution[r][c]
    puzzle[r][c] = val
    return r, c, val

