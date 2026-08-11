import importlib
import json

app_module = importlib.import_module("app")
client = app_module.app.test_client()

import sudoku_logic


def test_check_no_game_in_progress():
    # Clear any current game
    app_module.CURRENT['solution'] = None
    resp = client.post('/check', json={'board': sudoku_logic.create_empty_board()})
    assert resp.status_code == 400
    assert resp.get_json().get('error') == 'No game in progress'


def test_check_invalid_requests():
    # Missing board
    resp = client.post('/check', data=json.dumps({}), content_type='application/json')
    assert resp.status_code == 400
    assert 'Missing board' in resp.get_json().get('error')

    # Malformed board shape
    resp = client.post('/check', json={'board': [[1, 2], [3, 4]]})
    assert resp.status_code == 400
    assert 'Invalid board shape' in resp.get_json().get('error')

    # Invalid cell value
    bad = sudoku_logic.create_empty_board()
    bad[0][0] = 99
    # set a solution so route doesn't short-circuit
    app_module.CURRENT['solution'] = sudoku_logic.create_empty_board()
    resp = client.post('/check', json={'board': bad})
    assert resp.status_code == 400
    assert 'Invalid board values' in resp.get_json().get('error')


def test_check_detects_incorrect_and_empty_cells():
    # Create a known puzzle
    puzzle, solution = sudoku_logic.generate_puzzle(35)
    app_module.CURRENT['puzzle'] = puzzle
    app_module.CURRENT['solution'] = solution

    # Make a player board that copies the puzzle, then introduce errors
    player = [row.copy() for row in puzzle]
    # Introduce an incorrect filled cell (choose a cell that was empty in puzzle)
    # Find first empty cell and set wrong value
    found = False
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if puzzle[i][j] == 0:
                player[i][j] = (solution[i][j] % sudoku_logic.SIZE) + 1
                wrong_pos = [i, j]
                found = True
                break
        if found:
            break

    # Also leave another empty cell as 0
    empty_pos = None
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if puzzle[i][j] == 0 and [i, j] != wrong_pos:
                empty_pos = [i, j]
                break
        if empty_pos:
            break

    resp = client.post('/check', json={'board': player})
    assert resp.status_code == 200
    data = resp.get_json()
    incorrect = data.get('incorrect')
    assert wrong_pos in incorrect
    # empty_pos should be considered incorrect because it's empty while solution has a value
    if empty_pos:
        assert empty_pos in incorrect