import json
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "fukuoka-iizuka.json")
TEMPLATE_FILE = os.path.join(BASE_DIR, "templates", "sity-page.html")
OUTPUT_DIR = os.path.join(BASE_DIR, "fukuoka", "iizuka")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "iizuka.html")


def build_card_html(cards):
    cards_html = []
    for card in cards:
        card_html = f"""            <article class=\"card\">
                <img src=\"{card['image_url']}\" alt=\"{card['title']}\" class=\"card-image\">
                <div class=\"card-body\">
                    <span class=\"category-tag\">{card['category']}</span>
                    <h3>{card['title']}</h3>
                    <p>{card['description']}</p>
                    <div class=\"card-footer\">
                        <span>📍 {card['location']}</span>
                        <span>🕒 {card['date']}</span>
                    </div>
                </div>
            </article>"""
        if card.get("href"):
            card_html = f'<a class="card-link" href="{card["href"]}">\n{card_html}\n            </a>'
        cards_html.append(card_html)
    return "\n".join(cards_html)


def main():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
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

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    print("飯塚ページを更新しました")


if __name__ == "__main__":
    main()
