# icon-kit

A set of CLI tools for working with icons — convert SVG to PNG, resize images, and generate multiple variants in one go. Useful for preparing PWA icons, maskable icons, and multi-resolution assets.

## Scripts

| Script           | Description                          |
|------------------|--------------------------------------|
| `svg_to_png.py`  | Convert an SVG file to PNG           |
| `png_convert.py` | Resize an existing PNG file          |

## Requirements

```bash
pip install -r requirements.txt
```

---

## svg_to_png.py

Converts an SVG file to PNG. Supports exporting multiple sizes at once and adding padding for maskable icons.

```bash
python3 svg_to_png.py <file.svg> [--scale SCALE] [--scales SCALE...] [--sizes SIZE...] [--dpi DPI] [--padding PERCENT]
```

### Arguments

| Argument    | Default | Description                                                                                          |
|-------------|---------|------------------------------------------------------------------------------------------------------|
| `file.svg`  | —       | Path to the SVG file                                                                                 |
| `--scale`   | `2.0`   | Scale factor                                                                                         |
| `--scales`  | —       | Multiple scale factors to generate several files at once                                             |
| `--sizes`   | —       | Output sizes in px — square (`192`) or rectangular (`192x144`)                                       |
| `--dpi`     | `300`   | Resolution in DPI                                                                                    |
| `--padding` | —       | Padding as a % of the image size — the icon is scaled down inside, the file keeps the requested size |

### Examples

```bash
# Basic conversion
python3 svg_to_png.py logo.svg

# Custom scale
python3 svg_to_png.py logo.svg --scale 4.0

# Multiple scales at once
python3 svg_to_png.py logo.svg --scales 1 2 4

# Specific pixel sizes (e.g. PWA icons)
python3 svg_to_png.py logo.svg --sizes 192 512

# Rectangular sizes
python3 svg_to_png.py logo.svg --sizes 192x192 512x512 144x96

# Maskable icons for PWA — icon fits within the inner 80%, file stays exactly 192/512px
python3 svg_to_png.py logo.svg --sizes 192 512 --padding 10

# Lower resolution (for previews)
python3 svg_to_png.py logo.svg --scale 1.0 --dpi 96
```

### Output filenames

| Mode       | Example filenames                                  |
|------------|----------------------------------------------------|
| `--scale`  | `logo@2.0x.png`                                    |
| `--scales` | `logo@1.0x.png`, `logo@2.0x.png`, `logo@4.0x.png` |
| `--sizes`  | `logo-192.png`, `logo-512.png`, `logo-144x96.png`  |

The output file is saved in the same folder as the input SVG.

---

## png_convert.py

Resizes an existing PNG file. Supports the same sizing and padding options as `svg_to_png.py`.

```bash
python3 png_convert.py <file.png> [--sizes SIZE...] [--scale SCALE] [--scales SCALE...] [--padding PERCENT]
```

### Arguments

| Argument    | Description                                                                                          |
|-------------|------------------------------------------------------------------------------------------------------|
| `file.png`  | Path to the PNG file                                                                                 |
| `--sizes`   | Output sizes in px, e.g. `--sizes 192 512` or `--sizes 192x144`                                     |
| `--scale`   | Scale factor relative to the original, e.g. `--scale 0.5`                                           |
| `--scales`  | Multiple scale factors, e.g. `--scales 0.5 1 2`                                                     |
| `--padding` | Padding as a % of the image size — the icon is scaled down inside, the file keeps the requested size |

### Examples

```bash
# Specific sizes
python3 png_convert.py icon.png --sizes 192 512

# Scale relative to original
python3 png_convert.py icon.png --scales 0.5 1 2

# Maskable icons for PWA
python3 png_convert.py icon.png --sizes 192 512 --padding 10
```

### Output filenames

| Mode       | Example filenames                                         |
|------------|-----------------------------------------------------------|
| `--sizes`  | `icon-192.png`, `icon-512.png`, `icon-144x96.png`         |
| `--scales` | `icon@0.5x.png`, `icon@1.0x.png`, `icon@2.0x.png`         |

The output file is saved in the same folder as the input PNG.

---

## License

MIT
