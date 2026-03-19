#!/usr/bin/env python3
"""Konwerter SVG na PNG."""

import sys
import argparse
from pathlib import Path
from PIL import Image
import cairosvg


def parse_size(value: str) -> tuple[int, int]:
    """Parsuje rozmiar w formacie '192' lub '192x144'."""
    if "x" in value.lower():
        parts = value.lower().split("x")
        if len(parts) != 2:
            raise argparse.ArgumentTypeError(f"Nieprawidłowy rozmiar: {value}")
        return int(parts[0]), int(parts[1])
    size = int(value)
    return size, size


def apply_padding(image_path: Path, padding_percent: float) -> None:
    """Skaluje obraz w dół i umieszcza na przezroczystym tle tego samego rozmiaru."""
    img = Image.open(image_path).convert("RGBA")
    w, h = img.size

    pad_x = round(w * padding_percent / 100)
    pad_y = round(h * padding_percent / 100)

    inner_w = w - 2 * pad_x
    inner_h = h - 2 * pad_y

    img = img.resize((inner_w, inner_h), Image.LANCZOS)

    canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    canvas.paste(img, (pad_x, pad_y))
    canvas.save(image_path)


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
        raise FileNotFoundError(f"Plik nie istnieje: {input_path}")
    if input_path.suffix.lower() != ".svg":
        raise ValueError(f"Plik musi mieć rozszerzenie .svg: {input_path}")

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
        apply_padding(output_path, padding)

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Konwertuje plik SVG na PNG."
    )
    parser.add_argument("svg_file", help="Ścieżka do pliku SVG")
    parser.add_argument(
        "--scale",
        type=float,
        default=2.0,
        help="Współczynnik skalowania (domyślnie: 2.0)",
    )
    parser.add_argument(
        "--scales",
        type=float,
        nargs="+",
        metavar="SCALE",
        help="Lista skal, np. --scales 1 2 4",
    )
    parser.add_argument(
        "--sizes",
        type=parse_size,
        nargs="+",
        metavar="SIZE",
        help="Lista rozmiarów w px, np. --sizes 192 512 lub --sizes 192x192 512x512",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=300,
        help="Rozdzielczość w DPI (domyślnie: 300)",
    )
    parser.add_argument(
        "--padding",
        type=float,
        metavar="PERCENT",
        help="Padding jako %% rozmiaru obrazu, np. --padding 10 (dla ikon maskable)",
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
        print(f"Błąd: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
