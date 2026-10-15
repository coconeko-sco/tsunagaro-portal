import json
import re
from pathlib import Path
from datetime import datetime, timezone, timedelta
from jinja2 import Environment, FileSystemLoader

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent.parent

env = Environment(loader=FileSystemLoader(str(ROOT / "templates")))

MASTER_JSON_PATH = ROOT / "data" / "stores_master.json"
OUTPUT_DIR = ROOT / "fukuoka"

JST = timezone(timedelta(hours=9))

def is_closed_day(closed_days, now_jst):
    if not closed_days:
        return False
    weekday_str = now_jst.strftime("%a")
    week_of_month = (now_jst.day - 1) // 7 + 1
    ordinal = {1: "1st", 2: "2nd", 3: "3rd", 4: "4th", 5: "5th"}.get(week_of_month, "")
    nth_weekday = f"{ordinal}_{weekday_str}"
    return (weekday_str in closed_days) or (nth_weekday in closed_days)

def evaluate_card_state(store, now_jst):
    """
    カードの階層（tier: 1〜5）と、表示するステータス（status, message, color）を自動計算する
    """
    # 1. 手動で階層が固定されている場合（例: tier: 5 のココネコ・ワヤジャー杯）
    fixed_tier = store.get("tier")
    if fixed_tier == 5:
        badge = store.get("badge") or store.get("category", "")
        return {
            "tier": 5,
            "status": badge,
            "message": "",
            "color": "#64748b",
            "is_custom_badge": False
        }

    # 2. イベントカードの場合（event_date があるもの）
    event_date_str = store.get("event_date")
    if event_date_str:
        today_str = now_jst.strftime("%Y-%m-%d")
        if today_str == event_date_str:
            return {"tier": 1, "status": "本日開催！", "message": "本日開催中です！", "color": "#e67e22", "is_custom_badge": True}
        elif today_str < event_date_str:
            return {"tier": 2, "status": "開催予定", "message": "", "color": "#3498db", "is_custom_badge": True}
        else:
            return {"tier": 4, "status": "開催終了", "message": "このイベントは終了しました", "color": "#7f8c8d", "is_custom_badge": True}

    # 3. 店舗カードの場合（営業時間・定休日・LINEボタン判定）
    closed_days = store.get("closed_days", [])
    hours_list = store.get("hours", [])
    current = store.get("current", {})
    action_key = current.get("action_key", "default")

    # (A) 定休日チェック
    if is_closed_day(closed_days, now_jst):
        return {"tier": 3, "status": "定休日", "message": "本日は定休日です", "color": "#7f8c8d", "is_custom_badge": True}

    # (B) 営業時間リストの解析（中休み・複数回営業対応）
    now_hm = now_jst.strftime("%H:%M")
    in_open_period = False
    next_open_hm = None
    first_open_hm = None
    last_close_hm = None

    for period in hours_list:
        if "-" not in period:
            continue
        start_hm, end_hm = [p.strip() for p in period.split("-", 1)]
        if first_open_hm is None:
            first_open_hm = start_hm
        last_close_hm = end_hm

        if start_hm <= now_hm < end_hm:
            in_open_period = True
            break
        elif now_hm < start_hm and next_open_hm is None:
            next_open_hm = start_hm

    # (C) LINEボタン（C：早じまい・本日終了）が押されている場合
    if action_key == "button_c" and current.get("status"):
        # オープン後〜閉店前の間に押された早じまいは当日中有効
        if not first_open_hm or now_hm >= first_open_hm:
            return {
                "tier": 3,
                "status": current.get("status", "本日終了"),
                "message": current.get("message", "本日の営業は終了しました"),
                "color": current.get("color", "#c0392b"),
                "is_custom_badge": True
            }

    # (D) 営業時間内の場合
    if in_open_period:
        # LINEのA・Bボタンが押されていればそのメッセージを優先表示！
        if action_key in ["button_a", "button_b"] and current.get("status"):
            return {
                "tier": 1,
                "status": current.get("status"),
                "message": current.get("message", ""),
                "color": current.get("color", "#27ae60"),
                "is_custom_badge": True
            }
        # ボタンが押されていなければ通常の「営業中」
        return {
            "tier": 1,
            "status": "営業中",
            "message": "",
            "color": "#27ae60",
            "is_custom_badge": True
        }

    # (E) 営業時間外（朝のオープン前 ／ 中休み・仕込み中 ／ 閉店後）の自動切り替え
    if hours_list:
        if first_open_hm and now_hm < first_open_hm:
            # 0:00 〜 朝のオープン前
            return {
                "tier": 3,
                "status": "準備中",
                "message": f"本日は {first_open_hm} より営業いたします",
                "color": "#7f8c8d",
                "is_custom_badge": True
            }
        elif next_open_hm:
            # 昼の部と夜の部の間（中休み・仕込み時間）
            return {
                "tier": 3,
                "status": "準備中",
                "message": f"只今仕込み中です（次は {next_open_hm} より営業）",
                "color": "#7f8c8d",
                "is_custom_badge": True
            }
        else:
            # すべての営業時間が終わった後（〜23:59）
            return {
                "tier": 3,
                "status": "本日終了",
                "message": "本日の営業は終了いたしました",
                "color": "#7f8c8d",
                "is_custom_badge": True
            }

    # 営業時間データがない一般カード
    cat = store.get("badge") or store.get("category", "")
    return {"tier": 3, "status": cat, "message": "", "color": "#64748b", "is_custom_badge": False}

def update_individual_page(city_key, store, state, now_jst):
    """
    リンク先がポータル配下のHTMLであり、かつ <!-- STATUS_START --> の目印があるページのみ更新する
    """
    href = store.get("href", "")
    # 1. 外部リンク（http〜）は何もしない
    if not href or href.startswith("http") or href.startswith("#"):
        return

    clean_href = href.lstrip("./")
    target_html_path = OUTPUT_DIR / city_key / clean_href
    if not target_html_path.exists() or not target_html_path.is_file():
        return

    content = target_html_path.read_text(encoding="utf-8")

    # 2. 目印（<!-- STATUS_START -->）がないページは1ミリも触らない
    pattern = re.compile(r"(<!--\s*STATUS_START\s*-->)(.*?)(<!--\s*STATUS_END\s*-->)", re.DOTALL)
    if not pattern.search(content):
        return

    status_text = state["status"] or "営業案内"
    status_color = state["color"] or "#7f8c8d"
    status_msg = state["message"] or store.get("date", "")
    formatted_msg = status_msg.replace("\n", "<br>")
    updated_str = now_jst.strftime("%H:%M")

    injected_html = f"""\\1
        <div class="status-card" id="statusCard" style="border-color: {status_color};">
            <div class="status-badge" id="statusBadge" style="background-color: {status_color};">{status_text}</div>
            <p class="status-message" id="statusMessage">{formatted_msg}</p>
            <div class="status-updated" id="statusUpdated">自動確認: {updated_str}</div>
        </div>
        \\3"""

    new_content = pattern.sub(injected_html, content)
    if new_content != content:
        target_html_path.write_text(new_content, encoding="utf-8")
        print(f"  └ 個別ページを更新しました: {target_html_path}")

def build_nav_menu_html(nav_list):
    if not nav_list:
        return ""
    return "\n".join([f'<a href="{item.get("url", "#")}">{item.get("title", "")}</a>' for item in nav_list])

def build_cards_html(cards_with_state):
    cards_html = []
    modals_html = []
    
    for card, state in cards_with_state:
        title = card.get('title') or card.get('name', '')
        desc = card.get('description', '')
        img_url = card.get('image_url', '')
        href = card.get('href', '')
        loc = card.get('location', '')
        date_str = card.get('date', '')
        password = card.get('password', '')

        status_text = state['status']
        status_msg = state['message']
        status_color = state['color']
        is_custom = state['is_custom_badge']

        if is_custom and status_text:
            badge_html = f'<span style="background: {status_color}; color: #ffffff; font-size: 0.75rem; padding: 3px 10px; border-radius: 4px; font-weight: bold; margin-bottom: 8px; display: inline-block;">{status_text}</span>'
        elif status_text:
            badge_html = f'<span style="background: #f1f5f9; color: #475569; font-size: 0.75rem; padding: 2px 8px; border-radius: 4px; font-weight: bold; margin-bottom: 8px; display: inline-block;">{status_text}</span>'
        else:
            badge_html = ''

        if status_msg:
            formatted_msg = status_msg.replace('\n', '<br>')
            status_box_html = f'''
            <div style="background: #f8fafc; border-left: 4px solid {status_color}; padding: 8px 12px; margin-bottom: 12px; border-radius: 0 4px 4px 0; font-size: 0.85rem; color: #334155; font-weight: bold;">
                {formatted_msg}
            </div>'''
        else:
            status_box_html = ''

        info_html = f'<p style="font-size: 0.85rem; color: #64748b; margin-bottom: 12px;">📍 {loc} | 🕒 {date_str}</p>' if (loc or date_str) else ''
        
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
            link_html = f'<a href="{href}" {target_attr} style="margin-top: auto; display: block; text-align: center; background: linear-gradient(135deg, #f97316, #ea580c); color: white; padding: 10px; border-radius: 6px; text-decoration: none; font-weight: bold; font-size: 0.85rem; box-shadow: 0 2px 4px rgba(249, 115, 22, 0.2);">詳細を見る</a>' if href else ''

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

    now_jst = datetime.now(JST)
    global_data = master_data.get("global", {})
    nav_menu_html = build_nav_menu_html(global_data.get("nav_menu", []))
    root_path = "../.."

    all_stores = master_data.get("stores", {})
    cities_data = master_data.get("cities", {})

    for city_key, city_meta in cities_data.items():
        out_file = OUTPUT_DIR / city_key / f"{city_key}.html"
        city_name = city_meta.get("city_name", city_key)
        hero_img = city_meta.get("hero_image", f"./images/{city_key}-hero.jpg")
        hero_desc = city_meta.get("hero_description", "")
        is_coming_soon = city_meta.get("status") == "coming_soon"

        city_cards_with_state = []
        for store_id, store_data in all_stores.items():
            if store_data.get("city") == city_key and store_data.get("publish", True):
                state = evaluate_card_state(store_data, now_jst)
                city_cards_with_state.append((store_data, state))
                # 個別ページに目印があれば同時更新
                update_individual_page(city_key, store_data, state, now_jst)

        # 5段階の階層（tier: 1〜5）の順番でソート
        city_cards_with_state.sort(key=lambda item: item[1]["tier"])

        cards_list_html = build_cards_html(city_cards_with_state) if city_cards_with_state else '<p>掲載店舗はまだありません。</p>'
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

        print(f"[{city_name}] ページを生成しました（現在時刻 {now_jst.strftime('%H:%M')} 基準・5段階ソート済） -> {out_file}")

if __name__ == "__main__":
    main()
