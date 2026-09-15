import json
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_FILE = os.path.join(BASE_DIR, "templates", "sity-page.html")

# 処理対象の地域リスト（今後直方などを増やす際もここに追加すれば自動生成されます）
CITIES = ["iizuka", "tagawa"]


def build_card_html(cards):
    cards_html = []
    for card in cards:
        href = card.get("href")
        
        # リンクがある場合はタイトルとボタンを<a>タグにする
        if href:
            is_external = href.startswith("http")
            target_attr = ' target="_blank" rel="noopener noreferrer"' if is_external else ''
            title_html = f'<h3><a href="{href}"{target_attr}>{card["title"]}</a></h3>'
            link_btn_html = f'<a href="{href}"{target_attr} class="card-link-btn">詳細を見る →</a>'
        else:
            title_html = f'<h3>{card["title"]}</h3>'
            link_btn_html = ''

        # バッジ（休業中など）の安全な判定
        badge = card.get("badge", "")
        badge_html = f'<span class="badge">{badge}</span>' if badge else ''

        # --- MEO情報（評価・口コミ数・マップリンク）の組み立て ---
        meo_html = ""
        rating = card.get("rating")
        map_url = card.get("map_url")
        reviews_count = card.get("reviews_count")

        if rating or map_url:
            rating_text = f"★ {rating}" if rating else ""
            reviews_text = f" ({reviews_count}件)" if reviews_count else ""
            
            map_btn_html = ""
            if map_url:
                map_btn_html = f'<a href="{map_url}" target="_blank" rel="noopener noreferrer" class="meo-map-btn">📍 Googleマップ</a>'

            meo_html = f"""
                    <div class="card-meo">
                        <span class="meo-rating">{rating_text}{reviews_text}</span>
                        {map_btn_html}
                    </div>"""

        card_html = f"""            <article class="card">
                <img src="{card['image_url']}" alt="{card['title']}" class="card-image">
                <div class="card-body">
                    <div class="card-tags">
                        <span class="category-tag">{card['category']}</span>
                        {badge_html}
                    </div>
                    {title_html}
                    <p>{card['description']}</p>
                    {meo_html}
                    <div class="card-footer">
                        <span>📍 {card['location']}</span>
                        <span>🕒 {card['date']}</span>
                        {link_btn_html}
                    </div>
                </div>
            </article>"""
        cards_html.append(card_html)
    return "\n".join(cards_html)


def build_city_page(city_key):
    data_file = os.path.join(BASE_DIR, "data", "fukuoka", f"{city_key}.json")
    output_dir = os.path.join(BASE_DIR, "fukuoka", city_key)
    output_file = os.path.join(output_dir, f"{city_key}.html")

    if not os.path.exists(data_file):
        print(f"スキップ: {data_file} が見つかりません")
        return

    with open(data_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        html = f.read()

    city_name = data["page_title"].removesuffix("のおすすめ")
    replacements = {
        "{{CITY_NAME}}": city_name,
        "{{HERO_IMAGE}}": data["hero_image"],
        "{{HERO_DESCRIPTION}}": data["hero_description"],
        "{{CARD_LIST_HTML}}": build_card_html(data["cards"]),
    }
    for placeholder, value in replacements.items():
        html = html.replace(placeholder, value)

    os.makedirs(output_dir, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[{city_name}] ページを生成しました -> {output_file}")


def main():
    for city in CITIES:
        build_city_page(city)


if __name__ == "__main__":
    main()
