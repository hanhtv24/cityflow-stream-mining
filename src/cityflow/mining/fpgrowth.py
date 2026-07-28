"""FP-Growth — khai phá tập mục thường xuyên bằng phát triển mẫu.

Cài đặt from scratch theo slide chương Frequent Patterns tr.20-33.

Triết lý (slide tr.20): "Phát triển mẫu dài từ mẫu ngắn, chỉ dùng các item thường
xuyên cục bộ." Không sinh ứng viên, không kiểm tra ứng viên.

Phương pháp (slide tr.32):
    Với mỗi item thường xuyên (duyệt NGƯỢC f-list):
        1. Xây cơ sở mẫu điều kiện
        2. Xây cây FP điều kiện từ cơ sở đó
        3. Lặp lại đệ quy trên cây điều kiện mới
    Dừng khi cây rỗng hoặc chỉ còn một đường đi.

Ưu điểm so với Apriori (slide tr.33):
    - Chia để trị, thu hẹp dần CSDL
    - Không sinh/kiểm tra ứng viên
    - Nén CSDL bằng cấu trúc cây
    - Không quét lại toàn bộ CSDL nhiều lần
"""

from __future__ import annotations

from itertools import combinations

from .fptree import FPTree


def fpgrowth(transactions, min_support: int) -> dict[frozenset, int]:
    """Khai phá mọi tập mục thường xuyên.

    Trả về: {frozenset(các item): số đếm hỗ trợ}
    min_support tính theo SỐ ĐẾM tuyệt đối, không phải tỷ lệ.
    """
    tree = FPTree(transactions, min_support)
    result: dict[frozenset, int] = {}
    _mine(tree, frozenset(), min_support, result)
    return result


def _mine(tree: FPTree, suffix: frozenset, min_support: int,
          result: dict[frozenset, int]) -> None:
    if tree.is_empty():
        return

    path = tree.single_path()
    if path is not None:
        # Slide tr.31-32: cây một đường -> mọi tổ hợp con của đường đều thường xuyên.
        # Số đếm của một tổ hợp = số đếm của nút SÂU NHẤT trong tổ hợp đó, vì các
        # nút trên cùng một đường có số đếm không tăng khi đi xuống.
        for size in range(1, len(path) + 1):
            for combo in combinations(path, size):
                itemset = suffix | {n.item for n in combo}
                count = min(n.count for n in combo)
                if count >= min_support:
                    result[itemset] = max(result.get(itemset, 0), count)
        return

    # Duyệt NGƯỢC f-list: xử lý item ÍT thường xuyên trước, để cây điều kiện của
    # chúng nhỏ nhất có thể (slide tr.24-27 xử lý I5, I4, I3... theo đúng thứ tự này).
    for item in reversed(tree.f_list):
        support = tree.header[item][0]
        if support < min_support:
            continue

        new_suffix = suffix | {item}
        result[new_suffix] = max(result.get(new_suffix, 0), support)

        # Cơ sở mẫu điều kiện -> cây FP điều kiện
        cond_txns = []
        for prefix, count in tree.prefix_paths(item):
            cond_txns.extend([prefix] * count)

        if cond_txns:
            cond_tree = FPTree(cond_txns, min_support)
            _mine(cond_tree, new_suffix, min_support, result)


# ---------------------------------------------------------------------------
# Mẫu đóng và mẫu cực đại (slide tr.13-14)
# ---------------------------------------------------------------------------


def closed_itemsets(frequent: dict[frozenset, int]) -> dict[frozenset, int]:
    """Tập mục ĐÓNG: X đóng nếu không có tập cha Y ⊃ X có CÙNG số đếm hỗ trợ.

    Slide tr.13: mẫu đóng cho phép "nén không mất mát" tập mẫu thường xuyên —
    từ tập đóng khôi phục lại được toàn bộ tập thường xuyên kèm số đếm.
    """
    by_size: dict[int, list] = {}
    for iset, cnt in frequent.items():
        by_size.setdefault(len(iset), []).append((iset, cnt))

    closed = {}
    max_size = max(by_size) if by_size else 0
    for iset, cnt in frequent.items():
        is_closed = True
        for size in range(len(iset) + 1, max_size + 1):
            for other, ocnt in by_size.get(size, ()):
                if ocnt == cnt and iset < other:
                    is_closed = False
                    break
            if not is_closed:
                break
        if is_closed:
            closed[iset] = cnt
    return closed


def maximal_itemsets(frequent: dict[frozenset, int]) -> dict[frozenset, int]:
    """Tập mục CỰC ĐẠI: X cực đại nếu không có tập cha Y ⊃ X nào thường xuyên.

    Slide tr.13: nén mạnh hơn mẫu đóng nhưng CÓ MẤT MÁT — không khôi phục được
    số đếm hỗ trợ của các tập con.
    """
    by_size: dict[int, list] = {}
    for iset in frequent:
        by_size.setdefault(len(iset), []).append(iset)

    maximal = {}
    max_size = max(by_size) if by_size else 0
    for iset, cnt in frequent.items():
        is_max = True
        for size in range(len(iset) + 1, max_size + 1):
            if any(iset < other for other in by_size.get(size, ())):
                is_max = False
                break
        if is_max:
            maximal[iset] = cnt
    return maximal


def reconstruct_from_closed(closed: dict[frozenset, int]) -> dict[frozenset, int]:
    """Khôi phục toàn bộ tập thường xuyên từ tập ĐÓNG.

    Dùng để KIỂM CHỨNG khẳng định "nén không mất mát" của slide tr.13 bằng thực
    nghiệm, thay vì tin lời. Số đếm của một tập con X = max số đếm trong các tập
    đóng chứa X.
    """
    recovered: dict[frozenset, int] = {}
    for c_set, c_cnt in closed.items():
        for size in range(1, len(c_set) + 1):
            for combo in combinations(sorted(c_set), size):
                key = frozenset(combo)
                if recovered.get(key, 0) < c_cnt:
                    recovered[key] = c_cnt
    return recovered
