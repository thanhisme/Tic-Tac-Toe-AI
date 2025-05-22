import pygame
import sys
import math
from copy import deepcopy

# --- Game constants ---
CELL_SIZE = 60
BOARD_SIZE = 9
WIDTH = HEIGHT = CELL_SIZE * BOARD_SIZE
LINE_COLOR = (200, 200, 200)
BG_COLOR = (30, 30, 30)
X_COLOR = (255, 100, 100)
O_COLOR = (100, 180, 255)
FONT_SIZE = 40
STATUS_BAR_HEIGHT = 40
STATUS_BAR_BG = (255, 20, 20)
STATUS_BAR_POSITION = (0, 0)
DELAY_COMPUTER_MOVE = 300
RESULT_DISPLAY_TIME = 2000
CENTER_TEXT_Y = 30

POPUP_HEIGHT = 60
POPUP_BG_COLOR = (50, 50, 50)
TEXT_COLOR = (255, 255, 255)
CENTER_TEXT_Y_OFFSET = HEIGHT // 2 - 30

# --- Problem class: encapsulates game logic and rules ---
class Problem:
    def __init__(self, initial_state, player_max='X', player_min='O'):
        """
        Initialize the game problem.
        :param initial_state: Dictionary with board, current player, and move count
        :param player_max: The AI player symbol (default 'X')
        :param player_min: The human player symbol (default 'O')
        """
        self.initial_state = initial_state
        self.player_max = player_max
        self.player_min = player_min

    def player(self, state):
        """
        Return the current player to move.
        """
        return state['current_player']

    def actions(self, state):
        """
        Return a list of all possible moves (empty cells) on the board.
        """
        actions = []
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if state['board'][row][col] == '.':
                    actions.append((row, col))
        return actions

    def result(self, state, action):
        """
        Return a new game state after applying the given action.
        :param state: The current state
        :param action: A tuple (row, col) representing the move
        :return: A new state with the move applied and player switched
        """
        new_state = deepcopy(state)
        row, col = action
        new_state['board'][row][col] = state['current_player']
        new_state['move_count'] += 1
        new_state['current_player'] = self.player_min if state['current_player'] == self.player_max else self.player_max
        return new_state

    def terminal_test(self, state):
        """
        Check if the game has ended either by a win or a full board (draw).
        :return: True if the game is over, False otherwise
        """
        return self.get_winner(state) is not None or state['move_count'] >= BOARD_SIZE * BOARD_SIZE

    def get_winner(self, state):
        """
        Determine the winner of the game by checking all possible win lines.
        :return: 'X', 'O', or None if there's no winner
        """
        board = state['board']

        def check_line(line):
            count = 1
            for i in range(1, len(line)):
                if line[i] != '.' and line[i] == line[i - 1]:
                    count += 1
                    if count == 4:
                        return line[i]
                else:
                    count = 1
            return None

        # Check rows and columns
        for i in range(BOARD_SIZE):
            row = board[i]
            col = [board[j][i] for j in range(BOARD_SIZE)]
            if (winner := check_line(row)) or (winner := check_line(col)):
                return winner

        # Check diagonals (both main and anti-diagonals)
        for i in range(BOARD_SIZE - 3):
            for j in range(BOARD_SIZE - 3):
                diag1 = [board[i + k][j + k] for k in range(4)]  # Top-left to bottom-right
                diag2 = [board[i + 3 - k][j + k] for k in range(4)]  # Bottom-left to top-right
                if (winner := check_line(diag1)) or (winner := check_line(diag2)):
                    return winner
        return None

    def utility(self, state, player):
        """
        Return the utility value of the state from the perspective of 'player'.
        +1 if the player wins, -1 if loses, 0 for draw or ongoing game.
        """
        winner = self.get_winner(state)
        if winner == player:
            return 1
        elif winner is None:
            return 0
        else:
            return -1


# --- AlphaBetaAgent class: AI using alpha-beta pruning and heuristic evaluation ---
class AlphaBetaAgent:
    def __init__(self, problem, depth_limit=3):
        """
        Initialize the AlphaBeta agent.
        :param problem: Instance of the Problem class containing game rules
        :param depth_limit: Maximum depth for search (controls difficulty/performance)
        """
        self.problem = problem
        self.depth_limit = depth_limit

    def get_best_move(self, state):
        """
        Return the best move using alpha-beta pruning.
        :param state: Current game state
        :return: Best action (row, col)
        """
        best_score = -math.inf
        best_action = None
        alpha = -math.inf
        beta = math.inf

        for action in self.problem.actions(state):
            new_state = self.problem.result(state, action)
            score = self.h_min_value(new_state, alpha, beta, 1)
            if score > best_score:
                best_score = score
                best_action = action
            alpha = max(alpha, best_score)
        return best_action

    def h_max_value(self, state, alpha, beta, depth):
        """
        Recursive max-value function for maximizing player (AI).
        Applies alpha-beta pruning and stops at terminal/depth limit.
        """
        if self.problem.terminal_test(state) or depth >= self.depth_limit:
            return self.heuristic(state)

        value = -math.inf
        for action in self.problem.actions(state):
            value = max(value, self.h_min_value(self.problem.result(state, action), alpha, beta, depth + 1))
            if value >= beta:
                return value  # Beta cut-off
            alpha = max(alpha, value)
        return value

    def h_min_value(self, state, alpha, beta, depth):
        """
        Recursive min-value function for minimizing player (opponent).
        Applies alpha-beta pruning and stops at terminal/depth limit.
        """
        if self.problem.terminal_test(state) or depth >= self.depth_limit:
            return self.heuristic(state)

        value = math.inf
        for action in self.problem.actions(state):
            value = min(value, self.h_max_value(self.problem.result(state, action), alpha, beta, depth + 1))
            if value <= alpha:
                return value  # Alpha cut-off
            beta = min(beta, value)
        return value

    def heuristic(self, state):
        """
        Evaluate the current state using a custom heuristic function.
        It looks at every 4-cell sequence (horizontal, vertical, diagonal)
        and assigns scores based on potential for winning or blocking.
        """
        board = state['board']
        player = self.problem.player_max  # AI (X)
        opponent = self.problem.player_min  # Human (O)

        def evaluate_line(line):
            """
            Evaluate a line of 4 cells and return a score based on threat/potential.
            """
            def score_pattern(count, empty, open_ends, is_player):
                if count == 4:
                    return 100000 if is_player else -100000
                elif count == 3 and empty == 1:
                    return 2000 if is_player else -2500
                elif count == 2 and empty == 2:
                    score = 300 if open_ends else 100
                    return score if is_player else -600 if open_ends else -90
                elif count == 1 and empty == 3:
                    return 10 if is_player else -9
                return 0

            score = 0
            for i in range(len(line) - 3):
                window = line[i:i + 4]
                player_count = window.count(player)
                opponent_count = window.count(opponent)
                empty_count = window.count('.')

                # Ignore if both players have marks in this window (blocked line)
                if player_count > 0 and opponent_count > 0:
                    continue

                open_ends = window[0] == '.' and window[3] == '.'

                if player_count > 0:
                    score += score_pattern(player_count, empty_count, open_ends, is_player=True)
                elif opponent_count > 0:
                    score += score_pattern(opponent_count, empty_count, open_ends, is_player=False)
            return score

        total_score = 0

        # Evaluate all rows
        for row in board:
            total_score += evaluate_line(row)

        # Evaluate all columns
        for col in range(BOARD_SIZE):
            column = [board[row][col] for row in range(BOARD_SIZE)]
            total_score += evaluate_line(column)

        # Evaluate all top-left to bottom-right diagonals
        for row in range(BOARD_SIZE - 3):
            for col in range(BOARD_SIZE - 3):
                diag = [board[row + k][col + k] for k in range(4)]
                total_score += evaluate_line(diag)

        # Evaluate all bottom-left to top-right diagonals
        for row in range(3, BOARD_SIZE):
            for col in range(BOARD_SIZE - 3):
                diag = [board[row - k][col + k] for k in range(4)]
                total_score += evaluate_line(diag)

        return total_score


# --- Game class: handle visualization and main game loop using Pygame ---
class Game:
    def __init__(self):
        """
        Initialize the game environment:
        - Setup pygame window and font
        - Create initial game state (empty board, human player starts)
        - Initialize problem and AI agent
        """
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT + STATUS_BAR_HEIGHT))
        pygame.display.set_caption("9x9 Tic-Tac-Toe - Heuristic Alpha-Beta Search with Pruning")
        self.font = pygame.font.SysFont(None, FONT_SIZE)
        self.status_text = ""

        # Initial game state: empty 9x9 board, human is 'O', 0 moves played
        initial_state = {
            'board': [['.' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)],
            'current_player': 'O',  # Human always plays 'O'
            'move_count': 0
        }
        self.problem = Problem(initial_state)  # Game logic handler
        self.agent = AlphaBetaAgent(self.problem, depth_limit=3)  # AI player
        self.state = initial_state  # Current game state

    def draw_status(self):
        """
        Render the status bar text (e.g., "Your turn", "Opponent thinking") on screen.
        """
        status_bar = pygame.Surface((WIDTH, STATUS_BAR_HEIGHT))
        status_bar.fill(STATUS_BAR_BG)  # Background color of status bar
        status = self.font.render(self.status_text, True, TEXT_COLOR)
        status_rect = status.get_rect(center=(WIDTH // 2, STATUS_BAR_HEIGHT // 2))
        status_bar.blit(status, status_rect)
        self.screen.blit(status_bar, STATUS_BAR_POSITION)

    def draw_board(self):
        """
        Render the entire game board:
        - Clear screen and draw status bar
        - Draw grid cells and any placed X or O symbols
        - Refresh display
        """
        self.screen.fill(BG_COLOR)  # Clear screen
        self.draw_status()

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                # Draw cell rectangle
                rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE + STATUS_BAR_HEIGHT, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, LINE_COLOR, rect, 1)

                # Draw player's symbol if present ('X' or 'O')
                symbol = self.state['board'][row][col]
                if symbol != '.':
                    color = X_COLOR if symbol == 'X' else O_COLOR
                    text = self.font.render(symbol, True, color)
                    text_rect = text.get_rect(center=rect.center)
                    self.screen.blit(text, text_rect)

        pygame.display.flip()  # Update the full display

    def run(self):
        """
        Main game loop:
        - Alternates turns between human ('O') and AI ('X')
        - Handles user input for human moves
        - Uses AlphaBetaAgent for AI moves with a delay
        - Updates board and checks for game over condition
        """
        running = True
        while running and not self.problem.terminal_test(self.state):
            # Update status message depending on current player
            if self.problem.player(self.state) == self.problem.player_min:
                self.status_text = "Your turn (O)..."
            else:
                self.status_text = "Your opponent is thinking (X)..."
            self.draw_board()

            if self.problem.player(self.state) == self.problem.player_min:
                # Handle human player's turn: wait for mouse click on empty cell
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        break
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        x, y = pygame.mouse.get_pos()
                        # Translate pixel to board coordinates (account for status bar height)
                        row, col = (y - STATUS_BAR_HEIGHT) // CELL_SIZE, x // CELL_SIZE
                        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
                            # If the clicked cell is empty, update state with player's move
                            if (row, col) in self.problem.actions(self.state):
                                self.state = self.problem.result(self.state, (row, col))
                                break
            else:
                # AI player's turn: add a small delay for realism, then compute and make move
                pygame.time.delay(DELAY_COMPUTER_MOVE)
                move = self.agent.get_best_move(self.state)
                if move:
                    self.state = self.problem.result(self.state, move)

        # Once game ends, draw final board and show the result message
        self.draw_board()
        winner = self.problem.get_winner(self.state)
        self.show_result(winner)

    def show_result(self, winner):
        """
        Display the game result as a popup message and exit after a delay.
        :param winner: 'X', 'O', or None for draw
        """
        text = "Draw!" if winner is None else ("You win!" if winner == 'O' else "Your opponent wins!")
        print(text)  # Also print result in console

        # Create a semi-transparent popup bar at the bottom to display the result
        popup = pygame.Surface((WIDTH, POPUP_HEIGHT))
        popup.fill(POPUP_BG_COLOR)
        msg = self.font.render(text, True, TEXT_COLOR)
        msg_rect = msg.get_rect(center=(WIDTH // 2, CENTER_TEXT_Y))
        popup.blit(msg, msg_rect)
        self.screen.blit(popup, (0, CENTER_TEXT_Y_OFFSET))
        pygame.display.flip()

        # Wait a few seconds so the player can see the result, then exit
        pygame.time.delay(RESULT_DISPLAY_TIME)
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
