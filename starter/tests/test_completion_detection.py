import importlib

app_module = importlib.import_module("app")
client = app_module.app.test_client()

import sudoku_logic


def test_completed_board_records_score_and_sets_completed_flag():
    puzzle, solution = sudoku_logic.generate_puzzle(35)
    # Set server-side current game
    app_module.CURRENT['puzzle'] = puzzle
    app_module.CURRENT['solution'] = solution
    app_module.CURRENT['hints_used'] = 1

    # First, check endpoint should return no incorrect for correct full board
    resp = client.post('/check', json={'board': solution})
    assert resp.status_code == 200
    assert resp.get_json().get('incorrect') == []

    # Submit score with the final board
    resp = client.post('/score', json={'elapsed': 99, 'difficulty': 'medium', 'board': solution})
    assert resp.status_code == 200
    assert app_module.CURRENT.get('last_score') is not None
    assert app_module.CURRENT.get('completed') is True


def test_incorrect_full_board_is_rejected_for_score():
    puzzle, solution = sudoku_logic.generate_puzzle(35)
    app_module.CURRENT['puzzle'] = puzzle
    app_module.CURRENT['solution'] = solution

    # Create an incorrect full board by changing one cell
    bad = [row.copy() for row in solution]
    bad[0][0] = (bad[0][0] % sudoku_logic.SIZE) + 1

    resp = client.post('/check', json={'board': bad})
    assert resp.status_code == 200
    assert len(resp.get_json().get('incorrect')) > 0

    # Attempting to submit score with incorrect board should be rejected
    resp = client.post('/score', json={'elapsed': 50, 'difficulty': 'medium', 'board': bad})
    assert resp.status_code == 400
    assert app_module.CURRENT.get('last_score') is None or app_module.CURRENT.get('last_score').get('elapsed') != 50
