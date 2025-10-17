import os
import zipfile
import rarfile
import py7zr
import shutil
import tempfile
from pathlib import Path
import argparse

# -------------------------
# Configuration
# -------------------------
DAZ_FOLDERS = ["data", "People", "Props", "Runtime", "Environments", "Scenes"]
PROMO_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".pdf", ".txt", ".doc", ".docx", ".rtf"}
ARCHIVE_EXTS = {".zip", ".rar", ".7z"} 

# -------------------------
# Archive Extraction Helpers
# -------------------------
def extract_archive(archive_path: Path, dest_dir: Path):
    """Extract a zip, rar, or 7z archive into dest_dir."""
    try:
        ext = archive_path.suffix.lower()
        if ext == ".zip":
            with zipfile.ZipFile(archive_path, 'r') as z:
                z.extractall(dest_dir)
        elif ext == ".rar":
            with rarfile.RarFile(archive_path, 'r') as r:
                r.extractall(dest_dir)
        elif ext == ".7z":
            with py7zr.SevenZipFile(archive_path, 'r') as z:
                z.extractall(dest_dir)
        else:
            print(f"⚠️ Skipping unsupported archive: {archive_path}")
            return
    except Exception as e:
        print(f"❌ Failed to extract {archive_path}: {e}")

def extract_all_archives_recursively(root: Path):
    """
    Recursively extract all supported archives under `root`, case-insensitively.
    Continues until no archives remain.
    """
    iteration = 0
    while True:
        archives = [p for p in root.rglob("*") if p.suffix.lower() in ARCHIVE_EXTS]
        if not archives:
            print(f"🔍 No more archives found after {iteration} passes.\n")
            break

        print(f"🔍 Pass {iteration}: Found {len(archives)} archives to extract.")
        for archive in archives:
            try:
                extract_to = archive.parent
                print(f"📦 Extracting nested archive: {archive}")
                extract_archive(archive, extract_to)
                archive.unlink(missing_ok=True)
            except Exception as e:
                print(f"⚠️ Failed to extract nested archive {archive}: {e}")

        iteration += 1

# -------------------------
# DAZ Root Finder
# -------------------------
def find_daz_root(root: Path) -> Path | None:
    """
    Detects the DAZ Studio content root in `root`.
    Works for cases where DAZ folders (Runtime, People, Data, etc.)
    are directly in `root` or nested multiple levels deep.
    """
    daz_folders = set(f.lower() for f in DAZ_FOLDERS)

    # --- Case 1: Root itself already contains DAZ folders
    top_level = {p.name.lower() for p in root.iterdir() if p.is_dir()}
    if daz_folders.intersection(top_level):
        return root

    # --- Case 2: Search deeper for nested content
    for path in root.rglob("*"):
        if not path.is_dir():
            continue
        subdirs = {p.name.lower() for p in path.iterdir() if p.is_dir()}
        if daz_folders.intersection(subdirs):
            # Return this directory (the one that directly contains DAZ folders)
            return path

    return None



# -------------------------
# Copy + Normalize
# -------------------------
def copy_daz_root(source_root: Path, output_dir: Path, include_promos: bool):
    """Copy the DAZ content from source_root to output_dir."""
    for item in source_root.iterdir():
        if not include_promos and item.suffix.lower() in PROMO_EXTS:
            continue
        dest = output_dir / item.name
        if item.is_dir():
            shutil.copytree(item, dest, dirs_exist_ok=True)
        else:
            shutil.copy2(item, dest)

# -------------------------
# Main Processing Logic
# -------------------------
def process_archive(archive_path: Path, output_dir: Path, include_promos: bool, keep_temp: bool, merge_into_content: bool):
    tempdir = Path(tempfile.mkdtemp())
    print(f"\n📦 Processing {archive_path.name}...")
    extract_archive(archive_path, tempdir)
    print(f"📂 Contents after first extraction: {[p.name for p in tempdir.iterdir()]}")
    extract_all_archives_recursively(tempdir)

    daz_root = find_daz_root(tempdir)
    if daz_root:
        print(f"🧭 Found DAZ root at: {daz_root}")
    else:
        print("🧭 No DAZ root detected.")

    if not daz_root:
        print(f"⚠️ No DAZ folder found in {archive_path.name}")
        if keep_temp:
            print(f"🧭 Keeping temp dir for inspection: {tempdir}")
        else:
            shutil.rmtree(tempdir, ignore_errors=True)
        return

    if merge_into_content:
        content_dir = output_dir / "Content"
        content_dir.mkdir(parents=True, exist_ok=True)
        copy_daz_root(daz_root, content_dir, include_promos)
        print(f"✅ Merged {archive_path.name} → {content_dir}")
    else:
        cleaned_dir = output_dir / (archive_path.stem + "_normalized")
        cleaned_dir.mkdir(parents=True, exist_ok=True)
        copy_daz_root(daz_root, cleaned_dir, include_promos)
        zip_path = shutil.make_archive(str(cleaned_dir), "zip", cleaned_dir)
        print(f"✅ Normalized: {archive_path.name} → {Path(zip_path).name}")

    if not keep_temp:
        shutil.rmtree(tempdir, ignore_errors=True)

    tempdir = Path(tempfile.mkdtemp())

    print(f"📦 Extracting {archive_path.name}...")
    extract_archive(archive_path, tempdir)
    extract_all_archives_recursively(tempdir)

    daz_root = find_daz_root(tempdir)

    # If still nothing found, walk all subfolders as last resort
    if not daz_root:
        for sub in tempdir.rglob("*"):
            if sub.is_dir():
                daz_root = find_daz_root(sub)
                if daz_root:
                    break

    if not daz_root:
        print(f"⚠️ No DAZ folder found in {archive_path.name}")
        if not keep_temp:
            shutil.rmtree(tempdir, ignore_errors=True)
        return

    if merge_into_content:
        content_dir = output_dir / "Content"
        content_dir.mkdir(parents=True, exist_ok=True)
        copy_daz_root(daz_root, content_dir, include_promos)
        print(f"✅ Merged {archive_path.name} → {content_dir}")
    else:
        cleaned_dir = output_dir / (archive_path.stem + "_normalized")
        cleaned_dir.mkdir(parents=True, exist_ok=True)
        copy_daz_root(daz_root, cleaned_dir, include_promos)
        zip_path = shutil.make_archive(str(cleaned_dir), "zip", cleaned_dir)
        print(f"✅ Normalized: {archive_path.name} → {Path(zip_path).name}")

    if not keep_temp:
        shutil.rmtree(tempdir, ignore_errors=True)

    tempdir = Path(tempfile.mkdtemp())

    print(f"📦 Extracting {archive_path.name}...")
    extract_archive(archive_path, tempdir)

    # Fully unpack all nested archives (repeat until none left)
    extract_all_archives_recursively(tempdir)

    # Now find the DAZ root
    daz_root = find_daz_root(tempdir)
    print(f"🧭 Detected DAZ root: {daz_root}" if daz_root else "🧭 No DAZ root detected.")

    if not daz_root:
        # Try again one level deeper, sometimes content is inside a single extracted folder
        subfolders = [f for f in tempdir.iterdir() if f.is_dir()]
        for sub in subfolders:
            daz_root = find_daz_root(sub)
            if daz_root:
                break

    if not daz_root:
        print(f"⚠️ No DAZ folder found in {archive_path.name}")
        if not keep_temp:
            shutil.rmtree(tempdir, ignore_errors=True)
        return

    if merge_into_content:
        # Merge all directly into output_dir/Content
        content_dir = output_dir / "Content"
        content_dir.mkdir(parents=True, exist_ok=True)
        copy_daz_root(daz_root, content_dir, include_promos)
        print(f"✅ Merged {archive_path.name} → {content_dir}")
    else:
        cleaned_dir = output_dir / (archive_path.stem + "_normalized")
        cleaned_dir.mkdir(parents=True, exist_ok=True)
        copy_daz_root(daz_root, cleaned_dir, include_promos)
        zip_path = shutil.make_archive(str(cleaned_dir), "zip", cleaned_dir)
        print(f"✅ Normalized: {archive_path.name} → {Path(zip_path).name}")

    if not keep_temp:
        shutil.rmtree(tempdir, ignore_errors=True)

# -------------------------
# CLI Entry Point
# -------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Normalize DAZ Studio asset archives into a consistent folder structure."
    )
    parser.add_argument(
        "input_dir",
        type=Path,
        help="Path to the directory containing .zip/.rar archives"
    )
    parser.add_argument(
        "output_dir",
        type=Path,
        help="Path to the directory where normalized archives will be saved or merged"
    )
    parser.add_argument(
        "--include-promos",
        action="store_true",
        help="Include promo images, PDFs, and documentation instead of skipping them"
    )
    parser.add_argument(
        "--keep-temp",
        action="store_true",
        help="Keep temporary extraction folders (for debugging)"
    )
    parser.add_argument(
        "--merge-into-content",
        action="store_true",
        help="Merge all normalized content into one 'Content' folder suitable for direct DAZ installation"
    )

    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    archives = [f for f in args.input_dir.iterdir() if f.is_file() and f.suffix.lower() in ARCHIVE_EXTS]

    if not archives:
        print("⚠️ No archives found in input directory.")
        return

    for archive in archives:
        process_archive(
            archive,
            args.output_dir,
            include_promos=args.include_promos,
            keep_temp=args.keep_temp,
            merge_into_content=args.merge_into_content
        )

    print("\n✅ All done!")

if __name__ == "__main__":
    main()
