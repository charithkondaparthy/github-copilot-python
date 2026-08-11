import importlib

app_module = importlib.import_module("app")
client = app_module.app.test_client()

import sudoku_logic


def test_score_accepts_and_stores_valid_payload():
    # Ensure there's a current game so hints_used is meaningful
    puzzle, solution = sudoku_logic.generate_puzzle(35)
    app_module.CURRENT['puzzle'] = puzzle
    app_module.CURRENT['solution'] = solution
    app_module.CURRENT['hints_used'] = 2

    resp = client.post('/score', json={'elapsed': 123, 'difficulty': 'medium', 'board': solution})
    assert resp.status_code == 200
    assert app_module.CURRENT.get('last_score') is not None
    last = app_module.CURRENT['last_score']
    assert last['elapsed'] == 123
    assert last['difficulty'] == 'medium'
    assert last['hints_used'] == 2


def test_score_rejects_invalid_elapsed():
    # include a valid board to pass board validation
    puzzle, solution = sudoku_logic.generate_puzzle(35)
    app_module.CURRENT['puzzle'] = puzzle
    app_module.CURRENT['solution'] = solution
    resp = client.post('/score', json={'elapsed': -5, 'board': solution})
    assert resp.status_code == 400
    resp = client.post('/score', json={'elapsed': 'not-an-int', 'board': solution})
    assert resp.status_code == 400