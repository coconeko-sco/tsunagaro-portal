import re, shutil
from pathlib import Path
from PIL import Image, ImageOps

BASE = Path("/home/toku/Desktop/tsunagaro/fukuoka/iizuka/4mini-kahoterasu")
IMG_ROOT = BASE / "images"
RAW_BACKUP = Path("/home/toku/Desktop/4mini_raw_done")
HTML_FILE = BASE / "gallery2026.html"
CATS = ["entry", "staff", "other"]
EXTS = {".jpg", ".jpeg", ".png", ".webp"}

counts = {}
for cat in CATS:
    cat_dir = IMG_ROOT / cat
    thumb_dir = cat_dir / "thumb"
    full_dir = cat_dir / "full"
    bak_dir = RAW_BACKUP / cat
    for d in (cat_dir, thumb_dir, full_dir, bak_dir):
        d.mkdir(parents=True, exist_ok=True)

    # 既存の連番の最大値を取得（追加時に番号がズレないようにする）
    existing = sorted([int(f.stem) for f in full_dir.glob("*.jpg") if f.stem.isdigit()])
    next_num = existing[-1] + 1 if existing else 1

    # フォルダ直下にある未処理の新規写真を取得
    new_files = sorted(
        [f for f in cat_dir.iterdir() if f.is_file() and f.suffix.lower() in EXTS],
        key=lambda x: x.stat().st_mtime
    )

    for src in new_files:
        name = f"{next_num:03d}.jpg"
        with Image.open(src) as im:
            im = ImageOps.exif_transpose(im).convert("RGB")
            # 1) ダウンロード用（高画質・長辺1800px）
            full_im = im.copy()
            full_im.thumbnail((1800, 1800), Image.Resampling.LANCZOS)
            full_im.save(full_dir / name, "JPEG", quality=85, optimize=True)
            # 2) 一覧表示用（超軽量サムネイル・長辺500px）
            thumb_im = im.copy()
            thumb_im.thumbnail((500, 500), Image.Resampling.LANCZOS)
            thumb_im.save(thumb_dir / name, "JPEG", quality=75, optimize=True)
        # 処理済みの元画像はデスクトップのバックアップフォルダへ退避（Gitが重くなるのを防ぐ）
        shutil.move(str(src), str(bak_dir / f"{next_num:03d}_{src.name}"))
        next_num += 1

    total = len(list(full_dir.glob("*.jpg")))
    counts[cat] = total
    print(f"[{cat}] 新規 {len(new_files)} 枚を処理 → 合計 {total} 枚")

html = HTML_FILE.read_text(encoding="utf-8")
for cat, cnt in counts.items():
    html = re.sub(rf"({cat}:\s*)\d+", rf"\g<1>{cnt}", html)
HTML_FILE.write_text(html, encoding="utf-8")
print("gallery2026.html 更新完了！")
