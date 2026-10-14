import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
from jinja2 import Environment, FileSystemLoader

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent.parent

# Jinja2環境のセットアップ
env = Environment(loader=FileSystemLoader(str(ROOT / "templates")))

# 1つの統合マスターJSONファイルを読み込むパスと出力先の設定
MASTER_JSON_PATH = ROOT / "data" / "stores_master.json"
OUTPUT_DIR = ROOT / "fukuoka"

# 日本時間 (JST) の定義
JST = timezone(timedelta(hours=9))

def get_store_priority(store):
    """
    カードの並び順（優先度）を判定する関数
    数値が小さいほどページの上部に表示される（1: 最上位, 2: 通常, 3: 下位, 4: 最下層）
    """
    badge = store.get("badge", "")
    date_str = store.get("date", "")
    current = store.get("current", {})
    status = current.get("status", "")

    # 優先度4（最下層）：更新休止中・アーカイブ
    if "更新休止中" in badge or "アーカイブ" in date_str or "休業中" in store.get("title", ""):
        return 4

    # 優先度3（下位）：本日終了など、営業が終わっている状態
    if status in ["本日終了", "準備中", "定休日"]:
        return 3

    # 優先度1（最上位）：リアルタイムで「営業中」や「焼き上がり待ち」などアクティブな店舗
    if status in ["営業中", "焼き上がり待ち"] or (current and current.get("action_key") not in [None, "default"]):
        return 1

    # 優先度2（中位）：通常の店舗・これから開催されるイベント等
    return 2

def build_nav_menu_html(nav_list, root_path):
    """JSONの nav_menu 配列を <a> タグ群に変換"""
    if not nav_list:
        return ""
    links = []
    for item in nav_list:
        title = item.get("title", "")
        url = item.get("url", "#")
        links.append(f'<a href="{url}">{title}</a>')
    return "\n".join(links)

def build_cards_html(cards):
    """店舗やイベントのデータ配列を HTML カード群に変換（リアルタイムステータス＆モーダル対応版）"""
    cards_html = []
    modals_html = []
    
    for card in cards:
        title = card.get('title') or card.get('name', '')
        desc = card.get('description', '')
        img_url = card.get('image_url', '')
        href = card.get('href', '')
        loc = card.get('location', '')
        date_str = card.get('date', '')
        cat = card.get('badge') or card.get('category', '')
        password = card.get('password', '')

        # --- リアルタイム営業案内（current）の取得とHTML生成 ---
        current = card.get('current', {})
        status_text = current.get('status', '')
        status_msg = current.get('message', '')
        status_color = current.get('color', '#7f8c8d')

        # バッジ表示（currentのステータスがあればそちらを優先して色付きで目立たせる）
        if status_text:
            badge_html = f'<span style="background: {status_color}; color: #ffffff; font-size: 0.75rem; padding: 3px 10px; border-radius: 4px; font-weight: bold; margin-bottom: 8px; display: inline-block;">{status_text}</span>'
        elif cat:
            badge_html = f'<span style="background: #f1f5f9; color: #475569; font-size: 0.75rem; padding: 2px 8px; border-radius: 4px; font-weight: bold; margin-bottom: 8px; display: inline-block;">{cat}</span>'
        else:
            badge_html = ''

        # リアルタイムメッセージ枠（改行を<br>に変換してカード内に表示）
        if status_msg:
            formatted_msg = status_msg.replace('\n', '<br>')
            status_box_html = f'''
            <div style="background: #f8fafc; border-left: 4px solid {status_color}; padding: 8px 12px; margin-bottom: 12px; border-radius: 0 4px 4px 0; font-size: 0.85rem; color: #334155; font-weight: bold;">
                {formatted_msg}
            </div>'''
        else:
            status_box_html = ''

        info_html = f'<p style="font-size: 0.85rem; color: #64748b; margin-bottom: 12px;">📍 {loc} | 🕒 {date_str}</p>' if (loc or date_str) else ''
        
        # パスワード認証モーダル判定
        if password:
            card_id = "pwd_" + str(abs(hash(href)))
            link_html = f'''
                <button type="button" onclick="openModal('{card_id}_modal')" style="margin-top: auto; width: 100%; display: block; text-align: center; background: linear-gradient(135deg, #f97316, #ea580c); color: white; padding: 10px; border: none; border-radius: 6px; text-decoration: none; font-weight: bold; font-size: 0.85rem; cursor: pointer; box-shadow: 0 2px 4px rgba(249, 115, 22, 0.2);">特設ページを開く</button>
            '''
            
            modal_item = f'''
            <div id="{card_id}_modal" class="modal-overlay" hidden onclick="closeModalOnOverlay(event, '{card_id}_modal')">
                <div class="modal-content" style="max-width: 360px; text-align: center;">
                    <button type="button" class="modal-close" onclick="closeModal('{card_id}_modal')">&times;</button>
                    <h3 style="margin-bottom: 8px; font-size: 1.1rem;">🔒 パスワード認証</h3>
                    <p style="font-size: 0.85rem; color: #64748b; margin-bottom: 16px;">この先は関係者専用ページです。<br>合言葉を入力してください。</p>
                    <div style="display: flex; flex-direction: column; gap: 10px;">
                        <input type="password" id="{card_id}_input" placeholder="パスワードを入力" style="padding: 10px 12px; font-size: 0.9rem; border: 1px solid #cbd5e1; border-radius: 6px; outline: none; background: #f8fafc; width: 100%; box-sizing: border-box;">
                        <button type="button" onclick="
                            const pwd = document.getElementById('{card_id}_input').value;
                            if(pwd === '{password}') {{
                                window.location.href = '{href}?key=' + encodeURIComponent(pwd);
                            }} else {{
                                alert('パスワードが違います');
                            }}
                        " style="padding: 10px; background: linear-gradient(135deg, #f97316, #ea580c); color: white; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 0.9rem; box-shadow: 0 2px 4px rgba(249, 115, 22, 0.2);">認証して進む</button>
                    </div>
                </div>
            </div>
            '''
            modals_html.append(modal_item)
        else:
            target_attr = 'target="_blank" rel="noopener"' if href.startswith('http') else ''
            link_html = f'<a href="{href}" {target_attr} style="margin-top: auto; display: block; text-align: center; background: linear-gradient(135deg, #f97316, #ea580c); color: white; padding: 10px; border-radius: 6px; text-decoration: none; font-weight: bold; font-size: 0.85rem; box-shadow: 0 2px 4px rgba(249, 115, 22, 0.2);">詳細を見る</a>' if href else '<a href="#" style="margin-top: auto; display: block; text-align: center; background: #cbd5e1; color: white; padding: 10px; border-radius: 6px; text-decoration: none; font-weight: bold; font-size: 0.85rem;">詳細を見る</a>'

        card_item = f"""
            <article class="region-card" style="display: flex; flex-direction: column;">
                <img src="{img_url}" alt="{title}" class="card-img" onerror="this.style.display='none'">
                <div>{badge_html}</div>
                <h3>{title}</h3>
                <p>{desc}</p>
                {status_box_html}
                {info_html}
                {link_html}
            </article>"""
        cards_html.append(card_item)
        
    return "\n".join(cards_html) + "\n" + "\n".join(modals_html)

def main():
    if not MASTER_JSON_PATH.exists():
        print(f"エラー: マスターJSONが見つかりません -> {MASTER_JSON_PATH}")
        return

    with open(MASTER_JSON_PATH, "r", encoding="utf-8") as f:
        master_data = json.load(f)

    # 1. 共通ナビゲーションメニューを取得
    global_data = master_data.get("global", {})
    nav_list = global_data.get("nav_menu", [])
    root_path = "../.."
    nav_menu_html = build_nav_menu_html(nav_list, root_path)

    # 2. 全店舗データを取得
    all_stores = master_data.get("stores", {})

    # 3. 各都市（iizuka, tagawaなど）をループして一括ビルド
    cities_data = master_data.get("cities", {})
    for city_key, city_meta in cities_data.items():
        out_file = OUTPUT_DIR / city_key / f"{city_key}.html"

        city_name = city_meta.get("city_name", city_key)
        hero_img = city_meta.get("hero_image", f"./images/{city_key}-hero.jpg")
        hero_desc = city_meta.get("hero_description", "")
        is_coming_soon = city_meta.get("status") == "coming_soon"

        # 公開対象（publish: true）かつ該当都市のカードを抽出
        city_cards = [
            store_data for store_data in all_stores.values()
            if store_data.get("city") == city_key and store_data.get("publish", True)
        ]
        
        # ★優先順位（営業中＞通常＞終了＞休止中）で並び替え
        city_cards.sort(key=get_store_priority)
        
        cards_list_html = build_cards_html(city_cards) if city_cards else '<p>掲載店舗はまだありません。</p>'

        template = env.get_template('sity-page.html')

        html_content = template.render(
            CITY_ID=city_key,
            CITY_NAME=city_name,
            HERO_IMAGE=hero_img,
            HERO_DESCRIPTION=hero_desc,
            CARD_LIST_HTML=cards_list_html,
            NAV_MENU_HTML=nav_menu_html,
            root_path=root_path,
            is_coming_soon=is_coming_soon
        )

        out_file.parent.mkdir(parents=True, exist_ok=True)
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"[{city_name}] ページを生成しました（優先度ソート済） -> {out_file}")

if __name__ == "__main__":
    main()
