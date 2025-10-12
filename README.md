# 🧰 DAZ Archive Normalizer

**DAZ Archive Normalizer** is a Python utility that automatically extracts and restructures `.zip` and `.rar` archives containing DAZ Studio assets into a clean, standardized DAZ content folder layout.

It fixes the common problems with DAZ assets downloaded from various sources, such as:
- inconsistent folder hierarchies (`Runtime`, `People`, `Data` buried several levels deep);
- multiple nested archives inside one product archive;
- unwanted promo images and documentation clutter.

After processing, each archive becomes a properly organized DAZ Studio content folder:
```
Content/
├── Data/
├── People/
├── Runtime/
└── Props/
```

You can also merge everything directly into a single **Content** folder ready to add to your DAZ Studio library.

---

## ⚙️ Features

✅ **Recursive extraction** — automatically unpacks nested `.zip` and `.rar` archives.  
✅ **Automatic DAZ root detection** — finds where the main DAZ folders start, even if deeply nested.  
✅ **Merge mode** — combine all assets into one DAZ library folder.  
✅ **Promo filtering** — skips images and text files unless requested.  
✅ **Cross-platform** — works on macOS, Windows, and Linux (requires `unrar` for `.rar`).

---

## 🖥️ Requirements

- Python 3.9 or newer  
- `rarfile` module (and `unrar` or `bsdtar` installed system-wide)

### Install dependencies
```bash
pip install rarfile
```

If `.rar` extraction fails, install the `unrar` tool:

**macOS (Homebrew):**
```bash
brew install unrar
```

**Windows (Chocolatey):**
```bash
choco install unrar
```

---

## 🚀 Usage

### Basic syntax
```bash
python normalize_daz.py <input_dir> <output_dir> [options]
```

| Argument | Description |
|-----------|--------------|
| `input_dir` | Folder containing the `.zip`/`.rar` files |
| `output_dir` | Folder where normalized archives or merged content will be placed |

### Options

| Flag | Description |
|------|--------------|
| `--include-promos` | Keep promo images, PDFs, and documentation |
| `--keep-temp` | Keep temporary extraction folders (for debugging) |
| `--merge-into-content` | Merge everything into one `Content/` folder |

---

## 🧩 Examples

### 1️⃣ Normalize each archive individually
Creates new `.zip` files with cleaned folder structure.
```bash
python normalize_daz.py "Downloads/DAZ_Assets" "Normalized"
```

### 2️⃣ Merge all assets into one DAZ library
Perfect for direct import into DAZ Studio.
```bash
python normalize_daz.py "Downloads/DAZ_Assets" "DAZ_Merged" --merge-into-content
```

Result:
```
DAZ_Merged/
└── Content/
    ├── Data/
    ├── People/
    ├── Runtime/
    └── Props/
```

### 3️⃣ Keep promotional files
```bash
python normalize_daz.py "DAZ/" "Normalized/" --include-promos
```

### 4️⃣ Debug mode (inspect temp folders)
```bash
python normalize_daz.py "DAZ/" "Normalized/" --keep-temp
```
The script prints the path to the temporary directory for manual inspection.

---

## 🧠 How It Works

1. **Extraction phase**  
   - Each archive is unpacked into a temporary folder.  
   - All nested `.zip`/`.rar` files inside are extracted recursively.

2. **Root detection phase**  
   - The script scans for key DAZ folders (`Runtime`, `People`, `Data`, etc.).  
   - It automatically identifies the correct folder level (even if deeply nested).

3. **Copy / merge phase**  
   - DAZ folders are copied into a clean structure.  
   - Promotional files are skipped unless `--include-promos` is set.  
   - Optionally merges everything into one unified `Content/` directory.

---

## 🧾 Example

### Input (example product)

```
Example_Product.zip
 ├── Example_Product_Main.ZIP
 └── Example_Product_Templates.ZIP
```

Inside the main `.ZIP` there is the DAZ structure:

```
Data/
People/
Runtime/
Documentation/
```

### Output (merged)

```
Content/
├── Data/
├── People/
└── Runtime/
```

---

## 🧰 Troubleshooting

### ⚠️ “No DAZ folder found”
- Run again with `--keep-temp`.
- Open the printed temp directory path.
- If the DAZ folders are one level deeper (e.g., `Product/Content/Runtime`), move that folder manually or adjust your extraction.

### ⚠️ “Failed to extract .rar”
Make sure `unrar` or `bsdtar` is installed and accessible on your system.

### 💡 About “Templates” archives
Some products include separate archives for UV or OBJ templates (usually with “Templates” in the name).  
These are optional and not required for installation in DAZ Studio.

---

## 🧹 Notes

- Temporary folders are created automatically in your system’s temp directory.  
- They are deleted after processing unless `--keep-temp` is used.  
- Copying is non-destructive: existing files in the output are merged, not overwritten.

---

## 🧑‍💻 Author

Developed by **Lossmeril**, 2025  
For artists and collectors who want a consistent, organized DAZ Studio content library.
