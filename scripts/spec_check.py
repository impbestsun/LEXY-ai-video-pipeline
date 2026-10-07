#!/usr/bin/env python3
"""spec_check.py — 出片规格自动校验 (Gate6)

用法:
    python scripts/spec_check.py --input ./renders/ --width 768 --height 1344
    python scripts/spec_check.py --input ./renders/ --width 768 --height 1344 --min-frames 24

校验项:
    1. 分辨率必须等于 宽x高 (竖屏 9:16 交付规格)
    2. 文件必须为 png/jpg/jpeg/webp
    3. 黑边/留边检测: 四周 1% 区域若接近纯黑/纯白且占比过高 -> 警告
    4. (可选) 序列帧数量检查

退出码: 0 = 全部通过; 1 = 存在不通过项; 2 = 用法/环境错误
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    print("缺少依赖 Pillow, 请先: pip install -r requirements.txt", file=sys.stderr)
    raise SystemExit(2)

SUPPORTED = {".png", ".jpg", ".jpeg", ".webp"}


def iter_images(root: Path):
    for p in sorted(root.rglob("*")):
        if p.suffix.lower() in SUPPORTED and p.is_file():
            yield p


def edge_ratio(img: Image.Image, band: float = 0.01) -> float:
    """估算画面四周 band 比例区域内, 接近纯黑或纯白的像素占比 (黑边/留边检测)."""
    w, h = img.size
    bw, bh = max(1, int(w * band)), max(1, int(h * band))
    gray = img.convert("L")
    total = near = 0
    for box in (
        (0, 0, w, bh),            # 上
        (0, h - bh, w, h),        # 下
        (0, 0, bw, h),            # 左
        (w - bw, 0, w, h),        # 右
    ):
        crop = gray.crop(box)
        pixels = list(crop.getdata())
        total += len(pixels)
        near += sum(1 for v in pixels if v <= 8 or v >= 247)
    return near / total if total else 0.0


def main() -> int:
    ap = argparse.ArgumentParser(description="LEXY 出片规格校验")
    ap.add_argument("--input", required=True, help="待校验目录")
    ap.add_argument("--width", type=int, required=True)
    ap.add_argument("--height", type=int, required=True)
    ap.add_argument("--min-frames", type=int, default=0, help="序列帧最少数量, 0 表示不检查")
    ap.add_argument("--edge-threshold", type=float, default=0.95, help="边缘纯色占比阈值")
    args = ap.parse_args()

    root = Path(args.input)
    if not root.is_dir():
        print(f"[FAIL] 目录不存在: {root}", file=sys.stderr)
        return 2

    failures: list[str] = []
    warnings: list[str] = []
    count = 0
    for path in iter_images(root):
        count += 1
        try:
            with Image.open(path) as im:
                if im.size != (args.width, args.height):
                    failures.append(f"{path.name}: 分辨率 {im.size[0]}x{im.size[1]} != {args.width}x{args.height}")
                    continue
                r = edge_ratio(im)
                if r >= args.edge_threshold:
                    warnings.append(f"{path.name}: 边缘纯色占比 {r:.0%} (疑似黑边/留边)")
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{path.name}: 无法解析 ({exc})")

    if args.min_frames and count < args.min_frames:
        failures.append(f"序列帧数量 {count} < {args.min_frames}")

    print(f"共校验 {count} 个文件; 目标规格 {args.width}x{args.height}")
    for w in warnings:
        print(f"[WARN] {w}")
    for f in failures:
        print(f"[FAIL] {f}")
    if failures:
        print("结果: 不通过 —— 按 8-Gate SOP 回退对应 Gate 重做")
        return 1
    print("结果: 通过 (Gate6 规格校验 ✓)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
