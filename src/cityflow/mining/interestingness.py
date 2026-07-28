"""Mười độ đo mức độ thú vị của luật kết hợp.

Cài đặt theo slide chương Frequent Patterns tr.36-39. Giảng viên dành 4 slide
(10% chương) để phê phán support/confidence và giới thiệu tính BẤT BIẾN VỚI GIAO
DỊCH RỖNG (null-invariance) — nhưng 0/16 nhóm còn lại nêu độ đo nào trong tên đề tài.

-------------------------------------------------------------------------------
GIAO DỊCH RỖNG (null transaction) LÀ GÌ
-------------------------------------------------------------------------------
Là giao dịch KHÔNG chứa cả A lẫn B. Trong bảng chéo 2x2, đó là ô ~A & ~B.

Một độ đo BẤT BIẾN VỚI GIAO DỊCH RỖNG nếu giá trị của nó không đổi khi thêm hoặc
bớt các giao dịch rỗng. Vì sao quan trọng: trong CSDL thưa, phần lớn giao dịch là
rỗng đối với một cặp (A, B) bất kỳ. Nếu độ đo phụ thuộc vào số giao dịch rỗng thì
nó phụ thuộc vào việc ta chọn phân tích bao nhiêu dữ liệu — một tính chất vô lý.

Slide tr.39: "Tính bất biến với giao dịch rỗng là then chốt cho phân tích tương
quan. Lift và chi-bình phương KHÔNG bất biến. Năm độ đo bất biến: AllConf,
Coherence, Cosine, Kulczynski, MaxConf."

Ví dụ phản chứng của slide tr.36-37 (bóng rổ / ngũ cốc) được tái hiện trong
tests/test_interestingness.py.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RuleStats:
    """Thống kê thô của một luật A -> B, tính từ CSDL giao dịch."""

    n: int
    """Tổng số giao dịch."""
    sup_a: int
    """Số giao dịch chứa A."""
    sup_b: int
    """Số giao dịch chứa B."""
    sup_ab: int
    """Số giao dịch chứa cả A và B."""

    @property
    def n_null(self) -> int:
        """Số giao dịch RỖNG — không chứa cả A lẫn B."""
        return self.n - self.sup_a - self.sup_b + self.sup_ab

    def p_a(self) -> float:
        return self.sup_a / self.n

    def p_b(self) -> float:
        return self.sup_b / self.n

    def p_ab(self) -> float:
        return self.sup_ab / self.n


# ---------------------------------------------------------------------------
# Độ đo KHÔNG bất biến với giao dịch rỗng
# ---------------------------------------------------------------------------


def support(s: RuleStats) -> float:
    """P(A ∪ B) — slide tr.12."""
    return s.p_ab()


def confidence(s: RuleStats) -> float:
    """P(B | A) — slide tr.12."""
    return s.sup_ab / s.sup_a if s.sup_a else 0.0


def lift(s: RuleStats) -> float:
    """P(A ∩ B) / (P(A) · P(B)) — slide tr.36.

    KHÔNG bất biến với giao dịch rỗng: thêm giao dịch rỗng làm n tăng, kéo lift lên.
    """
    denom = s.p_a() * s.p_b()
    return s.p_ab() / denom if denom > 0 else 0.0


def chi_square(s: RuleStats) -> float:
    """Thống kê chi-bình phương trên bảng chéo 2x2 — slide tr.39.

    KHÔNG bất biến với giao dịch rỗng.
    """
    n = s.n
    observed = [
        s.sup_ab,                       # A & B
        s.sup_a - s.sup_ab,             # A & ~B
        s.sup_b - s.sup_ab,             # ~A & B
        s.n_null,                       # ~A & ~B
    ]
    expected = [
        s.sup_a * s.sup_b / n,
        s.sup_a * (n - s.sup_b) / n,
        (n - s.sup_a) * s.sup_b / n,
        (n - s.sup_a) * (n - s.sup_b) / n,
    ]
    total = 0.0
    for o, e in zip(observed, expected):
        if e > 0:
            total += (o - e) ** 2 / e
    return total


# ---------------------------------------------------------------------------
# Độ đo BẤT BIẾN với giao dịch rỗng (slide tr.39)
# ---------------------------------------------------------------------------
#
# Điểm chung: cả năm chỉ dùng sup_a, sup_b, sup_ab — KHÔNG dùng n. Đó chính là
# lý do hình thức khiến chúng bất biến: giao dịch rỗng chỉ làm n thay đổi.


def all_confidence(s: RuleStats) -> float:
    """sup(A,B) / max{sup(A), sup(B)} — slide tr.39."""
    m = max(s.sup_a, s.sup_b)
    return s.sup_ab / m if m else 0.0


def coherence(s: RuleStats) -> float:
    """sup(A,B) / (sup(A) + sup(B) - sup(A,B)) — slide tr.39. Chính là Jaccard."""
    denom = s.sup_a + s.sup_b - s.sup_ab
    return s.sup_ab / denom if denom else 0.0


def cosine(s: RuleStats) -> float:
    """sup(A,B) / sqrt(sup(A) · sup(B)) — slide tr.39."""
    denom = math.sqrt(s.sup_a * s.sup_b)
    return s.sup_ab / denom if denom else 0.0


def kulczynski(s: RuleStats) -> float:
    """(P(A|B) + P(B|A)) / 2 — slide tr.39."""
    left = s.sup_ab / s.sup_b if s.sup_b else 0.0
    right = s.sup_ab / s.sup_a if s.sup_a else 0.0
    return (left + right) / 2


def max_confidence(s: RuleStats) -> float:
    """max{sup(A,B)/sup(A), sup(A,B)/sup(B)} — slide tr.39."""
    left = s.sup_ab / s.sup_a if s.sup_a else 0.0
    right = s.sup_ab / s.sup_b if s.sup_b else 0.0
    return max(left, right)


def imbalance_ratio(s: RuleStats) -> float:
    """|sup(A) - sup(B)| / (sup(A) + sup(B) - sup(A,B)).

    Không có trong slide nhưng là bạn đồng hành tiêu chuẩn của Kulczynski
    (Wu, Chen & Han 2010): Kulczynski một mình không phân biệt được "A và B cân
    bằng" với "A kéo B nhưng B không kéo A". Tỷ số mất cân bằng bổ sung đúng chiều
    thông tin còn thiếu đó.
    """
    denom = s.sup_a + s.sup_b - s.sup_ab
    return abs(s.sup_a - s.sup_b) / denom if denom else 0.0


# ---------------------------------------------------------------------------

NULL_INVARIANT = ("all_confidence", "coherence", "cosine", "kulczynski",
                  "max_confidence", "imbalance_ratio")
"""Các độ đo bất biến với giao dịch rỗng — slide tr.39 nêu 5 cái đầu."""

NOT_NULL_INVARIANT = ("support", "confidence", "lift", "chi_square")

ALL_MEASURES = {
    "support": support,
    "confidence": confidence,
    "lift": lift,
    "chi_square": chi_square,
    "all_confidence": all_confidence,
    "coherence": coherence,
    "cosine": cosine,
    "kulczynski": kulczynski,
    "max_confidence": max_confidence,
    "imbalance_ratio": imbalance_ratio,
}


def compute_all(s: RuleStats) -> dict[str, float]:
    """Tính cả 10 độ đo cho một luật."""
    return {name: fn(s) for name, fn in ALL_MEASURES.items()}


def add_null_transactions(s: RuleStats, k: int) -> RuleStats:
    """Thêm k giao dịch RỖNG (không chứa A lẫn B).

    Công cụ cho thực nghiệm E10: chỉ n thay đổi, sup_a/sup_b/sup_ab giữ nguyên.
    Độ đo bất biến phải cho GIÁ TRỊ Y HỆT; độ đo không bất biến sẽ trôi.
    """
    return RuleStats(n=s.n + k, sup_a=s.sup_a, sup_b=s.sup_b, sup_ab=s.sup_ab)
