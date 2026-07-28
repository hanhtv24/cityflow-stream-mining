"""Cây FP (FP-tree) — cấu trúc nén cơ sở dữ liệu giao dịch.

Cài đặt from scratch theo slide chương Frequent Patterns tr.21-23
(Han, Pei & Yin, SIGMOD'00).

Xây cây theo hai lượt quét (slide tr.22):
    1. Quét lần 1: đếm tần suất từng item, giữ item thỏa min_support
    2. Sắp các item thường xuyên theo THỨ TỰ GIẢM DẦN tần suất (f-list)
    3. Quét lần 2: với mỗi giao dịch, lọc bỏ item hiếm, sắp theo f-list,
       rồi chèn vào cây

Vì sao sắp giảm dần tần suất: item phổ biến nằm gần gốc nên nhiều giao dịch dùng
chung tiền tố, cho tỷ lệ nén cao. Đây là điều làm FP-tree nhỏ hơn CSDL gốc.
"""

from __future__ import annotations


class FPNode:
    """Một nút của cây FP."""

    __slots__ = ("item", "count", "parent", "children", "node_link")

    def __init__(self, item, count: int = 1, parent: "FPNode | None" = None) -> None:
        self.item = item
        self.count = count
        self.parent = parent
        self.children: dict = {}
        self.node_link: "FPNode | None" = None
        """Liên kết tới nút kế tiếp cùng item — tạo thành danh sách liên kết mà
        bảng header dùng để duyệt mọi lần xuất hiện của một item (slide tr.28)."""

    def __repr__(self) -> str:
        return f"FPNode({self.item}:{self.count})"


class FPTree:
    """Cây FP kèm bảng header.

    Thuộc tính:
        root        : nút gốc (không mang item)
        header      : item -> [tổng tần suất, nút đầu tiên trong danh sách liên kết]
        f_list      : các item thường xuyên, sắp giảm dần tần suất
        min_support : ngưỡng tính theo SỐ ĐẾM tuyệt đối
    """

    __slots__ = ("root", "header", "f_list", "min_support", "n_transactions", "_n_nodes")

    def __init__(self, transactions, min_support: int) -> None:
        self.min_support = min_support
        self.root = FPNode(None, 0)
        self.header: dict = {}
        self._n_nodes = 0

        transactions = list(transactions)
        self.n_transactions = len(transactions)

        # --- Lượt 1: đếm tần suất item ---
        counts: dict = {}
        for txn in transactions:
            for item in txn:
                counts[item] = counts.get(item, 0) + 1

        frequent = {it: c for it, c in counts.items() if c >= min_support}

        # f-list: giảm dần theo tần suất; hòa thì theo item để kết quả tất định
        # (không có thứ tự tất định thì hai lần chạy có thể cho cây khác nhau).
        self.f_list = sorted(frequent, key=lambda it: (-frequent[it], it))
        rank = {it: i for i, it in enumerate(self.f_list)}

        for it in self.f_list:
            self.header[it] = [frequent[it], None]

        # --- Lượt 2: chèn từng giao dịch ---
        for txn in transactions:
            filtered = [it for it in txn if it in rank]
            if not filtered:
                continue
            filtered.sort(key=lambda it: rank[it])
            self._insert(filtered, self.root, 1)

    def _insert(self, items: list, node: FPNode, count: int) -> None:
        """Chèn một giao dịch đã sắp, dùng chung tiền tố nếu có."""
        for item in items:
            child = node.children.get(item)
            if child is not None:
                child.count += count
            else:
                child = FPNode(item, count, node)
                node.children[item] = child
                self._n_nodes += 1
                # Nối vào cuối danh sách liên kết của item trong bảng header.
                entry = self.header[item]
                if entry[1] is None:
                    entry[1] = child
                else:
                    cur = entry[1]
                    while cur.node_link is not None:
                        cur = cur.node_link
                    cur.node_link = child
            node = child

    # -- Nội quan ----------------------------------------------------------

    def is_empty(self) -> bool:
        return not self.root.children

    def n_nodes(self) -> int:
        return self._n_nodes

    def single_path(self) -> list[FPNode] | None:
        """Trả về đường đi nếu cây chỉ có MỘT nhánh, ngược lại None.

        Slide tr.31-32: khi cây chỉ còn một đường, mọi tổ hợp con của đường đó đều
        là mẫu thường xuyên — sinh trực tiếp bằng tổ hợp, không cần đệ quy tiếp.
        Đây là tối ưu hóa "single prefix path" và là điều kiện dừng của thuật toán.
        """
        path = []
        node = self.root
        while len(node.children) == 1:
            node = next(iter(node.children.values()))
            path.append(node)
        return path if not node.children else None

    def prefix_paths(self, item) -> list[tuple[list, int]]:
        """Cơ sở mẫu điều kiện (conditional pattern base) của `item` — slide tr.25-28.

        Duyệt danh sách liên kết của item; với mỗi lần xuất hiện, đi ngược lên gốc
        để lấy tiền tố, kèm theo số đếm của chính nút đó.
        """
        paths = []
        node = self.header.get(item, [0, None])[1]
        while node is not None:
            prefix = []
            parent = node.parent
            while parent is not None and parent.item is not None:
                prefix.append(parent.item)
                parent = parent.parent
            if prefix:
                prefix.reverse()
                paths.append((prefix, node.count))
            node = node.node_link
        return paths

    def __repr__(self) -> str:
        return (f"FPTree(items={len(self.f_list)}, nodes={self._n_nodes}, "
                f"txns={self.n_transactions}, min_sup={self.min_support})")
