class Problem:
    def __init__(self, win_length=4):
        self.win_length = win_length
        self.player_max = 'X'
        self.player_min = 'O'
        self.initial_state = [[None]*9 for _ in range(9)]

    def get_opponent(self, player):
        return self.player_min if player == self.player_max else self.player_max

    def get_successors(self, state, player):
        successors = []
        for r in range(9):
            for c in range(9):
                if state[r][c] is None:
                    new_state = [row[:] for row in state]
                    new_state[r][c] = player
                    successors.append(((r, c), new_state))
        return successors

    def apply_move(self, state, move, player):
        r, c = move
        new_state = [row[:] for row in state]
        new_state[r][c] = player
        return new_state

    def is_terminal(self, state):
        # Kiểm tra thắng/thua hoặc bàn cờ đầy
        def check_line(line):
            count = 0
            last = None
            for cell in line:
                if cell == last and cell is not None:
                    count += 1
                    if count >= self.win_length:
                        return True
                else:
                    count = 1
                    last = cell
            return False

        # Kiểm tra hàng, cột, đường chéo
        for r in range(9):
            if check_line(state[r]):
                return True
        for c in range(9):
            if check_line([state[r][c] for r in range(9)]):
                return True
        # Đường chéo chính và phụ
        for r in range(9 - self.win_length + 1):
            for c in range(9 - self.win_length + 1):
                diag1 = [state[r+i][c+i] for i in range(self.win_length)]
                diag2 = [state[r+i][c+self.win_length-1 - i] for i in range(self.win_length)]
                if check_line(diag1) or check_line(diag2):
                    return True

        # Kiểm tra bàn cờ đầy
        for r in range(9):
            for c in range(9):
                if state[r][c] is None:
                    return False
        return True  # Hòa nếu đầy mà không có người thắng

    def heuristic(self, state, player):
        opponent = self.get_opponent(player)
        board_size = 9

        directions = [
            (0, 1),   # ngang
            (1, 0),   # dọc
            (1, 1),   # chéo chính
            (1, -1),  # chéo phụ
        ]

        def in_board(r, c):
            return 0 <= r < board_size and 0 <= c < board_size

        def get_line_info(r, c, dr, dc, length, player_check):
            """
            Kiểm tra chuỗi liên tiếp bắt đầu tại (r,c) theo hướng (dr,dc),
            trả về:
            - count liên tiếp của player_check
            - trạng thái 2 đầu (True nếu trống, False nếu bị chặn)
            - vị trí của chuỗi trên board (dùng để đánh giá vị trí giữa hay mép)
            """
            count = 0
            for i in range(length):
                nr, nc = r + dr*i, c + dc*i
                if not in_board(nr, nc):
                    return 0, (False, False), []
                if state[nr][nc] == player_check:
                    count += 1
                else:
                    break

            if count == 0:
                return 0, (False, False), []

            # Kiểm tra 2 đầu
            before_r, before_c = r - dr, c - dc
            after_r, after_c = r + dr*count, c + dc*count

            before_open = in_board(before_r, before_c) and state[before_r][before_c] is None
            after_open = in_board(after_r, after_c) and state[after_r][after_c] is None

            positions = [(r + dr*i, c + dc*i) for i in range(count)]

            return count, (before_open, after_open), positions

        score = 0

        def eval_sequence(count, ends_open, positions, is_player):
            # Trọng số cho từng trường hợp (có thể tùy chỉnh)
            weights = {
                4: 100000,
                3: 1000,
                2: 100,
            }
            if count < 2:
                return 0

            # Trọng số ưu tiên 2 đầu mở cao hơn 1 đầu mở
            open_bonus = 1.5 if ends_open[0] and ends_open[1] else 1.0
            semi_open = (ends_open[0] != ends_open[1]) and not (ends_open[0] and ends_open[1])

            base_score = weights.get(count, 0)
            if semi_open:
                base_score /= 2  # bán mở ít giá trị hơn

            # Ưu tiên vị trí giữa bàn cờ (cách center càng gần càng cao)
            center = board_size // 2
            dist_sum = sum(abs(r - center) + abs(c - center) for r, c in positions)
            pos_bonus = max(0, (board_size - dist_sum / count))  # lớn hơn nếu gần trung tâm

            val = base_score * open_bonus + pos_bonus * 10

            # Nếu là đối thủ thì trừ điểm, ưu tiên chặn
            return val if is_player else -val * 1.2

        # Duyệt toàn bộ bàn cờ
        for r in range(board_size):
            for c in range(board_size):
                for dr, dc in directions:
                    for length in [2, 3, 4]:
                        count, ends_open, positions = get_line_info(r, c, dr, dc, length, player)
                        if count == length:
                            score += eval_sequence(count, ends_open, positions, True)
                        count_op, ends_open_op, positions_op = get_line_info(r, c, dr, dc, length, opponent)
                        if count_op == length:
                            score += eval_sequence(count_op, ends_open_op, positions_op, False)

        return score


class AlphaBetaAgent:
    def __init__(self, problem, max_player, depth_limit=3):
        self.problem = problem
        self.max_player = max_player
        self.min_player = problem.get_opponent(max_player)
        self.depth_limit = depth_limit

    def get_best_move(self, state):
        best_score = float('-inf')
        best_move = None
        alpha = float('-inf')
        beta = float('inf')

        for move, child_state in self.problem.get_successors(state, self.max_player):
            score = self._h_minimax(child_state, 1, alpha, beta, False)
            if score > best_score:
                best_score = score
                best_move = move
            alpha = max(alpha, best_score)

        return best_move

    def _h_minimax(self, state, depth, alpha, beta, maximizing):
        if self.problem.is_terminal(state) or depth >= self.depth_limit:
            return self.problem.heuristic(state, self.max_player)

        player = self.max_player if maximizing else self.min_player
        successors = self.problem.get_successors(state, player)

        if maximizing:
            value = float('-inf')
            for move, child in successors:
                value = max(value, self._h_minimax(child, depth + 1, alpha, beta, False))
                alpha = max(alpha, value)
                if beta <= alpha:
                    break
            return value
        else:
            value = float('inf')
            for move, child in successors:
                value = min(value, self._h_minimax(child, depth + 1, alpha, beta, True))
                beta = min(beta, value)
                if beta <= alpha:
                    break
            return value


class Game:
    def __init__(self, problem, agent):
        self.problem = problem
        self.agent = agent
        self.state = [row[:] for row in problem.initial_state]
        self.current_player = problem.player_max

    def switch_player(self):
        self.current_player = self.problem.get_opponent(self.current_player)

    def visualize(self):
        print("  " + " ".join(str(i) for i in range(9)))
        for i, row in enumerate(self.state):
            row_str = " ".join(cell if cell is not None else '.' for cell in row)
            print(f"{i} {row_str}")

    def human_move(self):
        while True:
            try:
                inp = input("Nhập nước đi (hàng,cột): ")
                r, c = map(int, inp.strip().split(','))
                if 0 <= r < 9 and 0 <= c < 9 and self.state[r][c] is None:
                    self.state[r][c] = self.current_player
                    break
                else:
                    print("Nước đi không hợp lệ hoặc ô đã có người đánh, thử lại.")
            except Exception:
                print("Sai định dạng, nhập lại theo dạng: hàng,cột (ví dụ 3,4)")

    def run(self):
        while True:
            self.visualize()
            if self.problem.is_terminal(self.state):
                print(f"Trò chơi kết thúc! Người chơi {self.current_player} thắng hoặc hòa.")
                break

            if self.current_player == self.agent.max_player:
                print("Máy đang suy nghĩ...")
                move = self.agent.get_best_move(self.state)
                print(f"Máy đánh: {move}")
                self.state = self.problem.apply_move(self.state, move, self.current_player)
            else:
                self.human_move()

            self.switch_player()


# --- Ví dụ chạy trò chơi ---
if __name__ == "__main__":
    problem = Problem()
    agent = AlphaBetaAgent(problem, max_player='X', depth_limit=3)
    game = Game(problem, agent)
    game.run()
