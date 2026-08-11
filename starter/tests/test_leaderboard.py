from leaderboard import top_n_scores


def test_sorting_and_top_n():
    entries = [
        {'name': 'A', 'elapsed': 120, 'difficulty': 'easy', 'hints': 1},
        {'name': 'B', 'elapsed': 60, 'difficulty': 'medium', 'hints': 0},
        {'name': 'C', 'elapsed': 180, 'difficulty': 'hard', 'hints': 2},
    ]
    top = top_n_scores(entries, n=2)
    assert len(top) == 2
    assert top[0]['name'] == 'B'
    assert top[1]['name'] == 'A'


def test_validation_filters_bad_entries():
    entries = [
        {'name': 'A', 'elapsed': -1, 'difficulty': 'easy', 'hints': 1},
        {'name': 'B', 'elapsed': 'notint'},
        {'name': 'C', 'elapsed': 100, 'difficulty': None, 'hints': 0},
    ]
    top = top_n_scores(entries)
    assert len(top) == 1
    assert top[0]['name'] == 'C'
