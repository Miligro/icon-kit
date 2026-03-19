#!/usr/bin/env python3
"""SVG to PNG converter."""

import sys
import argparse
from pathlib import Path
from PIL import Image
import cairosvg


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


def convert_svg_to_png(
    svg_path: str,
    scale: float = None,
    dpi: int = 300,
    width: int = None,
    height: int = None,
    suffix: str = None,
    padding: float = None,
) -> Path:
    input_path = Path(svg_path).resolve()

    if not input_path.exists():
        raise FileNotFoundError(f"File not found: {input_path}")
    if input_path.suffix.lower() != ".svg":
        raise ValueError(f"File must have a .svg extension: {input_path}")

    if suffix:
        output_path = input_path.with_name(f"{input_path.stem}-{suffix}.png")
    elif scale is not None:
        output_path = input_path.with_name(f"{input_path.stem}@{scale}x.png")
    else:
        output_path = input_path.with_suffix(".png")

    cairosvg.svg2png(
        url=str(input_path),
        write_to=str(output_path),
        scale=scale,
        dpi=dpi,
        output_width=width,
        output_height=height,
        background_color=None,
    )

    if padding:
        img = Image.open(output_path).convert("RGBA")
        img = apply_padding(img, padding)
        img.save(output_path)

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Convert an SVG file to PNG."
    )
    parser.add_argument("svg_file", help="Path to the SVG file")
    parser.add_argument(
        "--scale",
        type=float,
        default=2.0,
        help="Scale factor (default: 2.0)",
    )
    parser.add_argument(
        "--scales",
        type=float,
        nargs="+",
        metavar="SCALE",
        help="Multiple scale factors, e.g. --scales 1 2 4",
    )
    parser.add_argument(
        "--sizes",
        type=parse_size,
        nargs="+",
        metavar="SIZE",
        help="Output sizes in px, e.g. --sizes 192 512 or --sizes 192x192 512x512",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=300,
        help="Resolution in DPI (default: 300)",
    )
    parser.add_argument(
        "--padding",
        type=float,
        metavar="PERCENT",
        help="Padding as %% of image size, e.g. --padding 10 (for maskable icons)",
    )
    args = parser.parse_args()

    try:
        if args.sizes:
            for w, h in args.sizes:
                suffix = f"{w}x{h}" if w != h else str(w)
                output = convert_svg_to_png(
                    args.svg_file, dpi=args.dpi, width=w, height=h,
                    suffix=suffix, padding=args.padding,
                )
                print(f"Zapisano: {output}")
        else:
            scales = args.scales if args.scales else [args.scale]
            for scale in scales:
                output = convert_svg_to_png(
                    args.svg_file, scale=scale, dpi=args.dpi, padding=args.padding,
                )
                print(f"Zapisano: {output}")
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
