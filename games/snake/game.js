const board = document.getElementById("game-board");
const context = board.getContext("2d");
const scoreElement = document.getElementById("score");
const bestScoreElement = document.getElementById("best-score");
const statusElement = document.getElementById("status");
const restartButton = document.getElementById("restart-button");
const autoButton = document.getElementById("auto-button");

const GRID_SIZE = 24;
const CELL_SIZE = board.width / GRID_SIZE;
const BASE_SPEED = 5;
const MAX_SPEED = 15;
const STORAGE_KEY = "maxwellyin.snake.bestScore";

const colors = {
  gridBg: "#ffffff",
  gridColor: "rgba(15, 23, 42, 0.05)",
  snakeHead: "#324e98",
  snakeBody: "#3f5fb8",
  food: "#ef4444",
};

function updateColorsFromTheme() {
  const styles = getComputedStyle(document.documentElement);
  colors.gridBg = styles.getPropertyValue("--grid-bg").trim() || colors.gridBg;
  colors.gridColor = styles.getPropertyValue("--grid-color").trim() || colors.gridColor;
  colors.snakeHead = styles.getPropertyValue("--snake-head").trim() || colors.snakeHead;
  colors.snakeBody = styles.getPropertyValue("--snake").trim() || colors.snakeBody;
  colors.food = styles.getPropertyValue("--food").trim() || colors.food;
}

updateColorsFromTheme();

const DIRECTIONS = {
  ArrowUp: { x: 0, y: -1 },
  ArrowDown: { x: 0, y: 1 },
  ArrowLeft: { x: -1, y: 0 },
  ArrowRight: { x: 1, y: 0 },
};

const DIRECTION_LIST = Object.values(DIRECTIONS);

let state = createInitialState();
let pendingDirection = { ...state.direction };
let animationFrameId = null;
let lastTickTime = 0;
let touchStart = null;
let autoMode = false;

function createInitialState() {
  return {
    snake: [
      { x: 11, y: 12 },
      { x: 10, y: 12 },
      { x: 9, y: 12 },
    ],
    direction: { x: 1, y: 0 },
    food: { x: 17, y: 12 },
    score: 0,
    bestScore: readBestScore(),
    speed: BASE_SPEED,
    running: false,
    gameOver: false,
  };
}

function readBestScore() {
  return Number.parseInt(localStorage.getItem(STORAGE_KEY) || "0", 10);
}

function saveBestScore(score) {
  localStorage.setItem(STORAGE_KEY, String(score));
}

function startGame() {
  if (state.gameOver) return;
  if (state.running) return;

  state.running = true;
  updateStatus();
  lastTickTime = 0;
  animationFrameId = window.requestAnimationFrame(gameLoop);
}

function restartGame() {
  window.cancelAnimationFrame(animationFrameId);
  updateColorsFromTheme();
  state = createInitialState();
  pendingDirection = { ...state.direction };
  animationFrameId = null;
  lastTickTime = 0;
  render();
  if (autoMode) {
    startGame();
  }
}

function gameLoop(timestamp) {
  if (!state.running) return;

  if (!lastTickTime) {
    lastTickTime = timestamp;
  }

  const elapsedSeconds = (timestamp - lastTickTime) / 1000;
  const tickSeconds = 1 / state.speed;

  if (elapsedSeconds >= tickSeconds) {
    update();
    render();
    lastTickTime = timestamp;
    if (!state.running) return;
  }

  animationFrameId = window.requestAnimationFrame(gameLoop);
}

function update() {
  if (autoMode) {
    pendingDirection = chooseAutoDirection();
  }

  state.direction = pendingDirection;
  const head = state.snake[0];
  const nextHead = nextCellFor(head, state.direction);
  const willGrow = sameCell(nextHead, state.food);

  if (hitsWall(nextHead) || hitsSnake(nextHead, { includeTail: willGrow })) {
    endGame();
    return;
  }

  state.snake.unshift(nextHead);

  if (sameCell(nextHead, state.food)) {
    state.score += 1;
    state.speed = speedForScore(state.score);
    if (state.score > state.bestScore) {
      state.bestScore = state.score;
      saveBestScore(state.bestScore);
    }
    state.food = placeFood();
    return;
  }

  state.snake.pop();
}

function endGame() {
  state.running = false;
  state.gameOver = true;
  window.cancelAnimationFrame(animationFrameId);
  animationFrameId = null;
  statusElement.textContent = "Game over. Press Restart to try again.";
}

function placeFood() {
  const occupied = new Set(state.snake.map((part) => keyFor(part)));
  const openCells = [];

  for (let y = 0; y < GRID_SIZE; y += 1) {
    for (let x = 0; x < GRID_SIZE; x += 1) {
      const candidate = { x, y };
      if (!occupied.has(keyFor(candidate))) {
        openCells.push(candidate);
      }
    }
  }

  return openCells[Math.floor(Math.random() * openCells.length)];
}

function render() {
  drawBoard();
  drawFood();
  drawSnake();
  scoreElement.textContent = String(state.score);
  bestScoreElement.textContent = String(state.bestScore);
  updateStatus();
}

function speedForScore(score) {
  return Math.min(BASE_SPEED + Math.log(score + 1) * 2, MAX_SPEED);
}

function drawBoard() {
  context.fillStyle = colors.gridBg;
  context.fillRect(0, 0, board.width, board.height);

  context.strokeStyle = colors.gridColor;
  context.lineWidth = 1;
  for (let i = 1; i < GRID_SIZE; i += 1) {
    const pos = i * CELL_SIZE;
    context.beginPath();
    context.moveTo(pos, 0);
    context.lineTo(pos, board.height);
    context.stroke();
    context.beginPath();
    context.moveTo(0, pos);
    context.lineTo(board.width, pos);
    context.stroke();
  }
}

function drawSnake() {
  state.snake.forEach((part, index) => {
    context.fillStyle = index === 0 ? colors.snakeHead : colors.snakeBody;
    drawRoundedCell(part.x, part.y, 6);
  });
}

function drawFood() {
  context.fillStyle = colors.food;
  const centerX = state.food.x * CELL_SIZE + CELL_SIZE / 2;
  const centerY = state.food.y * CELL_SIZE + CELL_SIZE / 2;
  context.beginPath();
  context.arc(centerX, centerY, CELL_SIZE * 0.34, 0, Math.PI * 2);
  context.fill();
}

function drawRoundedCell(x, y, radius) {
  const inset = 2;
  const left = x * CELL_SIZE + inset;
  const top = y * CELL_SIZE + inset;
  const size = CELL_SIZE - inset * 2;

  context.beginPath();
  context.roundRect(left, top, size, size, radius);
  context.fill();
}

function setDirection(nextDirection) {
  if (autoMode) {
    setAutoMode(false);
  }

  const current = state.direction;
  const isReverse = current.x + nextDirection.x === 0 && current.y + nextDirection.y === 0;
  if (!isReverse) {
    pendingDirection = nextDirection;
  }
  startGame();
}

function setAutoMode(enabled) {
  autoMode = enabled;
  autoButton.setAttribute("aria-pressed", String(autoMode));
  autoButton.textContent = autoMode ? "Auto On" : "Auto";
  updateStatus();
}

function toggleAutoMode() {
  setAutoMode(!autoMode);
  if (autoMode) {
    startGame();
  }
}

function updateStatus() {
  if (state.gameOver) {
    statusElement.textContent = "Game over. Press Restart to try again.";
    return;
  }

  if (autoMode) {
    statusElement.textContent = "Auto mode is playing.";
    return;
  }

  statusElement.textContent = state.running ? "Running" : "Press an arrow key to start.";
}

function chooseAutoDirection() {
  const pathDirection = findDirectionToFood();
  if (pathDirection && isSafeMove(pathDirection)) {
    return pathDirection;
  }

  return chooseSafeFallbackDirection();
}

function findDirectionToFood() {
  const head = state.snake[0];
  const body = new Set(state.snake.slice(0, -1).map((part) => keyFor(part)));
  const queue = [{ cell: head, firstDirection: null }];
  const visited = new Set([keyFor(head)]);

  while (queue.length > 0) {
    const current = queue.shift();

    for (const direction of DIRECTION_LIST) {
      if (!current.firstDirection && isReverseDirection(direction)) continue;

      const nextCell = {
        x: current.cell.x + direction.x,
        y: current.cell.y + direction.y,
      };
      const nextKey = keyFor(nextCell);

      if (visited.has(nextKey) || hitsWall(nextCell) || body.has(nextKey)) {
        continue;
      }

      const firstDirection = current.firstDirection || direction;
      if (sameCell(nextCell, state.food)) {
        return firstDirection;
      }

      visited.add(nextKey);
      queue.push({ cell: nextCell, firstDirection });
    }
  }

  return null;
}

function chooseSafeFallbackDirection() {
  const head = state.snake[0];
  const body = new Set(state.snake.slice(0, -1).map((part) => keyFor(part)));
  let bestDirection = null;
  let bestScore = -Infinity;

  for (const direction of DIRECTION_LIST) {
    if (isReverseDirection(direction)) continue;

    if (!isSafeMove(direction)) {
      continue;
    }

    const nextCell = nextCellFor(head, direction);
    const openSpace = countReachableCells(nextCell, body);
    const foodDistance = Math.abs(nextCell.x - state.food.x) + Math.abs(nextCell.y - state.food.y);
    const score = openSpace * 2 - foodDistance;

    if (score > bestScore) {
      bestScore = score;
      bestDirection = direction;
    }
  }

  return bestDirection || state.direction;
}

function countReachableCells(start, blocked) {
  const queue = [start];
  const visited = new Set([keyFor(start)]);

  while (queue.length > 0) {
    const current = queue.shift();

    for (const direction of DIRECTION_LIST) {
      const nextCell = {
        x: current.x + direction.x,
        y: current.y + direction.y,
      };
      const nextKey = keyFor(nextCell);

      if (visited.has(nextKey) || hitsWall(nextCell) || blocked.has(nextKey)) {
        continue;
      }

      visited.add(nextKey);
      queue.push(nextCell);
    }
  }

  return visited.size;
}

function isReverseDirection(direction) {
  return state.direction.x + direction.x === 0 && state.direction.y + direction.y === 0;
}

function hitsWall(cell) {
  return cell.x < 0 || cell.x >= GRID_SIZE || cell.y < 0 || cell.y >= GRID_SIZE;
}

function hitsSnake(cell, options = {}) {
  const includeTail = options.includeTail ?? true;
  const body = includeTail ? state.snake : state.snake.slice(0, -1);
  return body.some((part) => sameCell(part, cell));
}

function isSafeMove(direction) {
  const nextCell = nextCellFor(state.snake[0], direction);
  const willGrow = sameCell(nextCell, state.food);
  return !hitsWall(nextCell) && !hitsSnake(nextCell, { includeTail: willGrow });
}

function nextCellFor(cell, direction) {
  return {
    x: cell.x + direction.x,
    y: cell.y + direction.y,
  };
}

function sameCell(a, b) {
  return a.x === b.x && a.y === b.y;
}

function keyFor(cell) {
  return `${cell.x},${cell.y}`;
}

function handleKeydown(event) {
  const nextDirection = DIRECTIONS[event.key];
  if (!nextDirection) return;

  event.preventDefault();
  setDirection(nextDirection);
}

function handleTouchStart(event) {
  const touch = event.changedTouches[0];
  touchStart = { x: touch.clientX, y: touch.clientY };
}

function handleTouchEnd(event) {
  if (!touchStart) return;

  const touch = event.changedTouches[0];
  const dx = touch.clientX - touchStart.x;
  const dy = touch.clientY - touchStart.y;
  touchStart = null;

  if (Math.max(Math.abs(dx), Math.abs(dy)) < 24) return;

  if (Math.abs(dx) > Math.abs(dy)) {
    setDirection(dx > 0 ? DIRECTIONS.ArrowRight : DIRECTIONS.ArrowLeft);
    return;
  }

  setDirection(dy > 0 ? DIRECTIONS.ArrowDown : DIRECTIONS.ArrowUp);
}

document.addEventListener("keydown", handleKeydown);
board.addEventListener("touchstart", handleTouchStart, { passive: true });
board.addEventListener("touchend", handleTouchEnd, { passive: true });
restartButton.addEventListener("click", restartGame);
autoButton.addEventListener("click", toggleAutoMode);

render();

// Gamepad support
let lastGamepadState = {};
function pollGamepad() {
  const gamepads = navigator.getGamepads ? navigator.getGamepads() : [];
  const gp = gamepads[0];
  if (gp) {
    const buttons = {
      left: gp.buttons[14]?.pressed || gp.axes[0] < -0.5 || gp.buttons[2]?.pressed, // X
      right: gp.buttons[15]?.pressed || gp.axes[0] > 0.5 || gp.buttons[1]?.pressed, // B
      up: gp.buttons[12]?.pressed || gp.axes[1] < -0.5 || gp.buttons[3]?.pressed,   // Y
      down: gp.buttons[13]?.pressed || gp.axes[1] > 0.5 || gp.buttons[0]?.pressed   // A
    };

    if (buttons.up && !lastGamepadState.up) setDirection(DIRECTIONS.ArrowUp);
    if (buttons.down && !lastGamepadState.down) setDirection(DIRECTIONS.ArrowDown);
    if (buttons.left && !lastGamepadState.left) setDirection(DIRECTIONS.ArrowLeft);
    if (buttons.right && !lastGamepadState.right) setDirection(DIRECTIONS.ArrowRight);

    lastGamepadState = buttons;
  }
  requestAnimationFrame(pollGamepad);
}
requestAnimationFrame(pollGamepad);
