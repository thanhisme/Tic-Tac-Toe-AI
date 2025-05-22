# 9x9 Tic-Tac-Toe with Heuristic Alpha-Beta Search

Vietnameses version: [Here](./README.vi.md).

## Problem Description

This project implements a 9x9 Tic-Tac-Toe game where the objective is to connect four consecutive marks ('X' or 'O') horizontally, vertically, or diagonally. The game is played between a human player ('O') and an AI opponent ('X'). The AI uses a heuristic-based Alpha-Beta pruning algorithm to efficiently make moves within the large search space.

---

## Introduction to Heuristic Alpha-Beta Search and the Heuristic Function

### 1. What is Heuristic Alpha-Beta Search?

Heuristic Alpha-Beta Search is an advanced search algorithm based on **Minimax**, commonly used in two-player games such as Tic-Tac-Toe, Chess, etc.

- **Minimax** searches for the optimal move by assuming the opponent also plays optimally. The Max player tries to maximize the score, while the Min player tries to minimize it.

- **Alpha-Beta Pruning** is a branch-cutting technique within Minimax that reduces the number of states to explore by eliminating branches that cannot improve the outcome, based on two values: alpha (the best value Max can guarantee) and beta (the best value Min can guarantee).

- **Heuristic** is used when it is impossible to explore the entire game tree due to a large state space (such as a 9x9 board). The algorithm limits the search depth (depth limit), and at this cutoff point, estimates the state’s value using a heuristic function instead of waiting for a terminal win/loss/draw outcome.

### 2. Pseudocode of the Alpha-Beta Search Algorithm

```pseudo
function MAX-VALUE(state, alpha, beta, depth):
    if terminal_test(state) or depth >= depth_limit:
        return heuristic(state)

    value = -∞
    for action in actions(state):
        value = max(value, MIN-VALUE(result(state, action), alpha, beta, depth + 1))
        if value >= beta:
            return value  // cắt nhánh beta
        alpha = max(alpha, value)
    return value

function MIN-VALUE(state, alpha, beta, depth):
    if terminal_test(state) or depth >= depth_limit:
        return heuristic(state)

    value = +∞
    for action in actions(state):
        value = min(value, MAX-VALUE(result(state, action), alpha, beta, depth + 1))
        if value <= alpha:
            return value  // cắt nhánh alpha
        beta = min(beta, value)
    return value
```

### 3. Heuristic Function in the Problem

The heuristic function is used to estimate how "good" the current board state is for the AI player (player_max). It evaluates consecutive sequences of cells on the board based on the following criteria:

- **Sliding windows of 4 consecutive cells** (since winning requires 4 in a row).
- Counts the number of AI pieces, opponent pieces, and empty cells within each window.
- Scores the pattern based on the configuration:
  - 4 in a row: very high score (100,000), indicating a winning position.
  - 3 pieces + 1 empty cell: high score (2,000 for AI, -2,500 for opponent), signaling a dangerous threat.
  - 2 pieces + 2 empty cells: medium score (300 if both ends are open, 100 if one end is open), reflecting potential for development.
  - 1 piece + 3 empty cells: low score (10 or -9), indicating minimal influence.
- If the window contains both AI and opponent pieces (blocked), it is not scored.
- Positive scores indicate advantage for AI, negative scores indicate strength for the opponent.

The heuristic returns the total score accumulated from all horizontal, vertical, and diagonal sequences, helping the AI evaluate the current position to choose the optimal move.

### 4. Depth Selection for Minimax with Alpha-Beta Pruning

- Since the 9x9 board has a very large state space, searching the entire game tree in real-time is infeasible.
- Therefore, the algorithm is limited to a certain search depth (depth_limit), which is set to 3 in this case.
- Depth 3 strikes a balance between reasonably accurate evaluation and acceptable computation time.
- If the depth is too shallow, the AI might miss strategic moves deeper in the game.
- If the depth is too deep, computation time increases significantly, negatively affecting the gameplay experience.

Using the heuristic function combined with depth limitation allows the Alpha-Beta Search algorithm to be both efficient and practical for this game.

## How to Run the Code

1. Make sure you have Python 3 installed.
2. Install dependencies using:

```bash
pip install -r requirements.txt
```

3. Run the game:

```
python main.py
```

4. The human player plays as 'O' and the AI plays as 'X'.
5. Click on the board to make your move. The AI will respond after a brief delay.

## License

Ton Duc Thang University.
