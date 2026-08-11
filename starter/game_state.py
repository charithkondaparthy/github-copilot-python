from __future__ import annotations

from typing import Any, Dict, List, Tuple

import sudoku_logic

CURRENT: Dict[str, Any] = {
    'puzzle': None,
    'solution': None,
    'hints_used': 0,
    'completed': False,
    'last_score': None,
}


def reset_current(puzzle: sudoku_logic.Board, solution: sudoku_logic.Board) -> None:
    """Initialize the current game state."""
    CURRENT.update(
        {
            'puzzle': puzzle,
            'solution': solution,
            'hints_used': 0,
            'completed': False,
            'last_score': None,
        }
    )


def _validate_board_shape(board: Any) -> sudoku_logic.Board:
    if (
        not isinstance(board, list)
        or len(board) != sudoku_logic.SIZE
        or any(not isinstance(row, list) or len(row) != sudoku_logic.SIZE for row in board)
    ):
        raise ValueError('Invalid board shape')
    return board


def validate_final_board(board: Any) -> sudoku_logic.Board:
    board = _validate_board_shape(board)
    for row in board:
        for value in row:
            if not isinstance(value, int) or not (1 <= value <= sudoku_logic.SIZE):
                raise ValueError('Final board must be fully filled with 1-9')
    return board


def get_incorrect_cells(board: Any, solution: sudoku_logic.Board) -> List[List[int]]:
    board = _validate_board_shape(board)
    incorrect: List[List[int]] = []
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            value = board[i][j]
            if not isinstance(value, int) or not (0 <= value <= sudoku_logic.SIZE):
                raise ValueError('Invalid board values')
            if value == 0:
                if solution[i][j] != 0:
                    incorrect.append([i, j])
            elif value != solution[i][j]:
                incorrect.append([i, j])
    return incorrect


def parse_elapsed(payload: Any) -> int:
    if not isinstance(payload, dict) or 'elapsed' not in payload:
        raise ValueError('Missing elapsed time')
    try:
        elapsed_int = int(payload['elapsed'])
    except Exception:
        raise ValueError('Invalid elapsed value')
    if elapsed_int < 0:
        raise ValueError('Invalid elapsed value')
    return elapsed_int
