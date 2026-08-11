import importlib

app_module = importlib.import_module("app")
client = app_module.app.test_client()

import sudoku_logic


def test_all_difficulties_accepted():
    for d in ('easy', 'medium', 'hard'):
        resp = client.get(f'/new?difficulty={d}')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'puzzle' in data


def _is_9x9(board):
    return len(board) == 9 and all(len(row) == 9 for row in board)


def test_each_difficulty_generates_valid_9x9_puzzle_and_unique_solution():
    for d in ('easy', 'medium', 'hard'):
        resp = client.get(f'/new?difficulty={d}')
        assert resp.status_code == 200
        puzzle = resp.get_json()['puzzle']
        assert _is_9x9(puzzle)
        # each generated puzzle should have exactly one solution
        assert sudoku_logic.count_solutions(puzzle, max_solutions=2) == 1


def test_prefilled_cells_are_preserved():
    resp = client.get('/new?difficulty=medium')
    puzzle = resp.get_json()['puzzle']
    solution = app_module.CURRENT.get('solution')
    assert solution is not None
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if puzzle[i][j] != 0:
                assert puzzle[i][j] == solution[i][j]
