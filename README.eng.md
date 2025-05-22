# Cờ Caro 9x9 với Thuật Toán Alpha-Beta Tìm Kiếm Có Heuristic

## Mô tả bài toán

Dự án này triển khai trò chơi Cờ Caro trên bảng 9x9, mục tiêu là nối 4 dấu ('X' hoặc 'O') liên tiếp theo hàng ngang, cột dọc hoặc đường chéo. Trò chơi diễn ra giữa người chơi ('O') và đối thủ AI ('X'). AI sử dụng thuật toán Alpha-Beta tìm kiếm kết hợp hàm heuristic để lựa chọn nước đi hiệu quả trong không gian trạng thái rất lớn.

---

## Giới thiệu về Thuật Toán Heuristic Alpha-Beta Search và Hàm Heuristic

### 1. Heuristic Alpha-Beta Search là gì?

Heuristic Alpha-Beta Search là thuật toán tìm kiếm nâng cao dựa trên **Minimax**, được sử dụng phổ biến trong các trò chơi hai người như Cờ Caro, Cờ Vua, v.v.

- **Minimax** tìm kiếm nước đi tối ưu bằng cách giả định đối thủ cũng chơi tối ưu. Người chơi Max cố gắng tối đa hóa điểm số, người chơi Min cố gắng tối thiểu hóa điểm số.

- **Alpha-Beta Pruning** là kỹ thuật cắt tỉa nhánh trong Minimax giúp giảm số trạng thái cần duyệt bằng cách loại bỏ những nhánh không thể cải thiện kết quả, dựa trên hai giá trị `alpha` (giá trị tốt nhất Max có thể đạt) và `beta` (giá trị tốt nhất Min có thể đạt).

- **Heuristic** được sử dụng khi không thể duyệt hết toàn bộ cây trò chơi do không gian trạng thái quá lớn (như bảng 9x9). Thuật toán giới hạn độ sâu tìm kiếm (`depth limit`), tại điểm cắt này, ước lượng giá trị trạng thái bằng hàm heuristic thay vì chờ kết quả thắng/thua/hòa.

### 2. Mã giả thuật toán Alpha-Beta Search

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

### 3. Hàm Heuristic trong bài toán

Hàm heuristic được sử dụng để ước lượng mức độ “tốt” của trạng thái bàn cờ hiện tại dành cho người chơi AI (`player_max`). Hàm này đánh giá các chuỗi ô liên tiếp trên bàn cờ dựa trên các tiêu chí sau:

- **Cửa sổ trượt gồm 4 ô liên tiếp** (vì để thắng cần nối 4 dấu cùng loại).
- Đếm số lượng quân của AI, quân đối thủ và ô trống trong mỗi cửa sổ.
- Tính điểm dựa trên mẫu nước đi:
  - 4 quân liên tiếp: điểm rất cao (100,000), biểu thị vị trí chiến thắng.
  - 3 quân + 1 ô trống: điểm cao (2,000 cho AI, -2,500 cho đối thủ), cảnh báo mối nguy hiểm.
  - 2 quân + 2 ô trống: điểm trung bình (300 nếu hai đầu mở, 100 nếu một đầu mở), phản ánh tiềm năng phát triển.
  - 1 quân + 3 ô trống: điểm thấp (10 hoặc -9), ảnh hưởng ít.
- Nếu cửa sổ chứa cả quân AI và đối thủ (bị chặn), cửa sổ đó không được tính điểm.
- Điểm dương thể hiện lợi thế cho AI, điểm âm thể hiện thế mạnh của đối thủ.

Hàm heuristic trả về tổng điểm của tất cả các chuỗi ngang, dọc và chéo, giúp AI đánh giá vị trí hiện tại để chọn nước đi tối ưu.

### 4. Lựa chọn độ sâu cho thuật toán Minimax với Alpha-Beta Pruning

- Bàn cờ 9x9 có không gian trạng thái rất lớn, nên không thể duyệt toàn bộ cây trò chơi trong thời gian thực.
- Thuật toán được giới hạn ở một độ sâu tìm kiếm nhất định (`depth_limit`), trong trường hợp này là 3.
- Độ sâu 3 là sự cân bằng giữa việc đánh giá tương đối chính xác và thời gian tính toán hợp lý.
- Nếu độ sâu quá nông, AI có thể bỏ lỡ những nước đi chiến lược sâu hơn.
- Nếu độ sâu quá sâu, thời gian tính toán kéo dài, ảnh hưởng đến trải nghiệm chơi.

Việc sử dụng hàm heuristic kết hợp với giới hạn độ sâu giúp thuật toán Alpha-Beta Search vừa hiệu quả vừa thực tiễn cho trò chơi này.

## Cách chạy code

1. Đảm bảo bạn đã cài đặt Python 3.
2. Cài đặt các thư viện cần thiết bằng lệnh:

```bash
pip install -r requirements.txt
```

3. Chạy chương trình:

```
python main.py
```

4. Người chơi sẽ đóng vai 'O' và AI sẽ đóng vai 'X'.
5. Nhấn vào bàn cờ để thực hiện nước đi của bạn. AI sẽ phản hồi sau một khoảng thời gian ngắn.

## License

Đại học Tôn Đức Thắng.
