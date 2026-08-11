from typing import List, Dict, Any


def top_n_scores(entries: List[Dict[str, Any]], n: int = 10) -> List[Dict[str, Any]]:
    """Validate, sort (ascending by elapsed), and return top-n scoreboard entries.

    Each entry must be a dict with keys: 'name' (str), 'elapsed' (int >=0),
    'difficulty' (optional str or None), and 'hints' (int >=0).
    """
    valid = []
    for e in entries:
        if not isinstance(e, dict):
            continue
        name = e.get('name')
        elapsed = e.get('elapsed')
        difficulty = e.get('difficulty', None)
        hints = e.get('hints', 0)
        if not isinstance(name, str):
            continue
        if not isinstance(elapsed, int) or elapsed < 0:
            continue
        if difficulty is not None and not isinstance(difficulty, str):
            continue
        if not isinstance(hints, int) or hints < 0:
            continue
        valid.append({'name': name, 'elapsed': elapsed, 'difficulty': difficulty, 'hints': hints})
    valid.sort(key=lambda x: x['elapsed'])
    return valid[:n]
