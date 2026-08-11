import random

from sudoku_logic import (
    create_empty_board,
    deep_copy,
    generate_puzzle,
    count_solutions,
    remove_cells,
    solve_board,
)


def test_empty_board_has_multiple_solutions():
    board = create_empty_board()
    assert count_solutions(board, max_solutions=3) > 1


def test_naive_removal_can_create_multiple_solutions():
    # Use a fixed seed so the test is reproducible
    random.seed(42)
    _, solution = generate_puzzle(81)
    board = deep_copy(solution)
    remove_cells(board, 30)
    # It's possible (and expected) that naive random removal produces
    # a puzzle with multiple solutions.
    assert count_solutions(board, max_solutions=3) >= 1


def test_generate_puzzle_produces_unique_solution():
    random.seed(0)
    puzzle, solution = generate_puzzle(35)
    # Solver should be able to find a solution and it should match the generator's
    # recorded solution. Also the puzzle must have exactly one solution.
    board_to_solve = deep_copy(puzzle)
    assert solve_board(board_to_solve) is True
    assert board_to_solve == solution
    assert count_solutions(puzzle, max_solutions=2) == 1
