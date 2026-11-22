import json, re, shutil, unicodedata
from pathlib import Path
from PIL import Image, ImageOps

BASE = Path("/home/toku/Desktop/tsunagaro/fukuoka/iizuka/4mini-kahoterasu")
IMG_ROOT = BASE / "images"
RAW_BACKUP = Path("/home/toku/Desktop/4mini_raw_done")
HTML_FILE = BASE / "gallery2026.html"
CATS = ["entry", "other"]
EXTS = {".jpg", ".jpeg", ".png", ".webp"}

file_lists = {}
for cat in CATS:
    cat_dir = IMG_ROOT / cat
    thumb_dir = cat_dir / "thumb"
    full_dir = cat_dir / "full"
    bak_dir = RAW_BACKUP / cat
    for d in (cat_dir, thumb_dir, full_dir, bak_dir):
        d.mkdir(parents=True, exist_ok=True)

    existing_200 = sorted([int(f.stem) for f in full_dir.glob("*.jpg") if f.stem.isdigit() and int(f.stem) >= 200])
    next_num = existing_200[-1] + 1 if existing_200 else 201

    new_files = sorted(
        [f for f in cat_dir.iterdir() if f.is_file() and f.suffix.lower() in EXTS],
        key=lambda x: x.stat().st_mtime
    )

    for src in new_files:
        norm_stem = unicodedata.normalize("NFKC", src.stem)
        if norm_stem.isdigit():
            stem = f"{int(norm_stem):03d}"
        elif re.match(r"^[A-Za-z]+\d+$", norm_stem) and not norm_stem.upper().startswith(("IMG", "DSC", "PXL", "F")):
            stem = norm_stem.upper()
        else:
            stem = f"{next_num:03d}"
            next_num += 1

        name = f"{stem}.jpg"
        print(f"処理中: {cat}/{name} <- {src.name}", flush=True)
        with Image.open(src) as im:
            im = ImageOps.exif_transpose(im).convert("RGB")
            full_im = im.copy()
            full_im.thumbnail((1400, 1400), Image.Resampling.LANCZOS)
            full_im.save(full_dir / name, "JPEG", quality=78, optimize=True)
            thumb_im = im.copy()
            thumb_im.thumbnail((500, 500), Image.Resampling.LANCZOS)
            thumb_im.save(thumb_dir / name, "JPEG", quality=75, optimize=True)

        shutil.move(str(src), str(bak_dir / f"{stem}_{src.name}"))

    all_names = sorted([f.name for f in full_dir.glob("*.jpg")])
    file_lists[cat] = all_names
    print(f"[{cat}] 新規 {len(new_files)} 枚を処理 → 合計 {len(all_names)} 枚")

html = HTML_FILE.read_text(encoding="utf-8")
html = re.sub(
    r"const PHOTO_FILES = \{[\s\S]*?\};",
    f"const PHOTO_FILES = {json.dumps(file_lists, ensure_ascii=False)};",
    html
)
HTML_FILE.write_text(html, encoding="utf-8")
print("gallery2026.html 更新完了！")
