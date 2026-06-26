"""一键生成三个演示二维码（H5 / PC 控制台 / 知识确认页）。

自动探测本机局域网 IP（UDP 路由探测，不真发包、不联网），把 PNG 写到仓库根。
换 WiFi / 路由器重启导致 IP 变化时，跑一次即可刷新全部码，无需手动查 ipconfig。

用法（仓库根目录）：.venv/Scripts/python scripts/gen_demo_qrcodes.py
依赖：qrcode[pil]（演示机已装；未装则 .venv/Scripts/python -m pip install 'qrcode[pil]'）
"""
import socket
import sys
from pathlib import Path

try:
    import qrcode
except ImportError:
    sys.exit("缺少依赖：.venv/Scripts/python -m pip install 'qrcode[pil]'")

# Windows 控制台默认 GBK，中文 print 易乱码；切 UTF-8 让 git bash 正确显示。
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
except Exception:
    pass

PORT = 8000
# (文件名后缀, 路径, 中文标签)
TARGETS = [
    ("h5", "/ui/h5.html", "客户视角 H5（扫码即聊）"),
    ("ui", "/ui", "PC 控制台"),
    ("confirm", "/ui/confirm.html", "知识确认页"),
]
OUT_DIR = Path(__file__).resolve().parent.parent  # 仓库根


def detect_lan_ip() -> str:
    """UDP 连一个公网地址（不真发包）→ 内核按默认路由选出口网卡 → 即本机局域网 IP。

    实测拿到的是物理 WiFi/以太网网卡（如 192.168.x.x），而非 WSL 虚拟网卡（172.28.x.x）。
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()


def main() -> None:
    ip = detect_lan_ip()
    wsl = ip.startswith("172.28.")
    print(f"探测到本机 IP：{ip}")
    if wsl:
        print("  ⚠️ 这是 WSL 虚拟网卡（172.28.x.x），手机访问不了！请检查网络/用 ipconfig 取 192.168.x.x。")
    print(f"生成到：{OUT_DIR}")
    for name, path, label in TARGETS:
        url = f"http://{ip}:{PORT}{path}"
        q = qrcode.QRCode(border=2, error_correction=qrcode.constants.ERROR_CORRECT_M)
        q.add_data(url)
        q.make(fit=True)
        out = OUT_DIR / f"demo-{name}-qrcode.png"
        q.make_image().save(out)
        print(f"  [{label}] {out.name}  ->  {url}")
    print("完成。手机与电脑连同一个 WiFi，扫码即开。")


if __name__ == "__main__":
    main()
