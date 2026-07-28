"""Tải sẵn wheel Python trên HOST để đóng gói Docker image không cần mạng.

Lý do tồn tại: mạng egress của container Docker trong môi trường phát triển này
không ổn định — cả apt-get (Debian mirror) lẫn pip (PyPI) đều timeout sau nhiều
phút khi gọi trực tiếp từ bên trong quá trình build image, trong khi cùng lệnh
pip chạy trên host (venv cục bộ) hoàn tất bình thường trong vài giây.

Giải pháp: tải wheel ở đây (trên host, mạng ổn định), COPY thư mục vào build
context, cài bằng `pip install --no-index --find-links=...` — không gọi mạng
trong lúc build image. Xem Dockerfile.api.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

WHEELS_DIR = Path(__file__).resolve().parents[1] / "docker_wheels"

# Khớp với dependencies trong pyproject.toml [project.dependencies].
PACKAGES = [
    "duckdb", "pandas", "pyarrow", "numpy", "requests",
    "fastapi", "uvicorn[standard]", "psycopg[binary]", "sqlalchemy", "pydantic",
    "setuptools", "wheel",
    # Phụ thuộc tùy chọn của uvicorn[standard] chỉ áp dụng trên Linux
    # (sys_platform != "win32"): pip download đánh giá environment marker theo
    # trình thông dịch ĐANG CHẠY (Windows), không theo --platform đích, nên phải
    # liệt kê tường minh để không bị bỏ sót khi tải trên host Windows.
    "uvloop", "httptools", "watchfiles", "websockets", "python-dotenv",
]

# Image cơ sở là python:3.12-slim (Debian, glibc) — phải khớp nền tảng/ABI khi
# tải trên host Windows, nếu không pip trong container sẽ không thấy wheel hợp lệ.
PLATFORM_ARGS = [
    "--platform", "manylinux2014_x86_64",
    "--python-version", "312",
    "--implementation", "cp",
    "--abi", "cp312",
    "--only-binary=:all:",
]


def main() -> int:
    WHEELS_DIR.mkdir(exist_ok=True)
    venv_python = Path(__file__).resolve().parents[1] / ".venv" / "Scripts" / "python.exe"
    python = str(venv_python) if venv_python.exists() else sys.executable

    cmd = [python, "-m", "pip", "download", "--no-cache-dir", "-d", str(WHEELS_DIR),
           *PLATFORM_ARGS, *PACKAGES]
    print("Đang tải wheel cho triển khai Docker offline...")
    result = subprocess.run(cmd)
    if result.returncode == 0:
        n = len(list(WHEELS_DIR.glob("*.whl")))
        print(f"\nHoàn tất: {n} file wheel tại {WHEELS_DIR}")
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
