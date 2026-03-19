#!/usr/bin/env python3
"""PNG resizer."""

import sys
import argparse
from pathlib import Path
from PIL import Image


def parse_size(value: str) -> tuple[int, int]:
    """Parse size in '192' or '192x144' format."""
    if "x" in value.lower():
        parts = value.lower().split("x")
        if len(parts) != 2:
            raise argparse.ArgumentTypeError(f"Nieprawidłowy rozmiar: {value}")
        return int(parts[0]), int(parts[1])
    size = int(value)
    return size, size


def apply_padding(img: Image.Image, padding_percent: float) -> Image.Image:
    """Scale image down and place it on a transparent canvas of the same size."""
    w, h = img.size
    pad_x = round(w * padding_percent / 100)
    pad_y = round(h * padding_percent / 100)

    inner = img.resize((w - 2 * pad_x, h - 2 * pad_y), Image.LANCZOS)
    canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    canvas.paste(inner, (pad_x, pad_y))
    return canvas


def process(
    input_path: Path,
    width: int,
    height: int,
    suffix: str,
    padding: float = None,
) -> Path:
    img = Image.open(input_path).convert("RGBA")
    img = img.resize((width, height), Image.LANCZOS)

    if padding:
        img = apply_padding(img, padding)

    output_path = input_path.with_name(f"{input_path.stem}{suffix}.png")
    img.save(output_path)
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Resize a PNG file."
    )
    parser.add_argument("png_file", help="Path to the PNG file")
    parser.add_argument(
        "--sizes",
        type=parse_size,
        nargs="+",
        metavar="SIZE",
        help="Output sizes in px, e.g. --sizes 192 512 or --sizes 192x144",
    )
    parser.add_argument(
        "--scale",
        type=float,
        help="Scale factor relative to original, e.g. --scale 0.5",
    )
    parser.add_argument(
        "--scales",
        type=float,
        nargs="+",
        metavar="SCALE",
        help="Multiple scale factors, e.g. --scales 0.5 1 2",
    )
    parser.add_argument(
        "--padding",
        type=float,
        metavar="PERCENT",
        help="Padding as %% of image size; file keeps the requested size",
    )
    args = parser.parse_args()

    if not args.sizes and not args.scale and not args.scales:
        parser.error("Provide --sizes, --scale, or --scales.")

    input_path = Path(args.png_file).resolve()

    if not input_path.exists():
        print(f"Error: File not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    if input_path.suffix.lower() != ".png":
        print(f"Error: File must have a .png extension: {input_path}", file=sys.stderr)
        sys.exit(1)

    try:
        if args.sizes:
            for w, h in args.sizes:
                suffix = f"-{w}x{h}" if w != h else f"-{w}"
                output = process(input_path, w, h, suffix, args.padding)
                print(f"Zapisano: {output}")
        else:
            orig = Image.open(input_path)
            orig_w, orig_h = orig.size
            scales = args.scales if args.scales else [args.scale]
            for scale in scales:
                w = round(orig_w * scale)
                h = round(orig_h * scale)
                suffix = f"@{scale}x"
                output = process(input_path, w, h, suffix, args.padding)
                print(f"Zapisano: {output}")
    except (FileNotFoundError, ValueError, OSError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
