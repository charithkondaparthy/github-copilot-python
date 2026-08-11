import importlib

app_module = importlib.import_module("app")
client = app_module.app.test_client()

import sudoku_logic


def test_hint_applies_single_hint_and_tracks_count():
    puzzle, solution = sudoku_logic.generate_puzzle(35)
    app_module.CURRENT['puzzle'] = puzzle
    app_module.CURRENT['solution'] = solution
    app_module.CURRENT['hints_used'] = 0

    resp = client.get('/hint')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'hint' in data and 'value' in data
    r, c = data['hint']
    val = data['value']
    # current puzzle should have the hinted value
    assert app_module.CURRENT['puzzle'][r][c] == val
    assert val == solution[r][c]
    assert app_module.CURRENT['hints_used'] == 1


def test_hint_when_no_empty_cells():
    # Full solution: no empty cells
    board = sudoku_logic.create_empty_board()
    sudoku_logic._fill_board_random(board)
    app_module.CURRENT['puzzle'] = board
    app_module.CURRENT['solution'] = board
    app_module.CURRENT['hints_used'] = 0

    resp = client.get('/hint')
    assert resp.status_code == 400
    assert 'No empty cells' in resp.get_json().get('error')