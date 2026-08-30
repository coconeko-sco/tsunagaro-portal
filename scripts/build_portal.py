import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "tsunagaro_data.json")
TEMPLATE_FILE = os.path.join(BASE_DIR, "templates", "index.html")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "index.html")
ROOT_INDEX_FILE = os.path.join(BASE_DIR, "index.html")


def build_featured_html(featured_items):
    if not featured_items:
        return ""

    featured = featured_items[0]
    region_names = " / ".join(item.get("region", "") for item in featured_items if item.get("region"))
    line_text = featured.get("line_caption") or "LINEから届いた最新情報をチェック。"
    title = featured.get("title", "地域のおすすめ")
    description = featured.get("description", "")
    image_url = featured.get("image_url", "")

    return f"""
        <article class="featured-card">
            <img src="{image_url}" alt="{title}">
            <div class="featured-body">
                <h1>{title}</h1>
                <p>{description}</p>
            </div>
        </article>
    """


def build_region_cards(regions):
    return ""


def build_line_posts(line_posts):
    html = ""
    for post in line_posts:
        html += f"""
            <article class="line-card">
                <img src="{post.get('image_url', '')}" alt="{post.get('caption', '')}">
                <div class="line-body">
                    <span class="line-tag">{post.get('label', '最新情報')}</span>
                    <p>{post.get('caption', '')}</p>
                </div>
            </article>
        """
    return html


def build_cards_html(cards, line_posts):
    html = ""
    for i, card in enumerate(cards):
        image_url = card.get("image_url", "")
        if not image_url:
            if i == 0:
                image_url = "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=600&auto=format&fit=crop&q=80"
            elif i == 1:
                image_url = "https://images.unsplash.com/photo-1533105079780-92b9be482077?w=600&auto=format&fit=crop&q=80"
            elif i == 2:
                image_url = "https://images.unsplash.com/photo-1526232761682-d26e03ac148e?w=600&auto=format&fit=crop&q=80"
            else:
                image_url = "https://images.unsplash.com/photo-1514933651103-005eec06c04b?w=600&auto=format&fit=crop&q=80"

        status_class = card.get("status", "open")
        if status_class == "active":
            status_class = "open"
        elif status_class == "preparation":
            status_class = "prep"
        elif status_class == "ended":
            status_class = "closed"

        html += f"""
            <article class="card">
                <img src="{image_url}" alt="{card['title']}" class="card-image">
                <div class="card-body">
                    <div class="card-header">
                        <span class="category-tag">{card['category']}</span>
                    </div>
                    <h3>{card['title']}</h3>
                    <p>{card['description']}</p>
                    <div class="card-footer">
                        <span>📍 {card['location']}</span>
                        <span>🕒 {card['date']}</span>
                    </div>
                </div>
            </article>
        """
    return html


def main():
    print("🚀 「つながろ」ポータルのビルドを開始します...")

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        html_template = f.read()

    featured_html = build_featured_html(data.get("featured", []))
    regions_html = build_region_cards(data.get("regions", []))
    line_posts_html = build_line_posts(data.get("line_posts", []))
    cards_html = build_cards_html(data.get("cards", []), data.get("line_posts", []))

    hot = data["hot_topics"]
    final_html = html_template.replace("{{FEATURED_HTML}}", featured_html)
    final_html = final_html.replace("{{REGIONS_HTML}}", regions_html)
    final_html = final_html.replace("{{LINE_POSTS_HTML}}", line_posts_html)
    final_html = final_html.replace("{{HOT_TITLE}}", hot.get("title", ""))
    final_html = final_html.replace("{{HOT_DESCRIPTION}}", hot["description"])
    final_html = final_html.replace("{{HOT_UPDATED}}", hot["updated_at"])
    final_html = final_html.replace("{{CARD_LIST_HTML}}", cards_html)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(final_html)
    with open(ROOT_INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(final_html)

    print(f"✨ ビルド成功！ポータルサイトが更新されました: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
