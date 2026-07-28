"""Giao diện chung cho mọi cấu trúc sketch.

Nguyên tắc P2 (Phase 4 §3.2): mọi sketch phải đo được bộ nhớ THẬT, không ước lượng.
Đây là điều kiện để chứng minh O(log^2 N), O(log N)... bằng số liệu thay vì bằng lời.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class Sketch(ABC):
    """Cấu trúc dữ liệu xấp xỉ xử lý luồng một lượt."""

    @abstractmethod
    def memory_bytes(self) -> int:
        """Bộ nhớ THỰC TẾ mà cấu trúc đang chiếm (byte).

        Đo bằng cách cộng dồn sys.getsizeof của các thành phần, không phải công thức.
        """

    @abstractmethod
    def theoretical_bits(self) -> float:
        """Số bit theo cận lý thuyết của giáo trình.

        Dùng để đối chiếu với memory_bytes() trong thực nghiệm E3. Hai con số sẽ
        KHÔNG bằng nhau — Python có overhead lớn cho mỗi đối tượng. Điều cần chứng
        minh là chúng cùng ĐỘ TĂNG TRƯỞNG theo N, không phải cùng giá trị.
        """
