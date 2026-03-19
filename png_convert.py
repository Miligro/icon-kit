#!/usr/bin/env python3
"""Konwerter PNG — zmiana rozmiaru i padding."""

import sys
import argparse
from pathlib import Path
from PIL import Image


def parse_size(value: str) -> tuple[int, int]:
    """Parsuje rozmiar w formacie '192' lub '192x144'."""
    if "x" in value.lower():
        parts = value.lower().split("x")
        if len(parts) != 2:
            raise argparse.ArgumentTypeError(f"Nieprawidłowy rozmiar: {value}")
        return int(parts[0]), int(parts[1])
    size = int(value)
    return size, size


def apply_padding(img: Image.Image, padding_percent: float) -> Image.Image:
    """Skaluje obraz w dół i umieszcza na przezroczystym tle tego samego rozmiaru."""
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

    output_path = input_path.with_name(f"{input_path.stem}-{suffix}.png")
    img.save(output_path)
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Zmienia rozmiar pliku PNG."
    )
    parser.add_argument("png_file", help="Ścieżka do pliku PNG")
    parser.add_argument(
        "--sizes",
        type=parse_size,
        nargs="+",
        metavar="SIZE",
        help="Lista rozmiarów w px, np. --sizes 192 512 lub --sizes 192x144",
    )
    parser.add_argument(
        "--scale",
        type=float,
        help="Współczynnik skalowania względem oryginału, np. --scale 0.5",
    )
    parser.add_argument(
        "--scales",
        type=float,
        nargs="+",
        metavar="SCALE",
        help="Lista współczynników skalowania, np. --scales 0.5 1 2",
    )
    parser.add_argument(
        "--padding",
        type=float,
        metavar="PERCENT",
        help="Padding jako %% rozmiaru obrazu (obraz zachowuje podany rozmiar)",
    )
    args = parser.parse_args()

    if not args.sizes and not args.scale and not args.scales:
        parser.error("Podaj --sizes, --scale lub --scales.")

    input_path = Path(args.png_file).resolve()

    if not input_path.exists():
        print(f"Błąd: Plik nie istnieje: {input_path}", file=sys.stderr)
        sys.exit(1)
    if input_path.suffix.lower() != ".png":
        print(f"Błąd: Plik musi mieć rozszerzenie .png: {input_path}", file=sys.stderr)
        sys.exit(1)

    try:
        if args.sizes:
            for w, h in args.sizes:
                suffix = f"{w}x{h}" if w != h else str(w)
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
    except Exception as e:
        print(f"Błąd: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
