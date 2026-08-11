from flask import Flask, render_template, jsonify, request

import game_state
import sudoku_logic

app = Flask(__name__)

# Keep a simple in-memory store for current puzzle and solution
CURRENT = game_state.CURRENT

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new')
def new_game():
    # Accept either a difficulty string (easy, medium, hard) or an explicit clues number
    difficulty = request.args.get('difficulty')
    clues_param = request.args.get('clues')
    try:
        if difficulty:
            puzzle, solution = sudoku_logic.generate_puzzle(difficulty)
        elif clues_param is not None:
            clues = int(clues_param)
            puzzle, solution = sudoku_logic.generate_puzzle(clues)
        else:
            puzzle, solution = sudoku_logic.generate_puzzle()
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400
    game_state.reset_current(puzzle, solution)
    return jsonify({'puzzle': puzzle})


@app.route('/hint')
def hint():
    puzzle = CURRENT.get('puzzle')
    solution = CURRENT.get('solution')
    if solution is None or puzzle is None:
        return jsonify({'error': 'No game in progress'}), 400

    hint_result = sudoku_logic.provide_hint(puzzle, solution)
    if hint_result is None:
        return jsonify({'error': 'No empty cells to hint'}), 400
    r, c, val = hint_result
    CURRENT['hints_used'] = CURRENT.get('hints_used', 0) + 1
    return jsonify({'hint': [r, c], 'value': val})


@app.route('/score', methods=['POST'])
def submit_score():
    data = request.get_json(silent=True)
    try:
        elapsed_int = game_state.parse_elapsed(data)
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400

    difficulty = data.get('difficulty')
    if difficulty is not None and difficulty not in sudoku_logic.DIFFICULTY_LEVELS:
        return jsonify({'error': 'Invalid difficulty'}), 400

    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400

    try:
        board = game_state.validate_final_board(data.get('board'))
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400

    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if board[i][j] != solution[i][j]:
                return jsonify({'error': 'Submitted board does not match solution'}), 400

    hints_used = CURRENT.get('hints_used', 0)
    CURRENT['last_score'] = {'elapsed': elapsed_int, 'difficulty': difficulty, 'hints_used': hints_used}
    CURRENT['completed'] = True
    return jsonify({'status': 'ok'})

@app.route('/check', methods=['POST'])
def check_solution():
    data = request.get_json(silent=True)
    if not data or 'board' not in data:
        return jsonify({'error': 'Missing board in request'}), 400

    try:
        board = game_state._validate_board_shape(data['board'])
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400

    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400

    try:
        incorrect = game_state.get_incorrect_cells(board, solution)
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400

    return jsonify({'incorrect': incorrect})

if __name__ == '__main__':
    app.run(debug=True)