import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import sudoku_logic


def _is_valid_complete_board(board):
    if len(board) != 9 or any(len(row) != 9 for row in board):
        return False

    expected = set(range(1, 10))

    for row in board:
        if set(row) != expected:
            return False

    for col in range(9):
        column_values = [board[row][col] for row in range(9)]
        if set(column_values) != expected:
            return False

    for box_row in range(0, 9, 3):
        for box_col in range(0, 9, 3):
            values = [
                board[row][col]
                for row in range(box_row, box_row + 3)
                for col in range(box_col, box_col + 3)
            ]
            if set(values) != expected:
                return False

    return True


def test_flask_app_can_start():
    app_module = importlib.import_module("app")

    assert app_module.app is not None
    assert app_module.app.name == "app"


def test_root_route_returns_http_200():
    app_module = importlib.import_module("app")
    client = app_module.app.test_client()

    response = client.get("/")

    assert response.status_code == 200


def test_sudoku_board_generator_produces_valid_9x9_board():
    puzzle, solution = sudoku_logic.generate_puzzle(35)

    assert len(puzzle) == 9
    assert len(solution) == 9
    assert all(len(row) == 9 for row in puzzle)
    assert all(len(row) == 9 for row in solution)
    assert _is_valid_complete_board(solution)


def test_existing_sudoku_functionality_still_works():
    board = sudoku_logic.create_empty_board()
    assert len(board) == 9
    assert all(len(row) == 9 for row in board)
    assert all(cell == 0 for row in board for cell in row)

    assert sudoku_logic.is_safe(board, 0, 0, 1)

    copied_board = sudoku_logic.deep_copy(board)
    assert copied_board == board

    puzzle, solution = sudoku_logic.generate_puzzle(35)
    assert puzzle is not None
    assert solution is not None
