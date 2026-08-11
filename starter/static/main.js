// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
let puzzle = [];
let elapsedSeconds = 0;
let timerInterval = null;
let hintsUsed = 0;

/* Theme handling */
const THEME_KEY = 'theme';
function applyTheme(theme) {
  const isDark = theme === 'dark';
  if (isDark) document.documentElement.classList.add('dark');
  else document.documentElement.classList.remove('dark');
  const toggle = document.getElementById('theme-toggle');
  if (toggle) toggle.checked = isDark;
  try {
    localStorage.setItem(THEME_KEY, theme);
  } catch (e) {
    // ignore storage errors
  }
}

function loadTheme() {
  try {
    const stored = localStorage.getItem(THEME_KEY);
    if (stored) { applyTheme(stored); return; }
  } catch (e) {}
  // fallback to system preference
  const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  applyTheme(prefersDark ? 'dark' : 'light');
}

function formatTime(seconds) {
  const mm = Math.floor(seconds / 60).toString().padStart(2, '0');
  const ss = (seconds % 60).toString().padStart(2, '0');
  return `${mm}:${ss}`;
}

/* Leaderboard (client-side localStorage) */
const LEADERBOARD_KEY = 'sudoku_leaderboard';
const LEADERBOARD_MAX = 10;

function isValidEntry(obj) {
  if (!obj || typeof obj !== 'object') return false;
  if (typeof obj.name !== 'string') return false;
  if (!Number.isInteger(obj.elapsed) || obj.elapsed < 0) return false;
  if (obj.difficulty !== null && obj.difficulty !== undefined && typeof obj.difficulty !== 'string') return false;
  if (!Number.isInteger(obj.hints) || obj.hints < 0) return false;
  return true;
}

function loadLeaderboard() {
  try {
    const raw = localStorage.getItem(LEADERBOARD_KEY);
    if (!raw) { displayEmptyLeaderboard(); return []; }
    const arr = JSON.parse(raw);
    if (!Array.isArray(arr)) throw new Error('bad');
    const valid = arr.filter(isValidEntry);
    const sorted = valid.sort((a,b) => a.elapsed - b.elapsed).slice(0, LEADERBOARD_MAX);
    localStorage.setItem(LEADERBOARD_KEY, JSON.stringify(sorted));
    displayLeaderboardFromArray(sorted);
    return sorted;
  } catch (e) {
    localStorage.removeItem(LEADERBOARD_KEY);
    displayEmptyLeaderboard();
    return [];
  }
}

function saveLeaderboard(arr) {
  try { localStorage.setItem(LEADERBOARD_KEY, JSON.stringify(arr.slice(0, LEADERBOARD_MAX))); } catch (e) {}
}

function addScoreLocal(entry) {
  if (!isValidEntry(entry)) return;
  const arr = loadLeaderboard();
  arr.push(entry);
  const sorted = arr.sort((a,b) => a.elapsed - b.elapsed).slice(0, LEADERBOARD_MAX);
  saveLeaderboard(sorted);
}

function escapeHtml(s) {
  return String(s).replace(/[&<>'"]/g, (m) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":"&#39;"})[m]);
}

function displayEmptyLeaderboard() {
  const c = document.getElementById('leaderboard');
  if (!c) return;
  c.innerHTML = '<div>No scores yet. Solve a puzzle to add your name!</div>';
}

function displayLeaderboardFromArray(arr) {
  const c = document.getElementById('leaderboard');
  if (!c) return;
  if (!arr || arr.length === 0) { displayEmptyLeaderboard(); return; }
  const table = document.createElement('table');
  table.style.width = '100%';
  table.style.borderCollapse = 'collapse';
  const header = document.createElement('tr');
  header.innerHTML = '<th style="text-align:left">Rank</th><th style="text-align:left">Name</th><th style="text-align:right">Time</th><th style="text-align:left">Difficulty</th><th style="text-align:right">Hints</th>';
  table.appendChild(header);
  arr.forEach((e, i) => {
    const tr = document.createElement('tr');
    const mmss = formatTime(e.elapsed);
    tr.innerHTML = `<td>${i+1}</td><td>${escapeHtml(e.name)}</td><td style="text-align:right">${mmss}</td><td>${e.difficulty || '-'}</td><td style="text-align:right">${e.hints}</td>`;
    table.appendChild(tr);
  });
  c.innerHTML = '';
  c.appendChild(table);
}

function displayLeaderboard() { loadLeaderboard(); }


function resetTimer() {
  elapsedSeconds = 0;
  const timerEl = document.getElementById('timer');
  if (timerEl) timerEl.innerText = formatTime(elapsedSeconds);
  if (timerInterval) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
}

function startTimer() {
  if (timerInterval) return; // already running
  timerInterval = setInterval(() => {
    elapsedSeconds += 1;
    const timerEl = document.getElementById('timer');
    if (timerEl) timerEl.innerText = formatTime(elapsedSeconds);
  }, 1000);
}

function stopTimer() {
  if (timerInterval) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
}

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.className = 'sudoku-cell';
      input.dataset.row = i;
      input.dataset.col = j;
      input.addEventListener('input', (e) => {
        const val = e.target.value.replace(/[^1-9]/g, '');
        e.target.value = val;
        markConflicts();
      });
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function renderPuzzle(puz) {
  puzzle = puz;
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        inp.className += ' prefilled';
      } else {
        inp.value = '';
        inp.disabled = false;
      }
    }
  }
}

function showMessage(text, color = '#d32f2f') {
  const msg = document.getElementById('message');
  if (msg) {
    msg.style.color = color;
    msg.innerText = text;
  }
}

function buildBoardFromInputs() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = inputs[idx].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }
  return board;
}

function markConflicts() {
  const boardDiv = document.getElementById('sudoku-board');
  if (!boardDiv) return;
  const inputs = boardDiv.getElementsByTagName('input');
  const board = buildBoardFromInputs();

  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    if (inp.disabled) continue;
    inp.classList.remove('invalid');
  }

  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const value = board[i][j];
      if (!value) continue;
      const idx = i * SIZE + j;
      let conflict = false;
      for (let col = 0; col < SIZE; col++) {
        if (col !== j && board[i][col] === value) conflict = true;
      }
      for (let row = 0; row < SIZE; row++) {
        if (row !== i && board[row][j] === value) conflict = true;
      }
      const startRow = Math.floor(i / 3) * 3;
      const startCol = Math.floor(j / 3) * 3;
      for (let dr = 0; dr < 3; dr++) {
        for (let dc = 0; dc < 3; dc++) {
          const r = startRow + dr;
          const c = startCol + dc;
          if ((r !== i || c !== j) && board[r][c] === value) conflict = true;
        }
      }
      if (conflict) {
        inputs[idx].classList.add('invalid');
      }
    }
  }
}

async function newGame() {
  const difficulty = document.getElementById('difficulty')?.value;
  const url = difficulty ? `/new?difficulty=${encodeURIComponent(difficulty)}` : '/new';
  const res = await fetch(url);
  const data = await res.json();
  if (!res.ok || data.error) {
    showMessage(data.error || 'Unable to start a new game. Please try again.');
    return;
  }
  renderPuzzle(data.puzzle);
  document.getElementById('message').innerText = '';
  hintsUsed = 0;
  resetTimer();
  startTimer();
}

async function checkSolution() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = inputs[idx].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }
  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.style.color = '#d32f2f';
    msg.innerText = data.error;
    return;
  }
  const incorrect = new Set(data.incorrect.map(x => x[0]*SIZE + x[1]));
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    if (inp.disabled) continue;
    inp.className = 'sudoku-cell';
    if (incorrect.has(idx)) {
      inp.className = 'sudoku-cell incorrect';
    }
  }
  if (incorrect.size === 0) {
    // Stop timer, disable inputs, and submit final board and elapsed to server
    stopTimer();
    msg.style.color = '#388e3c';
    msg.innerText = 'Congratulations! You solved it!';
    // disable all inputs to prevent further edits
    for (let idx = 0; idx < inputs.length; idx++) {
      inputs[idx].disabled = true;
      inputs[idx].className = 'sudoku-cell prefilled';
    }
    // Build final board to send to server
    const finalBoard = [];
    for (let i = 0; i < SIZE; i++) {
      finalBoard[i] = [];
      for (let j = 0; j < SIZE; j++) {
        const idx = i * SIZE + j;
        const val = inputs[idx].value;
        finalBoard[i][j] = val ? parseInt(val, 10) : 0;
      }
    }
    (async () => {
      try {
        const difficulty = document.getElementById('difficulty')?.value;
        await fetch('/score', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({elapsed: elapsedSeconds, difficulty, board: finalBoard})
        });
      } catch (e) {
        // ignore network errors for score submission
      }
    })();
    // Prompt for name and save locally to leaderboard
    try {
      let name = window.prompt('Enter name for leaderboard (leave blank for Anonymous):', '');
      if (name === null) {
        // user cancelled; do not save locally
      } else {
        name = String(name).trim().slice(0, 40) || 'Anonymous';
        const entry = { name, elapsed: elapsedSeconds, difficulty: difficulty || null, hints: hintsUsed || 0 };
        addScoreLocal(entry);
        displayLeaderboard();
      }
    } catch (e) {
      // ignore prompt errors
    }
  } else {
    msg.style.color = '#d32f2f';
    msg.innerText = 'Some cells are incorrect.';
  }
}

// Wire buttons
window.addEventListener('load', () => {
  // initialize theme first so layout paints correctly
  loadTheme();
  const themeToggle = document.getElementById('theme-toggle');
  if (themeToggle) {
    themeToggle.addEventListener('change', (e) => {
      applyTheme(e.target.checked ? 'dark' : 'light');
    });
  }
  document.getElementById('new-game').addEventListener('click', newGame);
  const hintBtn = document.getElementById('hint');
  if (hintBtn) {
    hintBtn.addEventListener('click', async () => {
      const res = await fetch('/hint');
      const data = await res.json();
      const msg = document.getElementById('message');
      if (data.error) {
        msg.style.color = '#d32f2f';
        msg.innerText = data.error;
        return;
      }
      const [r, c] = data.hint;
      const val = data.value;
      // Update specific cell in UI and disable it
      const boardDiv = document.getElementById('sudoku-board');
      const inputs = boardDiv.getElementsByTagName('input');
      const idx = r * SIZE + c;
      const inp = inputs[idx];
      inp.value = val;
      inp.disabled = true;
      inp.className = 'sudoku-cell prefilled hinted';
      hintsUsed += 1;
      msg.style.color = '#1976d2';
      msg.innerText = `Hint applied at row ${r+1}, col ${c+1}`;
    });
  }
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  // initialize
  newGame();
  displayLeaderboard();
});